#!/usr/bin/env python3
"""
Test script for Multi-Document Ollama summarization service
Sends a test message with multiple documents to Kafka topic and monitors the result
"""

import json
import time
from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import KafkaError
import sys
import os

# Configuration
KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', '192.168.210.42:9092')
INPUT_TOPIC = '33_multi_ollama'
OUTPUT_TOPIC = 'result_ai'

# Sample Vietnamese documents for testing
SAMPLE_DOCS = [
    """
    Công nghệ blockchain đang mở ra nhiều cơ hội mới cho ngành tài chính. Các ngân hàng lớn
    đang thử nghiệm ứng dụng blockchain để tăng tốc độ giao dịch và giảm chi phí. Công nghệ
    này cho phép ghi lại các giao dịch một cách minh bạch và bảo mật, không thể thay đổi sau
    khi đã được xác nhận. Nhiều chuyên gia tin rằng blockchain sẽ cách mạng hóa cách chúng ta
    chuyển tiền và quản lý tài sản trong tương lai.
    """,
    """
    Tiền điện tử như Bitcoin và Ethereum đang ngày càng được chấp nhận rộng rãi. Mặc dù có
    nhiều tranh cãi về tính biến động của giá, nhưng công nghệ cơ bản của chúng - blockchain -
    được đánh giá cao. Các nhà đầu tư tổ chức đang dần gia tăng đầu tư vào tiền điện tử như
    một loại tài sản thay thế. Việc một số quốc gia bắt đầu nghiên cứu phát hành tiền kỹ thuật
    số của ngân hàng trung ương cho thấy xu hướng số hóa trong tài chính là không thể đảo ngược.
    """,
    """
    Hợp đồng thông minh (smart contracts) là một ứng dụng quan trọng của blockchain. Chúng tự
    động thực thi các điều khoản của hợp đồng khi các điều kiện được đáp ứng, không cần bên
    trung gian. Điều này giúp giảm thiểu rủi ro gian lận và tăng hiệu quả trong nhiều lĩnh vực
    như bảo hiểm, bất động sản và chuỗi cung ứng. Các nền tảng như Ethereum đang dẫn đầu trong
    việc phát triển và triển khai hợp đồng thông minh.
    """
]

def create_test_message(mode="topic"):
    """
    Create a test message in the format expected by the multi-document service

    Args:
        mode: "topic" or "cluster"
    """
    message = {
        "user_id": "test_user_multi_123",
        "sumary_id": f"test_multi_summary_{int(time.time())}",
        "original_doc_ids": [f"test_doc_{i:03d}" for i in range(len(SAMPLE_DOCS))],
        "is_single": False,
        "is_cluster": mode == "cluster",
        "is_topic": mode == "topic",
        "percent_output": 0.3
    }

    if mode == "cluster":
        # Cluster mode: group documents for clustering
        message["cluster"] = {
            "list_doc": SAMPLE_DOCS,
            "list_doc_id": [f"test_doc_{i:03d}" for i in range(len(SAMPLE_DOCS))],
            "algo_id": "33",
            "percent_output": 0.3
        }
    else:
        # Topic mode: predefined document groups
        message["topic"] = [
            {
                "topic_id": "test_topic_multi_001",
                "list_doc": SAMPLE_DOCS,
                "list_doc_id": [f"test_doc_{i:03d}" for i in range(len(SAMPLE_DOCS))],
                "algo_id": "33",
                "percent_output": 0.3
            }
        ]

    return message


def send_test_message(mode="topic"):
    """Send test message to Kafka topic"""
    print(f"🚀 Connecting to Kafka at {KAFKA_BOOTSTRAP_SERVERS}...")

    try:
        producer = KafkaProducer(
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda x: json.dumps(x).encode('utf-8'),
            max_request_size=100000000
        )

        message = create_test_message(mode)
        sumary_id = message['sumary_id']

        print(f"\n📝 Test Message Details:")
        print(f"   Summary ID: {sumary_id}")
        print(f"   Algorithm: Multi Ollama (ID: 33)")
        print(f"   Mode: {mode.upper()}")
        print(f"   Number of documents: {len(SAMPLE_DOCS)}")
        print(f"   Total text length: {sum(len(doc) for doc in SAMPLE_DOCS)} characters")
        print(f"   Target summary: ~30% of original")
        print(f"   Topic: {INPUT_TOPIC}")

        print(f"\n📄 Document previews:")
        for i, doc in enumerate(SAMPLE_DOCS):
            preview = doc.strip()[:100] + "..."
            print(f"   Doc {i+1}: {preview}")

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


