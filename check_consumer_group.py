#!/usr/bin/env python3
"""
Script để kiểm tra consumer group offset
"""
from kafka import KafkaConsumer
from kafka.structs import TopicPartition
import os
from dotenv import load_dotenv

load_dotenv()

KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', '192.168.213.13:9092')
GROUP_ID = 'root-input1'
TOPIC = 'topic_input_ai'

print(f"🔍 Kiểm tra Consumer Group: {GROUP_ID}")
print(f"📊 Topic: {TOPIC}")
print(f"🌐 Kafka Server: {KAFKA_BOOTSTRAP_SERVERS}\n")

try:
    # Tạo consumer để kiểm tra offset
    consumer = KafkaConsumer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        group_id=GROUP_ID,
        enable_auto_commit=False
    )

    # Subscribe to topic
    consumer.subscribe([TOPIC])

    # Poll once to get assignment
    consumer.poll(timeout_ms=1000)

    # Get assigned partitions
    partitions = consumer.assignment()

    if not partitions:
        print(f"⚠️  Consumer không có partition nào được assign!")
    else:
        print(f"✅ Partitions được assign: {len(partitions)}\n")

        for partition in partitions:
            # Get current position (next offset to read)
            position = consumer.position(partition)

            # Get committed offset (last committed offset)
            committed = consumer.committed(partition)

            # Get end offset (latest offset in partition)
            end_offsets = consumer.end_offsets([partition])
            end_offset = end_offsets[partition]

            # Get beginning offset
            beginning_offsets = consumer.beginning_offsets([partition])
            beginning_offset = beginning_offsets[partition]

            lag = end_offset - (committed if committed is not None else 0)

            print(f"📌 Partition {partition.partition}:")
            print(f"   Beginning offset: {beginning_offset}")
            print(f"   Committed offset: {committed}")
            print(f"   Current position: {position}")
            print(f"   End offset (latest): {end_offset}")
            print(f"   📊 LAG: {lag} messages")

            if lag > 0:
                print(f"   ⚠️  CÓ {lag} message(s) chưa được xử lý!")
            else:
                print(f"   ✅ Tất cả messages đã được xử lý")
            print()

    consumer.close()

except Exception as e:
    print(f"❌ Lỗi: {str(e)}")
    import traceback
    traceback.print_exc()
