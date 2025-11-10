#!/usr/bin/env python3
"""
Test script for Ollama summarization service
Sends a test message to Kafka topic and monitors the result
"""

import json
import time
from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import KafkaError
import sys
import os

# Configuration
KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', '192.168.210.42:9092')
INPUT_TOPIC = '7_single_ollama'
OUTPUT_TOPIC = 'result_ai'

# Sample Vietnamese text for testing
SAMPLE_TEXT = """
Trí tuệ nhân tạo (AI) đang phát triển với tốc độ chưa từng có, mang lại nhiều cơ hội và thách thức cho xã hội.
Các mô hình ngôn ngữ lớn như GPT, Claude, và các mô hình mã nguồn mở như Llama, Mistral đã chứng minh khả năng
xử lý ngôn ngữ tự nhiên ở mức độ cao. Những công nghệ này đang được ứng dụng rộng rãi trong nhiều lĩnh vực như
y tế, giáo dục, tài chính, và dịch vụ khách hàng. Tuy nhiên, việc phát triển AI cũng đặt ra những câu hỏi về
đạo đức, quyền riêng tư, và tác động đến thị trường lao động. Các nhà nghiên cứu và chính phủ đang tìm cách
cân bằng giữa đổi mới sáng tạo và quản lý rủi ro để đảm bảo AI phát triển theo hướng có lợi cho nhân loại.
Việc phát triển các mô hình AI cần tuân thủ các nguyên tắc minh bạch, công bằng và an toàn để tránh các
hậu quả tiêu cực không mong muốn.
"""

def create_test_message():
    """Create a test message in the format expected by the service"""
    return {
        "user_id": "test_user_123",
        "sumary_id": f"test_summary_{int(time.time())}",
        "original_doc_ids": ["test_doc_001"],
        "is_single": True,
        "is_topic": True,
        "documents": [
            {
                "raw_text": SAMPLE_TEXT,
                "file_type": "txt",
                "page_from": 1,
                "page_to": 1,
                "documents_id": "test_doc_001"
            }
        ],
        "topic": [
            {
                "topic_id": "test_topic_001",
                "raw_text": SAMPLE_TEXT,
                "documents_id": ["test_doc_001"],
                "algo_id": "32",  # Ollama algorithm ID
                "percent_output": 0.3,  # 30% length
                "id_mapAlgTypeAI": "map_001"
            }
        ],
        "id_mapAlgTypeAI": ["map_001"],
        "percent_output": 0.3
    }


def send_test_message():
    """Send test message to Kafka topic"""
    print(f"🚀 Connecting to Kafka at {KAFKA_BOOTSTRAP_SERVERS}...")

    try:
        producer = KafkaProducer(
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda x: json.dumps(x).encode('utf-8'),
            max_request_size=100000000
        )

        message = create_test_message()
        sumary_id = message['sumary_id']

        print(f"\n📝 Test Message Details:")
        print(f"   Summary ID: {sumary_id}")
        print(f"   Algorithm: Ollama (ID: 32)")
        print(f"   Text length: {len(SAMPLE_TEXT)} characters")
        print(f"   Target summary: ~30% of original")
        print(f"   Topic: {INPUT_TOPIC}")

        print(f"\n📤 Sending message to topic '{INPUT_TOPIC}'...")
        future = producer.send(INPUT_TOPIC, message)

        # Wait for send to complete
        record_metadata = future.get(timeout=10)

        print(f"✅ Message sent successfully!")
        print(f"   Partition: {record_metadata.partition}")
        print(f"   Offset: {record_metadata.offset}")

        producer.flush()
        producer.close()

        return sumary_id

    except KafkaError as e:
        print(f"❌ Kafka error: {e}")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None


