from kafka import KafkaConsumer, KafkaProducer
from kafka.errors import CommitFailedError
from kafka import TopicPartition, ConsumerRebalanceListener
from json import loads
import init
import json
import requests
import logging
import traceback
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

logging.basicConfig(level=logging.INFO)

# Token estimation constants
CHARS_PER_TOKEN_VI = 4  # Vietnamese text: ~4 chars per token
MAX_TOKENS = 15000  # Safety margin for context window
MAX_CHARS = MAX_TOKENS * CHARS_PER_TOKEN_VI
MAX_WORKERS = 4  # Number of parallel workers for multi-doc processing


class TestRebalanceListener(ConsumerRebalanceListener):
    def __init__(self, consumer: KafkaConsumer, error_partition: TopicPartition, error_offset: int):
        self.consumer = consumer
        self.error_partition = error_partition
        self.error_offset = error_offset

    def on_partitions_revoked(self, revoked):
        pass

    def on_partitions_assigned(self, assigned):
        if len(assigned) > 0 and self.error_partition is not None:
            for partition in assigned:
                if self.error_partition == partition:
                    current_offset = self.error_offset + 1
                else:
                    current_offset = self.consumer.position(partition)
                self.consumer.seek(partition, current_offset)


def estimate_token_count(text: str) -> int:
    """Estimate token count for Vietnamese text"""
    return len(text) // CHARS_PER_TOKEN_VI


def normalize_whitespace(text: str) -> str:
    """
    Normalize excessive whitespace in text
    - Remove empty lines (no blank lines)
    - Keep line breaks between sentences
    - Remove trailing/leading whitespace from each line
    - Replace multiple spaces with single space
    """
    import re

    # Remove trailing/leading whitespace from each line and filter out empty lines
    lines = [line.strip() for line in text.split('\n') if line.strip()]

    # Join with newline to keep line structure
    text = '\n'.join(lines)

    # Replace multiple spaces with single space
    text = re.sub(r' {2,}', ' ', text)

    # Final trim
    return text.strip()


def chunk_text_by_tokens(text: str, max_tokens: int = MAX_TOKENS) -> list:
    """
    Chia văn bản thành các chunks dựa trên paragraph (đoạn văn)
    Mỗi chunk chứa nhiều đoạn văn nhưng không vượt quá max_tokens
    """
    # Chia theo paragraph: dựa vào dấu xuống dòng kép hoặc xuống dòng đơn
    paragraphs = []

    # Thử chia theo dấu xuống dòng kép trước
    temp_paragraphs = text.split('\n\n')

    # Nếu không có xuống dòng kép, chia theo xuống dòng đơn
    if len(temp_paragraphs) == 1:
        temp_paragraphs = text.split('\n')

    # Loại bỏ các đoạn rỗng và strip whitespace
    for para in temp_paragraphs:
        para = para.strip()
        if para:
            paragraphs.append(para)

    # Nếu không có paragraph nào (văn bản liền khối), fallback về sentence-based
    if len(paragraphs) <= 1:
        import nltk
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt', quiet=True)
        sentences = nltk.sent_tokenize(text)
        paragraphs = sentences

    # Group paragraphs vào chunks
    chunks = []
    current_chunk = []
    current_length = 0
    max_chars = max_tokens * CHARS_PER_TOKEN_VI

    for para in paragraphs:
        para_length = len(para)

        # Nếu thêm đoạn này vào sẽ vượt quá limit
        if current_length + para_length > max_chars and current_chunk:
            # Lưu chunk hiện tại
            chunks.append("\n\n".join(current_chunk))
            current_chunk = [para]
            current_length = para_length
        else:
            # Thêm đoạn vào chunk hiện tại
            current_chunk.append(para)
            current_length += para_length

    # Thêm chunk cuối cùng
    if current_chunk:
        chunks.append("\n\n".join(current_chunk))

    return chunks


