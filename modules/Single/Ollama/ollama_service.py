from kafka import KafkaConsumer, KafkaProducer
from kafka.errors import CommitFailedError
from kafka import TopicPartition, ConsumerRebalanceListener
from json import loads
import init
import json
import requests
import logging
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed

logging.basicConfig(level=logging.INFO)

# Token estimation constants
CHARS_PER_TOKEN_VI = 4  # Vietnamese text: ~4 chars per token
MAX_TOKENS = 15000  # Safety margin for 33k context window (conservative for better quality)
MAX_CHARS = MAX_TOKENS * CHARS_PER_TOKEN_VI
MAX_WORKERS = 4  # Number of parallel workers for chunking (adjust based on GPU/CPU capacity)

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


def call_ollama_summary_single(text: str, percent: float, ollama_url: str, model: str = "mistral") -> str:
    """Call Ollama API for single chunk summarization"""
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
                "prompt": f"Hãy đọc và hiểu văn bản sau, sau đó viết lại thành bản tóm tắt tóm lược (abstractive summary) bằng tiếng Việt với khoảng {num_sentences} câu. DIỄN GIẢI LẠI nội dung bằng cách hiểu của bạn, đừng chỉ sao chép câu gốc. Trả về nội dung súc tích, rõ ràng, không thêm XML, tag hay giải thích:\n\n{text}",
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

            # Normalize excessive whitespace (fix multiple newlines)
            summary = normalize_whitespace(summary)

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


def call_ollama_combine_summaries(combined_text: str, percent: float, ollama_url: str, model: str = "mistral") -> str:
    """
    Call Ollama API to combine multiple chunk summaries into a coherent narrative text
    This function creates a flowing document instead of bullet points
    """
    try:
        # Calculate number of sentences for final summary
        import nltk
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt', quiet=True)

        sentences = nltk.sent_tokenize(combined_text)
        # For combining phase, reduce output more aggressively to avoid long processing time
        if len(sentences) > 50:
            # For long combined texts, reduce more aggressively
            target_ratio = percent * 0.8  # Reduce by half
            num_sentences = max(10, int(len(sentences) * target_ratio))
        else:
            num_sentences = max(2, int(len(sentences) * percent))

        logging.info(f"Combining {len(sentences)} sentences from chunks into {num_sentences} sentences")

        # Call Ollama API with special prompt for combining summaries
        response = requests.post(
            f"{ollama_url}/api/generate",
            json={
                "model": model,
                "prompt": f"""{combined_text}
                Hãy đọc kỹ và hiểu các phần nội dung ở trên, sau đó viết lại thành một bản tóm tắt tóm lược (abstractive summary) bằng tiếng Việt, với khoảng {num_sentences} câu.

YÊU CẦU QUAN TRỌNG:
- DIỄN GIẢI LẠI nội dung bằng cách hiểu của bạn, KHÔNG chỉ sao chép câu gốc
- Viết dưới dạng các đoạn văn (paragraphs) liền mạch, tự nhiên
- KHÔNG sử dụng số thứ tự (1., 2., 3.), đầu mục, hay gạch đầu dòng
- Sử dụng các từ nối để kết nối ý giữa các phần (ví dụ: "Bên cạnh đó", "Ngoài ra", "Đồng thời", v.v.)
- Giữ đúng thứ tự logic và nội dung của văn bản gốc
- Diễn đạt ngắn gọn, súc tích nhưng đầy đủ ý nghĩa
- Chỉ trả về nội dung tóm tắt, không thêm XML, tag hay giải thích
 
{combined_text}""",
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "top_p": 0.9
                }
            },
            timeout=900  # Increased to 15 minutes for large combined summaries
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

            logging.info(f"Combined summarization successful, length: {len(summary)}")
            return summary
        else:
            logging.error(f"Ollama API error: {response.status_code} - {response.text}")
            # Fallback: return combined text as is
            return combined_text

    except Exception as e:
        logging.error(f"Ollama combine summaries failed: {e}")
        traceback.print_exc()
        # Fallback: return combined text as is
        return combined_text