def monitor_results(sumary_id, timeout=120):
    """Monitor the result topic for the response"""
    print(f"\n👀 Monitoring topic '{OUTPUT_TOPIC}' for results...")
    print(f"   Waiting for summary_id: {sumary_id}")
    print(f"   Timeout: {timeout} seconds")
    print(f"   Press Ctrl+C to stop\n")

    try:
        consumer = KafkaConsumer(
            OUTPUT_TOPIC,
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            auto_offset_reset='latest',  # Only read new messages
            enable_auto_commit=False,
            value_deserializer=lambda x: json.loads(x.decode('utf-8')),
            consumer_timeout_ms=timeout * 1000
        )

        start_time = time.time()
        message_count = 0

        for message in consumer:
            message_count += 1
            elapsed = time.time() - start_time

            data = message.value
            msg_sumary_id = data.get('sumary_id', 'unknown')

            print(f"📨 Message {message_count} received (offset: {message.offset}, elapsed: {elapsed:.1f}s)")

            if msg_sumary_id == sumary_id:
                print(f"\n🎉 Found our result!")
                print(f"=" * 80)
                print(f"Summary ID: {msg_sumary_id}")
                print(f"User ID: {data.get('user_id')}")
                print(f"Is Single: {data.get('is_single')}")

                result = data.get('result', {})
                topics = result.get('topic', [])

                if topics:
                    for idx, topic in enumerate(topics):
                        print(f"\n--- Topic {idx + 1} ---")
                        print(f"Topic ID: {topic.get('topic_id')}")
                        print(f"Algorithm ID: {topic.get('algo_id')}")
                        print(f"\n📄 Original Text ({len(SAMPLE_TEXT)} chars):")
                        print("-" * 80)
                        print(SAMPLE_TEXT.strip())
                        print("-" * 80)

                        summary = topic.get('text', '')
                        print(f"\n✨ Summary ({len(summary)} chars):")
                        print("=" * 80)
                        print(summary)
                        print("=" * 80)

                        reduction = (1 - len(summary) / len(SAMPLE_TEXT)) * 100
                        print(f"\n📊 Statistics:")
                        print(f"   Original: {len(SAMPLE_TEXT)} characters")
                        print(f"   Summary: {len(summary)} characters")
                        print(f"   Reduction: {reduction:.1f}%")
                else:
                    print("⚠️  No topic results found in response")

                print(f"\n✅ Test completed successfully in {elapsed:.1f} seconds!")
                consumer.close()
                return True
            else:
                print(f"   ⏭️  Skipping (different summary_id: {msg_sumary_id})")

        print(f"\n⏱️  Timeout reached after {timeout} seconds")
        print(f"   Processed {message_count} messages but didn't find our result")
        consumer.close()
        return False

    except KeyboardInterrupt:
        print("\n\n⚠️  Monitoring stopped by user")
        return False
    except Exception as e:
        print(f"\n❌ Error monitoring results: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_ollama_service_logs():
    """Show recent logs from ollama-service"""
    print("\n📋 Recent Ollama Service Logs:")
    print("=" * 80)
    os.system("docker logs --tail 20 ollama-service 2>&1")
    print("=" * 80)


def main():
    """Main test function"""
    print("=" * 80)
    print("🧪 OLLAMA SUMMARIZATION SERVICE TEST")
    print("=" * 80)

    # Send test message
    sumary_id = send_test_message()

    if not sumary_id:
        print("\n❌ Failed to send test message. Exiting.")
        sys.exit(1)

    # Wait a bit for processing to start
    print("\n⏳ Waiting 3 seconds for service to start processing...")
    time.sleep(3)

    # Show service logs
    check_ollama_service_logs()

    # Monitor for results
    success = monitor_results(sumary_id, timeout=120)

    if not success:
        print("\n⚠️  Result not received. Checking service logs again...")
        check_ollama_service_logs()
        print("\n💡 Troubleshooting tips:")
        print("   1. Check if ollama-service is running: docker ps | grep ollama")
        print("   2. Check service logs: docker logs -f ollama-service")
        print("   3. Verify Kafka topics: docker exec kafka-1 kafka-topics.sh --list --bootstrap-server localhost:9092")
        print("   4. Check if Ollama is accessible: curl http://192.168.210.47:11434/api/tags")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
