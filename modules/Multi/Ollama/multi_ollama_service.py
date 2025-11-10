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

logging.basicConfig(level=logging.INFO)


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


def call_ollama_multi_summary(documents: list, percent: float, ollama_url: str, model: str = "mistral") -> str:
    """Call Ollama API for multi-document summarization"""
    try:
        import nltk
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt', quiet=True)

        # Combine all documents
        combined_text = "\n\n".join(documents)

        # Calculate target length
        sentences = nltk.sent_tokenize(combined_text)
        num_sentences = max(3, int(len(sentences) * percent))

        logging.info(f"Multi-doc: {len(documents)} documents, {len(sentences)} total sentences -> {num_sentences} sentences")

        # Create prompt for multi-document summarization
        doc_list = "\n\n".join([f"--- Văn bản {i+1} ---\n{doc}" for i, doc in enumerate(documents)])

        prompt = f"""/nothink Bạn là một trợ lý tóm tắt văn bản chuyên nghiệp. Hãy đọc {len(documents)} văn bản sau đây và tạo một bản tóm tắt tổng hợp thành khoảng {num_sentences} câu.

Yêu cầu:
- Tổng hợp thông tin từ TẤT CẢ các văn bản
- Làm nổi bật các điểm chung và khác biệt (nếu có)
- Trả về CHỈ phần tóm tắt, không thêm giải thích hay nhận xét

{doc_list}

Tóm tắt tổng hợp:"""

        response = requests.post(
            f"{ollama_url}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "top_p": 0.9,
                    "num_ctx": 8192  # Larger context for multi-doc
                }
            },
            timeout=600  # Longer timeout for multi-doc
        )

        if response.status_code == 200:
            result = response.json()
            summary = result.get("response", "").strip()

            # Clean up <think> tags if present
            if "<think>" in summary and "</think>" in summary:
                import re
                summary = re.sub(r'<think>.*?</think>', '', summary, flags=re.DOTALL).strip()

            logging.info(f"Multi-doc summarization successful, length: {len(summary)}")
            return summary
        else:
            logging.error(f"Ollama API error: {response.status_code} - {response.text}")
            # Fallback: return first sentences from first document
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
        auto_offset_reset='latest',  # Changed to 'latest' to skip old stuck messages
        enable_auto_commit=False,
        max_poll_records=5,
        max_poll_interval_ms=600000,
        group_id="30_multi_ollama_v2",  # Changed group_id to reset offset
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
