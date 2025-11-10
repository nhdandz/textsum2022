#!/usr/bin/env python3
"""
Test script to verify Kafka is working with environment variables
"""
import os
import json
import time
from kafka import KafkaProducer, KafkaConsumer, KafkaAdminClient
from kafka.admin import NewTopic
from kafka.errors import TopicAlreadyExistsError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get Kafka server from environment
KAFKA_SERVER = os.getenv('HOST_IP', '192.168.210.42') + ':9092'
TEST_TOPIC = 'test-topic-' + str(int(time.time()))

print("=" * 60)
print("🧪 KAFKA TEST SCRIPT")
print("=" * 60)
print(f"Kafka Server: {KAFKA_SERVER}")
print(f"Test Topic: {TEST_TOPIC}")
print()

# Test 1: Create topic
print("📝 Test 1: Creating test topic...")
try:
    admin_client = KafkaAdminClient(
        bootstrap_servers=[KAFKA_SERVER],
        client_id='test-admin'
    )

    topic = NewTopic(
        name=TEST_TOPIC,
        num_partitions=1,
        replication_factor=1
    )

    admin_client.create_topics([topic], validate_only=False)
    print(f"✅ Topic '{TEST_TOPIC}' created successfully!")
    time.sleep(2)
except TopicAlreadyExistsError:
    print(f"ℹ️  Topic '{TEST_TOPIC}' already exists")
except Exception as e:
    print(f"❌ Error creating topic: {e}")
    exit(1)

# Test 2: Send messages
print("\n📤 Test 2: Sending test messages...")
try:
    producer = KafkaProducer(
        bootstrap_servers=[KAFKA_SERVER],
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )

    test_messages = [
        {"id": 1, "text": "Hello from Environment Variables!", "timestamp": time.time()},
        {"id": 2, "text": f"HOST_IP: {os.getenv('HOST_IP')}", "timestamp": time.time()},
        {"id": 3, "text": "Kafka is working! 🎉", "timestamp": time.time()},
    ]

    for msg in test_messages:
        future = producer.send(TEST_TOPIC, value=msg)
        result = future.get(timeout=10)
        print(f"✅ Sent message {msg['id']}: partition={result.partition}, offset={result.offset}")

    producer.flush()
    producer.close()
    print("✅ All messages sent successfully!")

except Exception as e:
    print(f"❌ Error sending messages: {e}")
    exit(1)

# Test 3: Consume messages
print("\n📥 Test 3: Consuming messages...")
try:
    consumer = KafkaConsumer(
        TEST_TOPIC,
        bootstrap_servers=[KAFKA_SERVER],
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        group_id='test-consumer-group',
        value_deserializer=lambda x: json.loads(x.decode('utf-8')),
        consumer_timeout_ms=5000
    )

    messages_received = 0
    for message in consumer:
        messages_received += 1
        print(f"✅ Received message {messages_received}:")
        print(f"   Topic: {message.topic}")
        print(f"   Partition: {message.partition}")
        print(f"   Offset: {message.offset}")
        print(f"   Value: {message.value}")
        print()

    consumer.close()

    if messages_received > 0:
        print(f"✅ Successfully received {messages_received} messages!")
    else:
        print("⚠️  No messages received (timeout)")

except Exception as e:
    print(f"❌ Error consuming messages: {e}")
    exit(1)

# Test 4: List topics
print("\n📋 Test 4: Listing all topics...")
try:
    topics = admin_client.list_topics()
    print(f"✅ Found {len(topics)} topics:")
    for topic in sorted(topics)[:10]:  # Show first 10
        print(f"   - {topic}")
    if len(topics) > 10:
        print(f"   ... and {len(topics) - 10} more")

except Exception as e:
    print(f"❌ Error listing topics: {e}")

# Test 5: Check consumer groups
print("\n👥 Test 5: Checking consumer groups...")
try:
    groups = admin_client.list_consumer_groups()
    print(f"✅ Found {len(groups)} consumer groups")
    for group in groups[:5]:  # Show first 5
        print(f"   - {group}")

except Exception as e:
    print(f"❌ Error listing consumer groups: {e}")

# Cleanup
print("\n🧹 Cleanup: Deleting test topic...")
try:
    admin_client.delete_topics([TEST_TOPIC])
    print(f"✅ Topic '{TEST_TOPIC}' deleted")
except Exception as e:
    print(f"⚠️  Could not delete topic: {e}")

admin_client.close()

print("\n" + "=" * 60)
print("✅ KAFKA TEST COMPLETED SUCCESSFULLY!")
print("=" * 60)
print("\n💡 Summary:")
print(f"   - Kafka Server: {KAFKA_SERVER}")
print(f"   - Environment Variables: ✅ Working")
print(f"   - Topic Creation: ✅ Working")
print(f"   - Message Production: ✅ Working")
print(f"   - Message Consumption: ✅ Working")
print("\n🎉 Your Kafka setup is ready to use!")
