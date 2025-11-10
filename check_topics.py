#!/usr/bin/env python3
"""Check last messages in routing topics"""
import json
from kafka import KafkaConsumer, TopicPartition

KAFKA_BOOTSTRAP_SERVERS = '192.168.210.42:9092'

def check_last_message(topic_name):
    print(f"\n{'='*80}")
    print(f"Topic: {topic_name}")
    print('='*80)

    consumer = KafkaConsumer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_deserializer=lambda x: json.loads(x.decode('utf-8')) if x else None,
        consumer_timeout_ms=2000
    )

    partitions = consumer.partitions_for_topic(topic_name)
    if not partitions:
        print(f"  ❌ Topic not found or has no partitions")
        consumer.close()
        return

    tp = TopicPartition(topic_name, 0)
    consumer.assign([tp])
    consumer.seek_to_end(tp)
    pos = consumer.position(tp)

    print(f"  Total messages: {pos}")

    if pos > 0:
        # Get last 3 messages
        start_offset = max(0, pos - 3)
        consumer.seek(tp, start_offset)

        messages = []
        for msg in consumer:
            messages.append(msg)
            if len(messages) >= 3:
                break

        for i, msg in enumerate(messages):
            data = msg.value
            if data:
                print(f"\n  Message {start_offset + i} (offset {msg.offset}):")
                print(f"    sumary_id: {data.get('sumary_id')}")
                print(f"    id_mapAlgTypeAI: {data.get('id_mapAlgTypeAI')}")
                print(f"    is_single: {data.get('is_single')}")

    consumer.close()

if __name__ == "__main__":
    check_last_message("topic_input_ai")
    check_last_message("single_root")
    check_last_message("7_single_ollama")
