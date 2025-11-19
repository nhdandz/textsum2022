#!/usr/bin/env python3
"""
Script để kiểm tra trạng thái consumer group chi tiết
"""
from kafka.admin import KafkaAdminClient
from kafka import KafkaConsumer
from kafka.structs import TopicPartition, OffsetAndMetadata
import os
from dotenv import load_dotenv

load_dotenv()

KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', '192.168.213.13:9092')
GROUP_ID = 'root-input1'
TOPIC = 'topic_input_ai'

print(f"🔍 KIỂM TRA CONSUMER GROUP STATUS")
print(f"{'='*80}\n")
print(f"Consumer Group: {GROUP_ID}")
print(f"Topic: {TOPIC}")
print(f"Kafka Server: {KAFKA_BOOTSTRAP_SERVERS}\n")

try:
    # Tạo admin client
    admin = KafkaAdminClient(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        client_id='status_checker'
    )

    # List tất cả consumer groups
    consumer_groups = admin.list_consumer_groups()
    print(f"📋 Tất cả Consumer Groups ({len(consumer_groups)}):")
    for group in consumer_groups:
        print(f"   • {group[0]} (protocol: {group[1]})")

    # Check if our group exists
    group_exists = any(g[0] == GROUP_ID for g in consumer_groups)
    print(f"\n{'='*80}")
    if group_exists:
        print(f"✅ Consumer group '{GROUP_ID}' TỒN TẠI")
    else:
        print(f"⚠️  Consumer group '{GROUP_ID}' KHÔNG TỒN TẠI")
        print(f"   → Có thể consumer chưa bao giờ chạy hoặc đã bị xóa")

    print(f"\n{'='*80}")
    print(f"📊 Kiểm tra offset của topic '{TOPIC}':\n")

    # Create a simple consumer to check offsets
    temp_consumer = KafkaConsumer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        enable_auto_commit=False
    )

    # Get partitions for topic
    partitions = temp_consumer.partitions_for_topic(TOPIC)

    if partitions:
        print(f"Topic có {len(partitions)} partition(s)\n")

        for partition_id in partitions:
            tp = TopicPartition(TOPIC, partition_id)

            # Get beginning and end offsets
            beginning = temp_consumer.beginning_offsets([tp])[tp]
            end = temp_consumer.end_offsets([tp])[tp]

            print(f"Partition {partition_id}:")
            print(f"   Beginning offset: {beginning}")
            print(f"   End offset: {end}")
            print(f"   Total messages: {end - beginning}")

            # Check committed offset for the group
            try:
                committed_consumer = KafkaConsumer(
                    bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                    group_id=GROUP_ID,
                    enable_auto_commit=False
                )
                committed = committed_consumer.committed(tp)
                committed_consumer.close()

                if committed is not None:
                    lag = end - committed
                    print(f"   Committed offset (group '{GROUP_ID}'): {committed}")
                    print(f"   📊 LAG: {lag} messages")

                    if lag > 0:
                        print(f"   ⚠️  CÓ {lag} MESSAGE(S) CHƯA ĐƯỢC XỬ LÝ!")
                    else:
                        print(f"   ✅ Đã xử lý hết")
                else:
                    print(f"   ⚠️  Group chưa commit offset nào")
                    print(f"   📊 LAG: {end - beginning} messages (chưa xử lý)")
            except Exception as e:
                print(f"   ⚠️  Không thể lấy committed offset: {str(e)}")

            print()

    temp_consumer.close()
    admin.close()

except Exception as e:
    print(f"❌ Lỗi: {str(e)}")
    import traceback
    traceback.print_exc()

print(f"{'='*80}")
print("✅ Hoàn thành kiểm tra!")
print(f"{'='*80}\n")
