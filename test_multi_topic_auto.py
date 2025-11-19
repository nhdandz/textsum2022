#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script test tự động thuật toán Multi xử lý tóm tắt theo chủ đề
"""

import requests
import json
import base64
import sys

# Configuration
ALGO_CONTROL_URL = "http://localhost:6789"
APP_PROCESS_URL = "http://localhost:9980"

def encode_sample_text():
    """Tạo sample text về khoa học công nghệ"""
    sample_texts = [
        """
        Trí tuệ nhân tạo (AI) đang cách mạng hóa lĩnh vực khoa học và công nghệ.
        Machine learning và deep learning là những công nghệ tiên tiến nhất hiện nay.
        Các nhà khoa học đang phát triển các thuật toán mới để cải thiện độ chính xác.
        Công nghệ blockchain cũng đang được nghiên cứu rộng rãi trong cộng đồng khoa học.
        Điện toán đám mây giúp xử lý dữ liệu lớn hiệu quả hơn cho các nghiên cứu khoa học.
        Nghiên cứu về Internet vạn vật kết hợp với trí tuệ nhân tạo đang phát triển.
        Các công nghệ mới đang được áp dụng trong nhiều lĩnh vực khoa học khác nhau.
        """,
        """
        Nghiên cứu về khoa học dữ liệu đang phát triển nhanh chóng với công nghệ mới.
        Các công nghệ tiên tiến như quantum computing đang được khám phá trong nghiên cứu khoa học.
        Trí tuệ nhân tạo giúp tự động hóa nhiều quy trình nghiên cứu khoa học.
        Internet vạn vật (IoT) kết nối các thiết bị thông minh phục vụ nghiên cứu.
        Công nghệ 5G mang lại tốc độ truyền tải cao hơn cho hệ thống khoa học.
        Các nhà khoa học đang sử dụng công nghệ AI để phân tích dữ liệu phức tạp.
        Nghiên cứu về công nghệ sinh học cũng được hưởng lợi từ AI và khoa học dữ liệu.
        """
    ]

    # Encode to base64
    encoded = []
    for text in sample_texts:
        encoded.append(base64.b64encode(text.encode('utf-8')).decode('utf-8'))

    return encoded


def test_with_algorithm(algo_id, algo_name):
    """Test với một thuật toán cụ thể"""
    print(f"\n{'='*60}")
    print(f"TEST VỚI THUẬT TOÁN: {algo_name} (ID={algo_id})")
    print(f"{'='*60}")

    encoded_texts = encode_sample_text()

    payload = {
        "user_id": f"test_user_{algo_id}",
        "sumary_id": f"test_summary_topic_{algo_id}",
        "original_doc_ids": ["doc_001", "doc_002"],
        "documents": [
            {
                "documents_id": "doc_001",
                "raw_text": encoded_texts[0],
                "file_type": 0,
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
                    ["khoa học", "công nghệ"],
                    []
                ],
                "topic_id": 120,
                "id_mapAlgTypeAI": algo_id
            }
        ],
        "id_mapAlgTypeAI": [],
        "percent_output": 0.1,
        "is_single": False
    }

    print(f"📤 Payload:")
    print(f"   - Số documents: {len(payload['documents'])}")
    print(f"   - Topic ID: {payload['topic'][0]['topic_id']}")
    print(f"   - Keywords: {payload['topic'][0]['keywords']}")
    print(f"   - Algorithm ID: {algo_id} ({algo_name})")
    print(f"   - Percent output: {payload['percent_output']}")

    try:
        # Gửi đến algo-control endpoint
        print(f"\n🔄 Đang gửi request đến algo-control...")
        response = requests.post(
            f"{ALGO_CONTROL_URL}/get_sum",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=120
        )

        print(f"📥 Status: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print(f"✓ Success!")
            print(f"\n📊 Response:")
            print(json.dumps(result, indent=2, ensure_ascii=False)[:500])

            # Kiểm tra có summary không
            if 'summary' in result or 'result' in result:
                print(f"\n✓ Đã nhận được kết quả tóm tắt!")

            return True
        else:
            print(f"✗ Error: {response.text[:200]}")
            return False

    except requests.exceptions.Timeout:
        print(f"⏱️  Timeout - Xử lý quá lâu (>120s)")
        return False
    except Exception as e:
        print(f"✗ Exception: {str(e)}")
        return False


def main():
    print("\n" + "="*60)
    print("  TEST TỰ ĐỘNG - THUẬT TOÁN MULTI VỚI TOPIC")
    print("="*60)

    # Danh sách thuật toán multi để test
    algorithms = [
        {"id": 23, "name": "MultiTexRank"},
        {"id": 24, "name": "MultiLexRank"},
        {"id": 25, "name": "MultiLSA"},
    ]

    # Nếu user muốn test thuật toán cụ thể
    if len(sys.argv) > 1:
        try:
            algo_id = int(sys.argv[1])
            algo_name = sys.argv[2] if len(sys.argv) > 2 else f"Algorithm_{algo_id}"
            algorithms = [{"id": algo_id, "name": algo_name}]
        except ValueError:
            print("Usage: python test_multi_topic_auto.py [algo_id] [algo_name]")
            return

    # Test từng thuật toán
    results = []
    for algo in algorithms:
        success = test_with_algorithm(algo["id"], algo["name"])
        results.append({
            "algorithm": algo["name"],
            "id": algo["id"],
            "success": success
        })

    # Tổng kết
    print(f"\n{'='*60}")
    print("TỔNG KẾT KẾT QUẢ TEST")
    print(f"{'='*60}")

    for result in results:
        status = "✓ PASS" if result["success"] else "✗ FAIL"
        print(f"{result['algorithm']:20s} (ID={result['id']:2d}): {status}")

    print(f"\n💡 Lưu ý:")
    print(f"   - Để test thuật toán khác: python test_multi_topic_auto.py <algo_id> <name>")
    print(f"   - Ví dụ: python test_multi_topic_auto.py 17 HiMap")
    print(f"   - Xem logs: docker compose logs -f multi-kafka")
    print(f"   - Kafka UI: http://localhost:8080")
    print()


if __name__ == "__main__":
    main()
