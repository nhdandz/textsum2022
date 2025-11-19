#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script test thuật toán Multi xử lý tóm tắt theo chủ đề qua Kafka
"""

from kafka import KafkaProducer, KafkaConsumer
import json
import base64
import time
import sys

# Configuration
KAFKA_BOOTSTRAP = 'localhost:9092'
KAFKA_INPUT_TOPIC = 'topic_input_ai'
KAFKA_OUTPUT_TOPIC = 'output_topic'


def create_producer():
    """Tạo Kafka producer"""
    return KafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP,
        max_request_size=100000000,
        value_serializer=lambda x: json.dumps(x).encode('utf-8')
    )


def encode_sample_text():
    """Tạo sample text về khoa học công nghệ"""
    sample_texts = [
        """
        Trí tuệ nhân tạo (AI) đang cách mạng hóa lĩnh vực khoa học và công nghệ.
        Machine learning và deep learning là những công nghệ tiên tiến nhất hiện nay.
        Các nhà khoa học đang phát triển các thuật toán mới để cải thiện độ chính xác của mô hình AI.
        Công nghệ blockchain cũng đang được nghiên cứu rộng rãi trong cộng đồng khoa học toàn cầu.
        Điện toán đám mây giúp xử lý dữ liệu lớn hiệu quả hơn cho các nghiên cứu khoa học phức tạp.
        Nghiên cứu về Internet vạn vật kết hợp với trí tuệ nhân tạo đang phát triển mạnh mẽ.
        Các công nghệ mới đang được áp dụng trong nhiều lĩnh vực khoa học khác nhau.
        Robot và tự động hóa đang thay đổi cách thức nghiên cứu khoa học hiện đại.
        Công nghệ sinh học kết hợp với AI mở ra nhiều cơ hội mới cho y học và khoa học sự sống.
        Quantum computing là một bước tiến lớn trong khoa học máy tính và công nghệ tính toán.
        """,
        """
        Nghiên cứu về khoa học dữ liệu đang phát triển nhanh chóng với sự trợ giúp của công nghệ mới.
        Các công nghệ tiên tiến như quantum computing đang được khám phá trong nhiều nghiên cứu khoa học.
        Trí tuệ nhân tạo giúp tự động hóa nhiều quy trình nghiên cứu khoa học phức tạp.
        Internet vạn vật (IoT) kết nối các thiết bị thông minh phục vụ cho nghiên cứu khoa học.
        Công nghệ 5G mang lại tốc độ truyền tải cao hơn cho các hệ thống khoa học thông tin.
        Các nhà khoa học đang sử dụng công nghệ AI để phân tích dữ liệu phức tạp và lớn.
        Nghiên cứu về công nghệ sinh học cũng được hưởng lợi từ AI và khoa học dữ liệu hiện đại.
        Big Data và phân tích dữ liệu là trọng tâm của nhiều dự án nghiên cứu khoa học.
        Công nghệ thực tế ảo (VR) và thực tế tăng cường (AR) đang được ứng dụng trong giáo dục khoa học.
        Khoa học máy tính và công nghệ phần mềm đang tiến bộ với tốc độ chưa từng có.
        """
    ]

    return sample_texts


def test_multi_topic_summarization(algo_id=23, algo_name="MultiTexRank"):
    """Test tóm tắt multi-document với topic"""
    print(f"\n{'='*70}")
    print(f"TEST THUẬT TOÁN MULTI VỚI TOPIC: {algo_name} (ID={algo_id})")
    print(f"{'='*70}\n")

    # Lấy sample text
    sample_texts = encode_sample_text()

    # Encode to base64
    encoded_texts = []
    for text in sample_texts:
        encoded = base64.b64encode(text.encode('utf-8')).decode('utf-8')
        encoded_texts.append(encoded)

    # Tạo payload
    payload = {
        "user_id": f"test_user_{algo_id}_{int(time.time())}",
        "sumary_id": f"test_summary_topic_{algo_id}_{int(time.time())}",
        "original_doc_ids": ["doc_001", "doc_002"],
        "documents": [
            {
                "documents_id": "doc_001",
                "raw_text": encoded_texts[0],
                "file_type": 0,  # 0 = text
                "page_from": 0,
                "page_to": 9999
            },
            {
                "documents_id": "doc_002",
                "raw_text": encoded_texts[1],
                "file_type": 0,
                "page_from": 0,
                "page_to": 9999
            }
        ],
        "topic": [
            {
                "keywords": [
                    ["khoa học", "công nghệ"],  # AND: phải chứa
                    []                           # NOT: loại trừ (empty)
                ],
                "topic_id": 120,
                "id_mapAlgTypeAI": algo_id
            }
        ],
        "id_mapAlgTypeAI": [],
        "percent_output": 0.1,
        "is_single": False
    }

    print(f"📋 PAYLOAD:")
    print(f"   User ID:         {payload['user_id']}")
    print(f"   Summary ID:      {payload['sumary_id']}")
    print(f"   Số documents:    {len(payload['documents'])}")
    print(f"   Topic ID:        {payload['topic'][0]['topic_id']}")
    print(f"   Keywords:        {payload['topic'][0]['keywords']}")
    print(f"   Algorithm ID:    {algo_id} ({algo_name})")
    print(f"   Percent output:  {payload['percent_output']}")
    print(f"   Is single:       {payload['is_single']}")
    print()

    try:
        # Tạo producer
        print("🔌 Đang kết nối Kafka...")
        producer = create_producer()
        print("✓ Đã kết nối Kafka")

        # Gửi message
        print(f"📤 Đang gửi message đến topic '{KAFKA_INPUT_TOPIC}'...")
        future = producer.send(KAFKA_INPUT_TOPIC, payload)
        record_metadata = future.get(timeout=10)

        print(f"✓ Đã gửi thành công!")
        print(f"   Topic:     {record_metadata.topic}")
        print(f"   Partition: {record_metadata.partition}")
        print(f"   Offset:    {record_metadata.offset}")
        print()

        producer.flush()
        producer.close()

        print("🎯 CÁCH THEO DÕI KẾT QUẢ:")
        print("   1. Xem logs multi-kafka:")
        print("      docker compose logs -f multi-kafka")
        print()
        print("   2. Xem logs thuật toán:")
        print(f"      docker compose logs -f m-textrank m-lexrank m-lsa")
        print()
        print("   3. Kafka UI:")
        print("      http://localhost:8080")
        print()
        print("   4. Kiểm tra output topic:")
        print(f"      python3 check_kafka_output.py {payload['sumary_id']}")
        print()

        return True

    except Exception as e:
        print(f"✗ LỖI: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_multiple_algorithms():
    """Test nhiều thuật toán"""
    print("\n" + "="*70)
    print("  TEST NHIỀU THUẬT TOÁN MULTI VỚI TOPIC")
    print("="*70)

    algorithms = [
        {"id": 23, "name": "MultiTexRank"},
        {"id": 24, "name": "MultiLexRank"},
        {"id": 25, "name": "MultiLSA"},
    ]

    results = []
    for algo in algorithms:
        print(f"\n{'─'*70}")
        success = test_multi_topic_summarization(algo["id"], algo["name"])
        results.append({
            "algorithm": algo["name"],
            "id": algo["id"],
            "success": success
        })
        time.sleep(2)  # Đợi giữa các test

    # Tổng kết
    print(f"\n{'='*70}")
    print("TỔNG KẾT")
    print(f"{'='*70}")

    for result in results:
        status = "✓ SENT" if result["success"] else "✗ FAILED"
        print(f"{result['algorithm']:20s} (ID={result['id']:2d}): {status}")

    print()


def main():
    if len(sys.argv) > 1:
        # Test thuật toán cụ thể
        algo_id = int(sys.argv[1])
        algo_name = sys.argv[2] if len(sys.argv) > 2 else f"Algorithm_{algo_id}"
        test_multi_topic_summarization(algo_id, algo_name)
    else:
        # Test nhiều thuật toán
        test_multiple_algorithms()


if __name__ == "__main__":
    main()
