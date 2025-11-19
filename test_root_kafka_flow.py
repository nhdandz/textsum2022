#!/usr/bin/env python3
"""
Script để test luồng từ topic_input_ai -> root-kafka -> single_root
"""
from kafka import KafkaProducer, KafkaConsumer
import json
import os
import time
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', '192.168.213.13:9092')

def send_test_message():
    """Gửi một test message vào topic_input_ai"""
    print("📤 Gửi test message vào topic_input_ai...")

    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        max_request_size=100000000,
        value_serializer=lambda x: json.dumps(x).encode('utf-8')
    )

    test_doc = {
        "user_id": "test_user_debug",
        "sumary_id": f"test_summary_{int(time.time())}",
        "documents": [
            {
                "documents_id": "test_doc_123",
                "raw_text": "This is a test document for debugging root-kafka flow. We need to check if messages are properly routed from topic_input_ai to single_root topic.",
                "file_type": 0,
                "page_from": 0,
                "page_to": 9999
            }
        ],
        "topic": [],
        "percent_output": 0.1,
        "id_mapAlgTypeAI": [1],  # LexRank
        "is_single": True,
        "original_doc_ids": ["test_doc_123"]
    }

    print(f"\n📋 Message content:")
    print(f"   sumary_id: {test_doc['sumary_id']}")
    print(f"   is_single: {test_doc['is_single']}")
    print(f"   user_id: {test_doc['user_id']}")
    print(f"   id_mapAlgTypeAI: {test_doc['id_mapAlgTypeAI']}")

    producer.send("topic_input_ai", test_doc)
    producer.flush()
    producer.close()

    print("\n✅ Message đã được gửi vào topic_input_ai!")
    return test_doc['sumary_id']

def check_single_root(timeout=10):
    """Kiểm tra xem message có đến single_root không"""
    print(f"\n📥 Đang kiểm tra single_root topic (timeout {timeout}s)...")

    consumer = KafkaConsumer(
        'single_root',
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        auto_offset_reset='latest',  # Chỉ đọc message mới
        enable_auto_commit=False,
        consumer_timeout_ms=timeout * 1000,
        value_deserializer=lambda x: json.loads(x.decode('utf-8')) if x is not None else None
    )

    message_found = False
    start_time = time.time()

    print(f"⏳ Đang chờ message... (timeout {timeout}s)")

    for message in consumer:
        if message.value is not None:
            message_found = True
            elapsed = time.time() - start_time

            print(f"\n✅ NHẬN ĐƯỢC MESSAGE trong single_root!")
            print(f"⏱️  Thời gian: {elapsed:.2f}s")
            print(f"📋 Message:")
            print(f"   sumary_id: {message.value.get('sumary_id')}")
            print(f"   user_id: {message.value.get('user_id')}")
            print(f"   is_single: {message.value.get('is_single')}")

            break

    consumer.close()

    if not message_found:
        print(f"\n❌ KHÔNG nhận được message trong single_root sau {timeout}s")
        print(f"⚠️  Root-kafka có thể không hoạt động đúng!")

    return message_found

if __name__ == "__main__":
    print("="*80)
    print("🧪 TEST ROOT-KAFKA FLOW")
    print("="*80)
    print(f"\nKafka Server: {KAFKA_BOOTSTRAP_SERVERS}")
    print(f"Thời gian: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Bước 1: Gửi message
    sumary_id = send_test_message()

    # Đợi 2 giây để root-kafka xử lý
    print("\n⏳ Đợi 2 giây để root-kafka xử lý...")
    time.sleep(2)

    # Bước 2: Kiểm tra single_root
    success = check_single_root(timeout=10)

    print("\n" + "="*80)
    if success:
        print("✅ TEST THÀNH CÔNG!")
        print("   Message đã đi qua root-kafka và đến single_root")
    else:
        print("❌ TEST THẤT BẠI!")
        print("   Message KHÔNG đến single_root")
        print("\n💡 Các bước troubleshooting:")
        print("   1. Kiểm tra root-kafka container: docker logs root-kafka")
        print("   2. Kiểm tra root-kafka có đang chạy: docker ps | grep root-kafka")
        print("   3. Restart root-kafka: docker restart root-kafka")
        print("   4. Kiểm tra Kafka connection trong root-kafka container")
    print("="*80)
