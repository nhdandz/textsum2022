#!/usr/bin/env python3
"""
Test clustering with documents from 2 different topics
"""

import json
import time
from kafka import KafkaProducer, KafkaConsumer
import sys
import os

KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', '192.168.210.42:9092')
INPUT_TOPIC = '33_multi_ollama'
OUTPUT_TOPIC = 'result_ai'

# 2 chủ đề khác nhau: AI và Nông nghiệp
SAMPLE_DOCS = [
    # Chủ đề 1: AI và Machine Learning (3 văn bản)
    """
    Trí tuệ nhân tạo (AI) đang cách mạng hóa nhiều ngành công nghiệp. Các thuật toán
    học máy (machine learning) cho phép máy tính học từ dữ liệu và cải thiện hiệu suất
    theo thời gian. Deep learning, một nhánh của machine learning, sử dụng mạng neural
    nhân tạo để xử lý dữ liệu phức tạp. Các ứng dụng AI đang được triển khai rộng rãi
    trong nhận diện hình ảnh, xử lý ngôn ngữ tự nhiên và xe tự lái.
    """,

    """
    Machine learning đang trở thành công cụ thiết yếu trong phân tích dữ liệu lớn.
    Các mô hình supervised learning như Random Forest và SVM giúp dự đoán chính xác
    dựa trên dữ liệu đã được gắn nhãn. Unsupervised learning như K-means clustering
    giúp khám phá patterns ẩn trong dữ liệu. Reinforcement learning đang được ứng
    dụng trong game AI và robotics, cho phép agent học thông qua thử và sai.
    """,

    """
    Neural networks đã đạt được những bước tiến vượt bậc nhờ GPU computing và big data.
    Convolutional Neural Networks (CNN) xuất sắc trong computer vision, trong khi
    Recurrent Neural Networks (RNN) và Transformers thống trị NLP. Transfer learning
    cho phép tái sử dụng mô hình đã huấn luyện, tiết kiệm thời gian và tài nguyên.
    AutoML đang làm cho machine learning dễ tiếp cận hơn với người dùng phi kỹ thuật.
    """,

    # Chủ đề 2: Nông nghiệp và Công nghệ (3 văn bản)
    """
    Nông nghiệp công nghệ cao đang thay đổi cách chúng ta sản xuất thực phẩm. IoT sensors
    giám sát độ ẩm đất, nhiệt độ và dinh dưỡng theo thời gian thực. Drone nông nghiệp
    giúp khảo sát cánh đồng, phun thuốc chính xác và đánh giá sức khỏe cây trồng. Hệ thống
    tưới tiêu tự động tối ưu hóa việc sử dụng nước, giảm lãng phí và tăng năng suất.
    """,

    """
    Công nghệ blockchain đang được áp dụng trong chuỗi cung ứng nông sản để đảm bảo
    truy xuất nguồn gốc. Smart farming sử dụng dữ liệu thời tiết, đất đai và lịch sử
    mùa vụ để tối ưu hóa kế hoạch canh tác. Vertical farming và aquaponics mang lại
    giải pháp sản xuất thực phẩm bền vững trong đô thị. Công nghệ di truyền giúp
    tạo giống cây trồng chịu hạn, chống sâu bệnh tốt hơn.
    """,

    """
    Robot nông nghiệp đang tự động hóa các công việc thu hoạch và chăm sóc cây trồng.
    Precision agriculture sử dụng GPS và GIS để quản lý từng mảnh đất một cách tối ưu.
    Biofertilizer và biopesticide giảm phụ thuộc vào hóa chất độc hại. Công nghệ
    blockchain và AI kết hợp tạo nên hệ thống quản lý trang trại thông minh, dự đoán
    năng suất và giá cả thị trường chính xác hơn.
    """
]

def create_cluster_test_message():
    """Create message with diverse documents for clustering"""
    return {
        "user_id": "test_cluster_user",
        "sumary_id": f"test_cluster_{int(time.time())}",
        "original_doc_ids": [f"doc_{i:03d}" for i in range(len(SAMPLE_DOCS))],
        "is_single": False,
        "is_cluster": True,  # Cluster mode
        "is_topic": False,
        "percent_output": 0.25,
        "cluster": {
            "list_doc": SAMPLE_DOCS,
            "list_doc_id": [f"doc_{i:03d}" for i in range(len(SAMPLE_DOCS))],
            "algo_id": "33",
            "percent_output": 0.25
        }
    }

def send_message():
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda x: json.dumps(x).encode('utf-8'),
        max_request_size=100000000
    )

    message = create_cluster_test_message()
    sumary_id = message['sumary_id']

    print("=" * 80)
    print("🧪 TEST: CLUSTERING WITH 2 DIFFERENT TOPICS")
    print("=" * 80)
    print(f"\n📝 Test Details:")
    print(f"   Summary ID: {sumary_id}")
    print(f"   Mode: CLUSTER (automatic)")
    print(f"   Documents: {len(SAMPLE_DOCS)}")
    print(f"   Expected clusters: 2 (AI vs Agriculture)")

    print(f"\n📚 Document Topics:")
    print(f"   Doc 0-2: AI, Machine Learning, Neural Networks (3 docs)")
    print(f"   Doc 3-5: Agriculture, Smart Farming, IoT (3 docs)")

    print(f"\n📤 Sending to Kafka...")
    future = producer.send(INPUT_TOPIC, message)
    record = future.get(timeout=10)

    print(f"✅ Sent! Partition: {record.partition}, Offset: {record.offset}")
    producer.close()

    return sumary_id