def summarize_chunk_wrapper(args):
    """Wrapper function for parallel chunk summarization"""
    chunk_idx, chunk, percent, ollama_url, model = args
    try:
        logging.info(f"Summarizing chunk {chunk_idx} (~{estimate_token_count(chunk)} tokens)")
        summary = call_ollama_summary_single(chunk, percent, ollama_url, model)
        logging.info(f"Chunk {chunk_idx} completed")
        return (chunk_idx, summary, None)
    except Exception as e:
        logging.error(f"Failed to summarize chunk {chunk_idx}: {e}")
        # Fallback: use first part of chunk
        try:
            import nltk
            try:
                nltk.data.find('tokenizers/punkt')
            except LookupError:
                nltk.download('punkt', quiet=True)
            sentences = nltk.sent_tokenize(chunk)
            num_sentences = max(2, int(len(sentences) * percent))
            fallback_summary = " ".join(sentences[:num_sentences])
            return (chunk_idx, fallback_summary, str(e))
        except Exception as fallback_error:
            logging.error(f"Fallback also failed for chunk {chunk_idx}: {fallback_error}")
            return (chunk_idx, chunk[:1000], str(fallback_error))


def call_ollama_summary(text: str, percent: float, ollama_url: str, model: str = "mistral") -> str:
    """
    Call Ollama API for text summarization with hierarchical chunking and parallel processing
    Automatically handles large texts by splitting into chunks and processing them in parallel
    """
    estimated_tokens = estimate_token_count(text)
    logging.info(f"Text estimated at ~{estimated_tokens} tokens ({len(text)} chars)")

    # If text is within token limit, summarize directly
    if estimated_tokens <= MAX_TOKENS:
        logging.info("Text within token limit, using direct summarization")
        return call_ollama_summary_single(text, percent, ollama_url, model)

    # Text is too large, use hierarchical summarization with parallel processing
    logging.info(f"Text exceeds token limit, using hierarchical summarization with parallel processing")
    chunks = chunk_text_by_tokens(text, MAX_TOKENS)
    logging.info(f"Split text into {len(chunks)} chunks, processing with {MAX_WORKERS} workers")

    # Step 1: Summarize each chunk in parallel
    chunk_summaries = [None] * len(chunks)  # Pre-allocate to maintain order

    # Prepare arguments for parallel processing
    chunk_args = [
        (i + 1, chunk, percent, ollama_url, model)
        for i, chunk in enumerate(chunks)
    ]

    # Use ThreadPoolExecutor for parallel processing
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # Submit all tasks
        future_to_idx = {
            executor.submit(summarize_chunk_wrapper, args): args[0]
            for args in chunk_args
        }

        # Collect results as they complete
        for future in as_completed(future_to_idx):
            chunk_idx, summary, error = future.result()
            chunk_summaries[chunk_idx - 1] = summary
            if error:
                logging.warning(f"Chunk {chunk_idx} had error: {error}")

    # Step 2: Combine chunk summaries
    combined_summary = "\n\n".join(chunk_summaries)
    logging.info(f"Combined summaries length: {len(combined_summary)} chars (~{estimate_token_count(combined_summary)} tokens)")

    # Step 3: If combined summary is still too large, recursively summarize
    if estimate_token_count(combined_summary) > MAX_TOKENS:
        logging.info("Combined summary still too large, applying recursive summarization")
        return call_ollama_summary(combined_summary, percent, ollama_url, model)
    else:
        # Final summarization of combined chunks into coherent narrative
        logging.info("Applying final summarization to combined chunks")
        return call_ollama_combine_summaries(combined_summary, percent, ollama_url, model)


def main():
    logging.info("Starting Ollama summarization service...")

    consumer = KafkaConsumer(
        bootstrap_servers=init.configs["bootstrap_servers"],
        auto_offset_reset='latest',  # Changed to 'latest' to skip old stuck messages
        enable_auto_commit=False,
        max_poll_records=5,
        max_poll_interval_ms=1800000,  # 30 minutes for large text chunking
        session_timeout_ms=60000,  # 60 seconds session timeout
        heartbeat_interval_ms=20000,  # 20 seconds heartbeat
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
