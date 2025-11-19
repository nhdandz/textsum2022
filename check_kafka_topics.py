#!/usr/bin/env python3
"""
Script để kiểm tra messages trong các Kafka topics
"""
from kafka import KafkaConsumer
from kafka.admin import KafkaAdminClient
from json import loads
import os
from dotenv import load_dotenv

load_dotenv()

# Lấy Kafka bootstrap servers từ .env
KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', '192.168.213.13:9092')

def check_topic_messages(topic_name, max_messages=5):
    """Kiểm tra messages trong topic"""
    print(f"\n{'='*80}")
    print(f"📊 Kiểm tra topic: {topic_name}")
    print(f"{'='*80}")

    try:
        consumer = KafkaConsumer(
            topic_name,
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            auto_offset_reset='earliest',
            enable_auto_commit=False,
            consumer_timeout_ms=5000,  # Timeout sau 5 giây
            value_deserializer=lambda x: loads(x.decode('utf-8')) if x is not None else None
        )

        message_count = 0
        for message in consumer:
            message_count += 1
            print(f"\n📨 Message {message_count}:")
            print(f"  Offset: {message.offset}")
            print(f"  Partition: {message.partition}")
            print(f"  Timestamp: {message.timestamp}")

            if message.value is not None:
                print(f"  Value preview:")
                # Print các field quan trọng
                if isinstance(message.value, dict):
                    if 'sumary_id' in message.value:
                        print(f"    sumary_id: {message.value.get('sumary_id')}")
                    if 'is_single' in message.value:
                        print(f"    is_single: {message.value.get('is_single')}")
                    if 'user_id' in message.value:
                        print(f"    user_id: {message.value.get('user_id')}")
                    if 'id_mapAlgTypeAI' in message.value:
                        print(f"    id_mapAlgTypeAI: {message.value.get('id_mapAlgTypeAI')}")
                else:
                    print(f"    {str(message.value)[:200]}")
            else:
                print(f"  Value: Tombstone record (None)")

            if message_count >= max_messages:
                break

        consumer.close()

        if message_count == 0:
            print(f"\n⚠️  Topic '{topic_name}' KHÔNG có message nào!")
        else:
            print(f"\n✅ Tìm thấy {message_count} message(s) trong topic '{topic_name}'")

        return message_count

    except Exception as e:
        print(f"\n❌ Lỗi khi kiểm tra topic '{topic_name}': {str(e)}")
        return 0

def list_all_topics():
    """List tất cả topics hiện có"""
    print(f"\n{'='*80}")
    print("📋 Danh sách tất cả Kafka topics")
    print(f"{'='*80}")

    try:
        admin_client = KafkaAdminClient(
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            client_id='topic_checker'
        )

        topics = admin_client.list_topics()
        print(f"\nTổng số topics: {len(topics)}")
        for topic in sorted(topics):
            print(f"  • {topic}")

        admin_client.close()
        return topics

    except Exception as e:
        print(f"\n❌ Lỗi khi list topics: {str(e)}")
        return []

if __name__ == "__main__":
    print(f"🔍 KAFKA TOPIC CHECKER")
    print(f"Kafka Server: {KAFKA_BOOTSTRAP_SERVERS}\n")

    # List tất cả topics
    all_topics = list_all_topics()

    # Kiểm tra các topics quan trọng
    important_topics = ['topic_input_ai', 'single_root', 'multi_root']

    print(f"\n{'='*80}")
    print("🔎 Kiểm tra các topics quan trọng")
    print(f"{'='*80}")

    for topic in important_topics:
        if topic in all_topics:
            check_topic_messages(topic, max_messages=3)
        else:
            print(f"\n❌ Topic '{topic}' không tồn tại!")

    print(f"\n{'='*80}")
    print("✅ Hoàn thành kiểm tra!")
    print(f"{'='*80}\n")