def monitor_results(sumary_id, timeout=240):
    print(f"\n👀 Monitoring results...")
    print(f"   Waiting for: {sumary_id}")
    print(f"   Timeout: {timeout}s\n")

    consumer = KafkaConsumer(
        OUTPUT_TOPIC,
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
            print(f"\n🎉 RESULTS RECEIVED! ({elapsed:.1f}s)")
            print("=" * 80)

            result = data.get('result', {})
            clusters = result.get('cluster', [])

            print(f"\n📊 CLUSTERING RESULTS:")
            print(f"   Number of clusters: {len(clusters)}")

            if len(clusters) == 2:
                print(f"   ✅ SUCCESS: Detected 2 clusters as expected!")
            elif len(clusters) == 1:
                print(f"   ⚠️  Only 1 cluster (all docs grouped together)")
            else:
                print(f"   🤔 Unexpected: {len(clusters)} clusters")

            print(f"\n{'='*80}")

            for idx, cluster in enumerate(clusters):
                print(f"\n🗂️  CLUSTER {idx + 1}: {cluster.get('displayName')}")
                print(f"{'─'*80}")

                doc_ids = cluster.get('documents_id', [])
                print(f"📄 Documents: {len(doc_ids)}")
                print(f"   IDs: {', '.join(doc_ids)}")

                # Phân tích cluster composition
                ai_docs = [d for d in doc_ids if d in ['doc_000', 'doc_001', 'doc_002']]
                agri_docs = [d for d in doc_ids if d in ['doc_003', 'doc_004', 'doc_005']]

                print(f"\n📑 Composition:")
                if ai_docs:
                    print(f"   • AI/ML docs: {len(ai_docs)} - {ai_docs}")
                if agri_docs:
                    print(f"   • Agriculture docs: {len(agri_docs)} - {agri_docs}")

                # Đánh giá cluster purity
                if len(ai_docs) == len(doc_ids):
                    print(f"   ✅ Pure AI cluster")
                elif len(agri_docs) == len(doc_ids):
                    print(f"   ✅ Pure Agriculture cluster")
                else:
                    print(f"   ⚠️  Mixed cluster")

                summary = cluster.get('text', '')
                print(f"\n✨ Summary ({len(summary)} chars):")
                print(f"{'─'*80}")
                print(summary)
                print(f"{'─'*80}")

            # Overall clustering quality assessment
            print(f"\n📈 CLUSTERING QUALITY ASSESSMENT:")
            if len(clusters) == 2:
                cluster1_docs = set(clusters[0].get('documents_id', []))
                cluster2_docs = set(clusters[1].get('documents_id', []))

                ai_set = set(['doc_000', 'doc_001', 'doc_002'])
                agri_set = set(['doc_003', 'doc_004', 'doc_005'])

                # Check if clustering is perfect
                if (cluster1_docs == ai_set and cluster2_docs == agri_set) or \
                   (cluster1_docs == agri_set and cluster2_docs == ai_set):
                    print("   ✅ PERFECT CLUSTERING!")
                    print("   All AI docs in one cluster, all Agriculture docs in another")
                else:
                    # Calculate purity
                    c1_ai = len(cluster1_docs & ai_set)
                    c1_agri = len(cluster1_docs & agri_set)
                    c2_ai = len(cluster2_docs & ai_set)
                    c2_agri = len(cluster2_docs & agri_set)

                    print(f"   Cluster 1: {c1_ai} AI docs, {c1_agri} Agri docs")
                    print(f"   Cluster 2: {c2_ai} AI docs, {c2_agri} Agri docs")

                    purity = (max(c1_ai, c1_agri) + max(c2_ai, c2_agri)) / 6
                    print(f"   Purity: {purity*100:.1f}%")

            print(f"\n{'='*80}")
            consumer.close()
            return True

    print(f"\n⏱️  Timeout after {timeout}s")
    consumer.close()
    return False

def main():
    sumary_id = send_message()

    if not sumary_id:
        print("❌ Failed to send message")
        sys.exit(1)

    print("\n⏳ Waiting 5s for processing to start...")
    time.sleep(5)

    print("\n📋 Service logs:")
    print("=" * 80)
    os.system("docker logs --tail 15 multi-ollama-service 2>&1 | grep -i 'cluster\\|processing'")
    print("=" * 80)

    success = monitor_results(sumary_id, timeout=240)

    if not success:
        print("\n⚠️  No result received. Check logs:")
        os.system("docker logs --tail 30 multi-ollama-service")

if __name__ == "__main__":
    main()