def monitor_results(sumary_id, timeout=180):
    """Monitor the result topic for the response"""
    print(f"\n👀 Monitoring topic '{OUTPUT_TOPIC}' for results...")
    print(f"   Waiting for summary_id: {sumary_id}")
    print(f"   Timeout: {timeout} seconds")
    print(f"   Press Ctrl+C to stop\n")

    try:
        consumer = KafkaConsumer(
            OUTPUT_TOPIC,
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            auto_offset_reset='latest',
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
                print(f"Is Topic: {data.get('is_topic')}")

                result = data.get('result', {})

                # Display cluster results
                clusters = result.get('cluster', [])
                if clusters:
                    print(f"\n📊 CLUSTER RESULTS ({len(clusters)} clusters):")
                    for idx, cluster in enumerate(clusters):
                        print(f"\n{'='*80}")
                        print(f"Cluster {idx + 1}: {cluster.get('displayName')}")
                        print(f"Documents: {len(cluster.get('documents_id', []))}")
                        print(f"Algorithm ID: {cluster.get('algo_id')}")

                        summary = cluster.get('text', '')
                        print(f"\n✨ Summary ({len(summary)} chars):")
                        print("-" * 80)
                        print(summary)
                        print("-" * 80)

                # Display topic results
                topics = result.get('topic', [])
                if topics:
                    print(f"\n📑 TOPIC RESULTS ({len(topics)} topics):")
                    for idx, topic in enumerate(topics):
                        print(f"\n{'='*80}")
                        print(f"Topic {idx + 1}")
                        print(f"Topic ID: {topic.get('topic_id')}")
                        print(f"Documents: {len(topic.get('documents_id', []))}")
                        print(f"Algorithm ID: {topic.get('algo_id')}")

                        summary = topic.get('text', '')
                        total_orig = sum(len(doc) for doc in SAMPLE_DOCS)
                        reduction = (1 - len(summary) / total_orig) * 100

                        print(f"\n✨ Summary ({len(summary)} chars):")
                        print("-" * 80)
                        print(summary)
                        print("-" * 80)

                        print(f"\n📊 Statistics:")
                        print(f"   Original: {total_orig} characters")
                        print(f"   Summary: {len(summary)} characters")
                        print(f"   Reduction: {reduction:.1f}%")

                if not clusters and not topics:
                    print("⚠️  No results found in response")

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


def check_service_logs():
    """Show recent logs from multi-ollama-service"""
    print("\n📋 Recent Multi-Ollama Service Logs:")
    print("=" * 80)
    os.system("docker logs --tail 30 multi-ollama-service 2>&1")
    print("=" * 80)


def main():
    """Main test function"""
    print("=" * 80)
    print("🧪 MULTI-DOCUMENT OLLAMA SUMMARIZATION SERVICE TEST")
    print("=" * 80)

    # Determine mode
    mode = "topic"  # Default mode
    if len(sys.argv) > 1 and sys.argv[1] == "cluster":
        mode = "cluster"

    print(f"\n🔧 Testing in {mode.upper()} mode")

    # Send test message
    sumary_id = send_test_message(mode)

    if not sumary_id:
        print("\n❌ Failed to send test message. Exiting.")
        sys.exit(1)

    # Wait a bit for processing to start
    print("\n⏳ Waiting 5 seconds for service to start processing...")
    time.sleep(5)

    # Show service logs
    check_service_logs()

    # Monitor for results (longer timeout for multi-doc)
    success = monitor_results(sumary_id, timeout=180)

    if not success:
        print("\n⚠️  Result not received. Checking service logs again...")
        check_service_logs()
        print("\n💡 Troubleshooting tips:")
        print("   1. Check if multi-ollama-service is running: docker ps | grep multi-ollama")
        print("   2. Check service logs: docker logs -f multi-ollama-service")
        print("   3. Verify Ollama is accessible: curl http://192.168.210.47:11434/api/tags")
        print("   4. Check clustering service (if using cluster mode): docker ps | grep clustering")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