def call_ollama_summary_single(text: str, percent: float, ollama_url: str, model: str = "mistral", is_multi: bool = False) -> str:
    """Call Ollama API for single chunk summarization"""
    try:
        import nltk
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt', quiet=True)

        sentences = nltk.sent_tokenize(text)
        num_sentences = max(3, int(len(sentences) * percent))

        logging.info(f"Calling Ollama with model {model} to summarize {len(sentences)} sentences to {num_sentences}")

        # Call Ollama API
        response = requests.post(
            f"{ollama_url}/api/generate",
            json={
                "model": model,
                "prompt": f"Hãy đọc và hiểu văn bản sau, sau đó viết lại thành bản tóm tắt tóm lược (abstractive summary) bằng tiếng Việt với khoảng {num_sentences} câu. DIỄN GIẢI LẠI nội dung bằng cách hiểu của bạn, đừng chỉ sao chép câu gốc. Trả về nội dung súc tích, rõ ràng, không thêm XML, tag hay giải thích:\n\n{text}",
                "stream": False,
                "think": False,
                "options": {
                    "temperature": 0.3,
                    "top_p": 0.9,
                    "num_ctx": 8192 if is_multi else 4096
                }
            },
            timeout=600
        )

        if response.status_code == 200:
            result = response.json()
            summary = result.get("response", "").strip()

            # Remove any XML-like tags from the response
            import re
            summary = re.sub(r'<think>.*?</think>', '', summary, flags=re.DOTALL)
            summary = re.sub(r'<[^>]+>', '', summary)
            summary = summary.strip()

            # Normalize excessive whitespace (fix multiple newlines)
            summary = normalize_whitespace(summary)

            logging.info(f"Ollama summarization successful, length: {len(summary)}")
            return summary
        else:
            logging.error(f"Ollama API error: {response.status_code} - {response.text}")
            # Fallback: return first sentences
            return " ".join(sentences[:num_sentences])

    except Exception as e:
        logging.error(f"Multi-doc Ollama summarization failed: {e}")
        traceback.print_exc()
        # Fallback
        try:
            import nltk
            combined_text = "\n\n".join(documents)
            sentences = nltk.sent_tokenize(combined_text)
            num_sentences = max(3, int(len(sentences) * percent))
            return " ".join(sentences[:num_sentences])
        except:
            return "\n\n".join(documents)[:1000]


