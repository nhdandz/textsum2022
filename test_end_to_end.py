#!/usr/bin/env python3
"""
End-to-end test: Send message to topic_input_ai and verify routing to Ollama
"""

import json
import time
from kafka import KafkaProducer, KafkaConsumer
import os

KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', '192.168.210.42:9092')

# Sample text
SAMPLE_TEXT = """
Trí tuệ nhân tạo đang thay đổi thế giới. Machine learning cho phép máy tính
học từ dữ liệu. Deep learning sử dụng neural networks để xử lý thông tin phức tạp.
AI đang được ứng dụng trong nhiều lĩnh vực như y tế, giáo dục và kinh doanh.
"""

def send_to_topic_input_ai():
    """Send message to topic_input_ai with id_mapAlgTypeAI=[32]"""

    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda x: json.dumps(x).encode('utf-8'),
        max_request_size=100000000
    )

    # Message format theo chuẩn của hệ thống
    message = {
        "user_id": "test_end_to_end_user",
        "sumary_id": f"test_e2e_{int(time.time())}",
        "documents": [
            {
                "raw_text": SAMPLE_TEXT,
                "file_type": "txt",
                "page_from": 1,
                "page_to": 1,
                "documents_id": "test_doc_e2e_001"
            }
        ],
        "topic": [],  # Empty topic - sẽ tóm tắt toàn bộ văn bản
        "id_mapAlgTypeAI": [32],  # ID 32 = Ollama Single
        "percent_output": 0.3,
        "is_single": True,
        "is_topic": False
    }

    sumary_id = message["sumary_id"]

    print("=" * 80)
    print("🧪 END-TO-END ROUTING TEST")
    print("=" * 80)

    print(f"\n📝 Test Message:")
    print(f"   Sumary ID: {sumary_id}")
    print(f"   id_mapAlgTypeAI: [32]")
    print(f"   Expected route: topic_input_ai → single_root → 7_single_ollama")
    print(f"   Text length: {len(SAMPLE_TEXT)} chars")

    print(f"\n📤 Sending to topic_input_ai...")
    future = producer.send("topic_input_ai", message)
    record = future.get(timeout=10)

    print(f"✅ Sent successfully!")
    print(f"   Partition: {record.partition}")
    print(f"   Offset: {record.offset}")

    producer.close()

    return sumary_id


def monitor_ollama_topic(timeout=30):
    """Monitor if message arrives at 7_single_ollama topic"""

    print(f"\n👀 Monitoring topic '7_single_ollama' for incoming messages...")
    print(f"   Timeout: {timeout}s")

    consumer = KafkaConsumer(
        '7_single_ollama',
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        auto_offset_reset='latest',  # Only new messages
        enable_auto_commit=False,
        value_deserializer=lambda x: json.loads(x.decode('utf-8')),
        consumer_timeout_ms=timeout * 1000
    )

    start = time.time()

    for message in consumer:
        elapsed = time.time() - start
        data = message.value

        print(f"\n🎉 MESSAGE ARRIVED at 7_single_ollama!")
        print(f"   Time: {elapsed:.2f}s")
        print(f"   Partition: {message.partition}")
        print(f"   Offset: {message.offset}")
        print(f"\n📦 Message content:")
        print(f"   sumary_id: {data.get('sumary_id')}")
        print(f"   user_id: {data.get('user_id')}")
        print(f"   is_single: {data.get('is_single')}")
        print(f"   is_topic: {data.get('is_topic')}")

        topics = data.get('topic', [])
        if topics:
            print(f"   topics: {len(topics)} topic(s)")
            print(f"   algo_id: {topics[0].get('algo_id')}")
            print(f"   text length: {len(topics[0].get('raw_text', ''))}")

        print(f"\n✅ ROUTING SUCCESSFUL!")
        print(f"   topic_input_ai → single_root → 7_single_ollama ✓")

        consumer.close()
        return True

    print(f"\n⏱️  Timeout after {timeout}s - No message received")
    consumer.close()
    return False


def monitor_result(sumary_id, timeout=120):
    """Monitor result_ai topic for final result"""

    print(f"\n👀 Monitoring 'result_ai' for final result...")
    print(f"   Waiting for sumary_id: {sumary_id}")
    print(f"   Timeout: {timeout}s")

    consumer = KafkaConsumer(
        'result_ai',
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        auto_offset_reset='latest',
        enable_auto_commit=False,
        value_deserializer=lambda x: json.loads(x.decode('utf-8')),
        consumer_timeout_ms=timeout * 1000
    )

    start = time.time()

    for message in consumer:
        data = message.value

        if data.get('sumary_id') == sumary_id:
            elapsed = time.time() - start

            print(f"\n🎉 RESULT RECEIVED!")
            print(f"   Time: {elapsed:.2f}s")

            result = data.get('result', {})
            topics = result.get('topic', [])

            if topics:
                summary = topics[0].get('text', '')
                print(f"\n✨ Summary ({len(summary)} chars):")
                print("─" * 80)
                print(summary)
                print("─" * 80)

                print(f"\n📊 Statistics:")
                print(f"   Original: {len(SAMPLE_TEXT)} chars")
                print(f"   Summary: {len(summary)} chars")
                print(f"   Reduction: {(1 - len(summary)/len(SAMPLE_TEXT))*100:.1f}%")

            print(f"\n✅ END-TO-END TEST SUCCESSFUL!")
            consumer.close()
            return True

    print(f"\n⏱️  Timeout - No result received")
    consumer.close()
    return False


def check_logs():
    """Check service logs"""
    print("\n📋 Checking service logs...")

    print("\n1️⃣ root-kafka logs (routing decision):")
    print("─" * 80)
    os.system("docker logs --tail 5 root-kafka 2>&1 | grep -E 'send to|single root|multi root'")

    print("\n2️⃣ single-kafka logs (API call):")
    print("─" * 80)
    os.system("docker logs --tail 10 single-kafka 2>&1 | grep -E 'sumary_id|Done|get_detail_algo'")

    print("\n3️⃣ ollama-service logs (processing):")
    print("─" * 80)
    os.system("docker logs --tail 10 ollama-service 2>&1 | grep -E 'Processing|sumary_id|Ollama'")


def main():
    # Send message
    sumary_id = send_to_topic_input_ai()

    print("\n⏳ Waiting 2 seconds for routing...")
    time.sleep(2)

    # Monitor intermediate topic
    arrived = monitor_ollama_topic(timeout=15)

    if not arrived:
        print("\n❌ Message did not arrive at 7_single_ollama!")
        print("\n🔍 Checking logs for debugging...")
        check_logs()
        return

    # Monitor final result
    print("\n⏳ Waiting for Ollama to process...")
    success = monitor_result(sumary_id, timeout=120)

    if not success:
        print("\n⚠️  No result received")
        check_logs()

    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
