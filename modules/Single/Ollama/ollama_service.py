from kafka import KafkaConsumer, KafkaProducer
from kafka.errors import CommitFailedError
from kafka import TopicPartition, ConsumerRebalanceListener
from json import loads
import init
import json
import requests
import logging
import traceback

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


def call_ollama_summary(text: str, percent: float, ollama_url: str, model: str = "mistral") -> str:
    """Call Ollama API for text summarization"""
    try:
        # Calculate number of sentences
        import nltk
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt', quiet=True)

        sentences = nltk.sent_tokenize(text)
        num_sentences = max(2, int(len(sentences) * percent))

        logging.info(f"Calling Ollama with model {model} to summarize {len(sentences)} sentences to {num_sentences}")

        # Call Ollama API
        response = requests.post(
            f"{ollama_url}/api/generate",
            json={
                "model": model,
                "prompt": f"Hãy tóm tắt văn bản sau đây thành khoảng {num_sentences} câu bằng tiếng Việt. Chỉ trả về phần tóm tắt, không thêm bất kỳ thẻ XML, tag hoặc giải thích nào khác. Chỉ trả về nội dung tóm tắt thuần túy:\n\n{text}",
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "top_p": 0.9
                }
            },
            timeout=300
        )

        if response.status_code == 200:
            result = response.json()
            summary = result.get("response", "").strip()

            # Remove any XML-like tags from the response
            import re
            summary = re.sub(r'<think>.*?</think>', '', summary, flags=re.DOTALL)
            summary = re.sub(r'<[^>]+>', '', summary)
            summary = summary.strip()

            logging.info(f"Ollama summarization successful, length: {len(summary)}")
            return summary
        else:
            logging.error(f"Ollama API error: {response.status_code} - {response.text}")
            # Fallback: return first part of text
            return " ".join(sentences[:num_sentences])

    except Exception as e:
        logging.error(f"Ollama summarization failed: {e}")
        traceback.print_exc()
        # Fallback: return first sentences
        try:
            import nltk
            sentences = nltk.sent_tokenize(text)
            num_sentences = max(2, int(len(sentences) * percent))
            return " ".join(sentences[:num_sentences])
        except:
            return text[:len(text)//3]


def main():
    logging.info("Starting Ollama summarization service...")

    consumer = KafkaConsumer(
        bootstrap_servers=init.configs["bootstrap_servers"],
        auto_offset_reset='latest',  # Changed to 'latest' to skip old stuck messages
        enable_auto_commit=False,
        max_poll_records=5,
        max_poll_interval_ms=600000,
        group_id="7_single_ollama_v2",  # Changed group_id to reset offset
        value_deserializer=lambda x: loads(x.decode('utf-8')))

    topic = "7_single_ollama"
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

            sum_id = message["sumary_id"]
            logging.info(f"Processing message with sumary_id: {sum_id}")

            try:
                topic_count = len(message.get('topic', []))
                logging.info(f"Message has {topic_count} topics")
            except Exception as e:
                logging.error(f"Error analyzing message: {e}")
                traceback.print_exc()
                consumer.commit()
                continue

            url_status = init.configs["url_status_Web"]

            # Check status (skip if API unavailable for testing)
            skip_message = False
            try:
                logging.info(f"Checking status at: {url_status}/{sum_id}")
                res = requests.get(f"{url_status}/{sum_id}", timeout=5)
                logging.info(f"Status check response: {res.status_code}")
                res = json.loads(res.content)
                if not res.get("data", {}).get("status", True):
                    logging.info(f"Skipping sumary_id {sum_id} - status is false")
                    skip_message = True
            except Exception as e:
                logging.warning(f"Failed to check status for {sum_id}: {e}")
                logging.info(f"Continuing anyway (status API might be unavailable)")
                # Don't skip if status API is unavailable - continue processing

            if skip_message:
                consumer.commit()
                continue

            output_format = {
                "user_id": message["user_id"],
                "sumary_id": message["sumary_id"],
                "original_doc_ids": message["original_doc_ids"],
                "is_single": True,
                "is_topic": message["is_topic"],
                "result": {"cluster": [], "topic": []}
            }

            # Update status to processing
            try:
                requests.post(f"{url_status}", json={
                    "inMultiDocSumId": sum_id,
                    "inStatusId": 1
                }, timeout=5)
                logging.info(f"Updated status to processing for {sum_id}")
            except Exception as e:
                logging.warning(f"Failed to update status: {e}")

            try:
                for idx, top in enumerate(message["topic"]):
                    logging.info(f"Processing topic {idx + 1}/{len(message['topic'])}")

                    obj = {
                        "text": "summary",
                        "topic_id": top["topic_id"],
                        "documents_id": top["documents_id"],
                        "algo_id": top["algo_id"]
                    }

                    try:
                        per = top["percent_output"]
                        if per is None:
                            per = 0.1
                    except:
                        per = 0.1

                    # Call Ollama service
                    summary = call_ollama_summary(
                        top["raw_text"],
                        per,
                        ollama_url,
                        ollama_model
                    )
                    obj.update({"text": summary})
                    output_format["result"]["topic"].append(obj)

                logging.info(f"Committing offset and sending result for {sum_id}")
                consumer.commit()
                f = producer.send("result_ai", output_format)
                f.get(60)
                logging.info(f"Successfully completed processing for {sum_id}")

            except CommitFailedError as ex:
                logging.error(f"Commit failed for {sum_id}: {ex}")
                try:
                    requests.post(f"{url_status}", json={
                        "inMultiDocSumId": sum_id,
                        "inStatusId": 3
                    }, timeout=5)
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
                }, timeout=5)
            except:
                pass
            consumer.commit()


if __name__ == "__main__":
    main()