def main():
    logging.info("Starting Multi-Document Ollama summarization service...")

    consumer = KafkaConsumer(
        bootstrap_servers=init.configs["bootstrap_servers"],
        auto_offset_reset='earliest',  # Changed to 'earliest' to process old messages
        enable_auto_commit=False,
        max_poll_records=1,  # Process 1 message at a time for long-running multi-doc tasks
        max_poll_interval_ms=1800000,  # 30 minutes for parallel chunked processing
        session_timeout_ms=300000,  # 5 minutes session timeout
        heartbeat_interval_ms=30000,  # 30 seconds heartbeat
        group_id="30_multi_ollama_v3",  # Changed group_id to reset offset and read from beginning
        value_deserializer=lambda x: loads(x.decode('utf-8')))

    topic = "30_multi_ollama"
    consumer.subscribe([topic], listener=TestRebalanceListener(consumer, None, 0))
    logging.info(f"Subscribed to topic: {topic}")

    producer = KafkaProducer(
        bootstrap_servers=init.configs["bootstrap_servers"],
        max_request_size=100000000,
        value_serializer=lambda x: json.dumps(x).encode('utf-8'))

    ollama_url = init.configs.get("ollama_url", "http://ollama:11434")
    ollama_model = init.configs.get("ollama_model", "mistral")
    logging.info(f"Using Ollama at {ollama_url} with model {ollama_model}")

    for data in consumer:
        try:
            message = data.value
            current_partition = data.partition
            current_offset = data.offset

            url_status = init.configs["url_status_Web"]
            sum_id = message["sumary_id"]
            logging.info(f"Processing multi-doc message with sumary_id: {sum_id}")

            # Check status (skip if API unavailable for testing)
            skip_message = False
            try:
                res = requests.get(f"{url_status}/{sum_id}", timeout=5)
                res = json.loads(res.content)
                if not res.get("data", {}).get("status", True):
                    logging.info(f"Skipping sumary_id {sum_id} - status is false")
                    skip_message = True
            except Exception as e:
                logging.warning(f"Failed to check status for {sum_id}: {e}")
                logging.info(f"Continuing anyway (status API might be unavailable)")

            if skip_message:
                consumer.commit()
                continue

            output_format = {
                "user_id": message["user_id"],
                "sumary_id": message["sumary_id"],
                "original_doc_ids": message["original_doc_ids"],
                "is_single": False,
                "is_topic": message["is_topic"],
                "result": {"cluster": [], "topic": []}
            }

            try:
                per = message.get("cluster", {}).get("percent_output") or \
                      message.get("percent_output") or 0.1
            except:
                per = 0.1

            # Update status to processing
            try:
                requests.post(f"{url_status}", json={
                    "inMultiDocSumId": sum_id,
                    "inStatusId": 1
                })
                logging.info(f"Updated status to processing for {sum_id}")
            except Exception as e:
                logging.warning(f"Failed to update status: {e}")

            try:
                # Handle cluster mode
                if message.get("is_cluster", False):
                    logging.info("Processing in CLUSTER mode")

                    # Call clustering API if needed
                    cluster_data = message.get("cluster", {})
                    list_docs = cluster_data.get("list_doc", [])
                    list_doc_ids = cluster_data.get("list_doc_id", [])
                    algo_id = cluster_data.get("algo_id", "33")

                    # Call clustering service
                    try:
                        tic = time.time()
                        res = requests.post(
                            init.configs["url_cluster"],
                            json={"list_doc": list_docs},
                            timeout=60
                        )
                        tac = time.time()
                        logging.info(f"Clustering took {tac - tic:.2f}s")

                        if res.status_code != 200:
                            logging.error("Clustering API failed, sending empty result")
                            producer.send("result_ai", output_format)
                            consumer.commit()
                            continue

                        list_cluster = json.loads(res.content)["clusters"]
                    except Exception as e:
                        logging.error(f"Clustering failed: {e}")
                        producer.send("result_ai", output_format)
                        consumer.commit()
                        continue

                    # Summarize each cluster
                    for idx, cluster in enumerate(list_cluster):
                        obj = {
                            "text": "summary",
                            "displayName": f"Cụm {int(idx) + 1}",
                            "documents_id": [list_doc_ids[x] for x in cluster],
                            "algo_id": algo_id
                        }

                        logging.info(f"Processing cluster {idx + 1}/{len(list_cluster)} with {len(cluster)} documents")

                        tic = time.time()
                        cluster_docs = [list_docs[x] for x in cluster]
                        summary = call_ollama_multi_summary(cluster_docs, per, ollama_url, ollama_model)
                        toc = time.time()

                        logging.info(f"Cluster {idx + 1} summarization took {toc - tic:.2f}s")

                        if summary is None or summary == "":
                            summary = " ".join(cluster_docs)[:500]

                        obj.update({"text": summary})
                        output_format["result"]["cluster"].append(obj)

                    consumer.commit()
                    f = producer.send("result_ai", output_format)
                    f.get(60)
                    logging.info(f"Cluster mode completed for {sum_id}")

                else:
                    # Handle topic mode
                    logging.info("Processing in TOPIC mode")

                    for idx, top in enumerate(message.get("topic", [])):
                        obj = {
                            "text": "summary",
                            "topic_id": top["topic_id"],
                            "documents_id": top.get("list_doc_id", top.get("documents_id", [])),
                            "algo_id": top["algo_id"]
                        }

                        list_docs = top.get("list_doc", [])
                        logging.info(f"Processing topic {idx + 1}/{len(message['topic'])} with {len(list_docs)} documents")

                        tic = time.time()
                        summary = call_ollama_multi_summary(list_docs, per, ollama_url, ollama_model)
                        toc = time.time()

                        logging.info(f"Topic {idx + 1} summarization took {toc - tic:.2f}s")

                        if summary is None or summary == "":
                            summary = " ".join(list_docs)[:500]

                        obj.update({"text": summary})
                        output_format["result"]["topic"].append(obj)

                    consumer.commit()
                    f = producer.send("result_ai", output_format)
                    f.get(60)
                    logging.info(f"Topic mode completed for {sum_id}")

            except CommitFailedError as ex:
                logging.error(f"Commit failed for {sum_id}: {ex}")
                try:
                    requests.post(f"{url_status}", json={
                        "inMultiDocSumId": sum_id,
                        "inStatusId": 3
                    })
                except:
                    pass
                traceback.print_exc()
                consumer.subscribe([topic], listener=TestRebalanceListener(
                    consumer, TopicPartition(topic, current_partition), current_offset
                ))

        except Exception as e:
            logging.error(f"Error processing message: {e}")
            traceback.print_exc()
            try:
                sum_id = message.get("sumary_id", "unknown")
                requests.post(f"{url_status}", json={
                    "inMultiDocSumId": sum_id,
                    "inStatusId": 3
                })
            except:
                pass
            consumer.commit()


if __name__ == "__main__":
    main()
