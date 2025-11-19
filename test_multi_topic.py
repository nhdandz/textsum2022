#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script kiểm tra thuật toán Multi xử lý tóm tắt theo chủ đề
Tương ứng với payload mà user cung cấp
"""

import requests
import json
import base64
import time

# Configuration
ALGO_CONTROL_URL = "http://localhost:6789"
APP_PROCESS_URL = "http://localhost:9980"
KAFKA_INPUT_TOPIC_URL = "http://localhost:9092/kafka/topic_input_ai"

def test_health_check():
    """Kiểm tra services có hoạt động không"""
    print("=" * 60)
    print("1. KIỂM TRA HEALTH CHECK")
    print("=" * 60)

    services = {
        "algo-control": f"{ALGO_CONTROL_URL}/",
        "app-process": f"{APP_PROCESS_URL}/",
    }

    for name, url in services.items():
        try:
            response = requests.get(url, timeout=5)
            status = "✓ OK" if response.status_code == 200 else f"✗ FAILED ({response.status_code})"
            print(f"{name:20s}: {status}")
        except Exception as e:
            print(f"{name:20s}: ✗ ERROR - {str(e)}")
    print()


def encode_sample_text():
    """Tạo sample text về khoa học công nghệ"""
    sample_texts = [
        """
        Trí tuệ nhân tạo (AI) đang cách mạng hóa lĩnh vực khoa học và công nghệ.
        Machine learning và deep learning là những công nghệ tiên tiến nhất hiện nay.
        Các nhà khoa học đang phát triển các thuật toán mới để cải thiện độ chính xác.
        Công nghệ blockchain cũng đang được nghiên cứu rộng rãi.
        Điện toán đám mây giúp xử lý dữ liệu lớn hiệu quả hơn.
        """,
        """
        Nghiên cứu về khoa học dữ liệu đang phát triển nhanh chóng.
        Các công nghệ mới như quantum computing đang được khám phá.
        Trí tuệ nhân tạo giúp tự động hóa nhiều quy trình.
        Internet vạn vật (IoT) kết nối các thiết bị thông minh.
        Công nghệ 5G mang lại tốc độ truyền tải cao hơn.
        """
    ]

    # Encode to base64
    encoded = []
    for text in sample_texts:
        encoded.append(base64.b64encode(text.encode('utf-8')).decode('utf-8'))

    return encoded


def test_payload_original():
    """Test với payload mà user cung cấp (đã sửa để phù hợp)"""
    print("=" * 60)
    print("2. TEST VỚI PAYLOAD GỐC (CÓ TOPIC)")
    print("=" * 60)

    encoded_texts = encode_sample_text()

    payload = {
        "user_id": "test_user_001",
        "sumary_id": "test_summary_topic_120",
        "original_doc_ids": ["doc_001", "doc_002"],
        "documents": [
            {
                "documents_id": "doc_001",
                "raw_text": encoded_texts[0],
                "file_type": 0,  # 0 = text
                "page_from": 0,
                "page_to": 1
            },
            {
                "documents_id": "doc_002",
                "raw_text": encoded_texts[1],
                "file_type": 0,
                "page_from": 0,
                "page_to": 1
            }
        ],
        "topic": [
            {
                "keywords": [
                    ["khoa học", "công nghệ"],  # AND clause - phải chứa
                    []                           # NOT clause - loại trừ
                ],
                "topic_id": 120,
                "id_mapAlgTypeAI": 17  # HiMap algorithm
            }
        ],
        "id_mapAlgTypeAI": [],
        "percent_output": 0.1,
        "is_single": False
    }

    print(f"📤 Gửi payload với:")
    print(f"   - Số documents: {len(payload['documents'])}")
    print(f"   - Topic ID: {payload['topic'][0]['topic_id']}")
    print(f"   - Keywords: {payload['topic'][0]['keywords']}")
    print(f"   - Algorithm ID: {payload['topic'][0]['id_mapAlgTypeAI']} (HiMap)")
    print(f"   - Percent output: {payload['percent_output']}")
    print(f"   - Is single: {payload['is_single']}")
    print()

    try:
        # Gửi request
        print(f"🔄 Đang gửi request đến Kafka...")
        response = requests.post(
            KAFKA_INPUT_TOPIC_URL,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )

        print(f"📥 Response status: {response.status_code}")
        print(f"📥 Response body: {response.text}")
        print()

        if response.status_code == 200:
            print("✓ Payload đã được gửi thành công!")
            print(f"⏰ Chờ xử lý... (có thể mất vài phút)")
            print(f"💡 Kiểm tra Kafka UI tại: http://localhost:8088")
            print(f"💡 Kiểm tra logs: docker-compose logs -f multi-kafka")
        else:
            print(f"✗ Lỗi khi gửi payload: {response.text}")

    except Exception as e:
        print(f"✗ Exception: {str(e)}")

    print()


def test_check_short_topic():
    """Test endpoint check_short_topic"""
    print("=" * 60)
    print("3. TEST ENDPOINT /check_short_topic")
    print("=" * 60)

    test_text = """
    Trí tuệ nhân tạo đang cách mạng hóa lĩnh vực khoa học và công nghệ.
    Machine learning và deep learning là những công nghệ tiên tiến.
    """

    payload = {
        "keywords": [["khoa học", "công nghệ"], []],
        "text": test_text
    }

    print(f"📤 Test với text: {test_text[:50]}...")
    print(f"📤 Keywords: {payload['keywords']}")

    try:
        response = requests.post(
            f"{APP_PROCESS_URL}/check_short_topic",
            json=payload,
            timeout=10
        )

        result = response.json()
        print(f"📥 Response: {result}")
        print(f"   Text is short after topic filter: {result.get('is_short', False)}")

    except Exception as e:
        print(f"✗ Error: {str(e)}")

    print()


def test_multi_algorithms():
    """Test các thuật toán Multi khác nhau"""
    print("=" * 60)
    print("4. TEST CÁC THUẬT TOÁN MULTI KHÁC NHAU")
    print("=" * 60)

    algorithms = [
        {"id": 17, "name": "HiMap", "algorId": 17},
        {"id": 19, "name": "MultiBart", "algorId": 19},
        {"id": 20, "name": "MultiPeg", "algorId": 20},
        {"id": 21, "name": "Primera", "algorId": 21},
        {"id": 23, "name": "MultiTexRank", "algorId": 23},
        {"id": 24, "name": "MultiLexRank", "algorId": 24},
        {"id": 25, "name": "MultiLSA", "algorId": 25},
    ]

    print("Các thuật toán Multi có thể test:")
    for algo in algorithms:
        print(f"  {algo['id']:2d}. {algo['name']:20s} (algorId: {algo['algorId']})")

    print()
    print("💡 Để test thuật toán khác, sửa 'id_mapAlgTypeAI' trong payload")
    print("💡 Ví dụ: Thay 17 (HiMap) → 23 (MultiTexRank)")
    print()


def show_monitoring_commands():
    """Hiển thị các lệnh monitor"""
    print("=" * 60)
    print("5. LỆNH MONITOR & DEBUG")
    print("=" * 60)

    commands = [
        ("Xem logs algo-control", "docker-compose logs -f algo-control"),
        ("Xem logs app-process", "docker-compose logs -f app-process"),
        ("Xem logs multi-kafka", "docker-compose logs -f multi-kafka"),
        ("Xem logs thuật toán", "docker-compose logs -f m-textrank m-lexrank m-lsa"),
        ("Kafka UI", "http://localhost:8088"),
        ("Check health", "curl http://localhost:9980/"),
        ("Xem tất cả containers", "docker-compose ps"),
        ("Xem resource usage", "docker stats"),
    ]

    for desc, cmd in commands:
        print(f"  • {desc:25s}: {cmd}")

    print()


def show_workflow():
    """Hiển thị workflow xử lý"""
    print("=" * 60)
    print("6. WORKFLOW XỬ LÝ TÓM TẮT THEO CHỦ ĐỀ")
    print("=" * 60)

    print("""
    1. Client gửi payload với topic → Kafka topic_input_ai

    2. algo-control nhận message:
       ├─ Kiểm tra is_single = false → Multi-document
       └─ Forward đến multi-kafka consumer

    3. multi-kafka xử lý:
       ├─ Gọi app-process để extract nội dung từ documents
       ├─ Lọc văn bản theo keywords trong topic:
       │  ├─ keywords[0]: phải chứa ("khoa học" AND "công nghệ")
       │  └─ keywords[1]: loại trừ (empty = không loại trừ)
       ├─ Kiểm tra văn bản sau filter có đủ dài không
       └─ Chọn thuật toán theo id_mapAlgTypeAI trong topic

    4. Gọi thuật toán tương ứng:
       ├─ id=17 → HiMap (port 8898)
       ├─ id=23 → MultiTexRank (port 7302)
       ├─ id=24 → MultiLexRank (port 7302)
       └─ ...

    5. Thuật toán xử lý và trả về kết quả tóm tắt

    6. Kết quả được gửi đến Kafka output topic
    """)


if __name__ == "__main__":
    print("\n")
    print("=" * 60)
    print("  TEST THUẬT TOÁN MULTI XỬ LÝ TÓM TẮT THEO CHỦ ĐỀ")
    print("=" * 60)
    print()

    # Run tests
    test_health_check()
    test_check_short_topic()
    test_multi_algorithms()
    show_monitoring_commands()
    show_workflow()

    # Main test
    input("⏸  Nhấn Enter để gửi payload test (hoặc Ctrl+C để thoát)...")
    test_payload_original()

    print()
    print("=" * 60)
    print("✓ HOÀN TẤT!")
    print("=" * 60)
    print()
