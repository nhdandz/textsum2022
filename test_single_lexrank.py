#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script test thuật toán Single LexRank
"""

from kafka import KafkaProducer
import json
import base64
import time

# Configuration
KAFKA_BOOTSTRAP = 'localhost:9092'
KAFKA_INPUT_TOPIC = 'topic_input_ai'

def create_producer():
    """Tạo Kafka producer"""
    return KafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP,
        max_request_size=100000000,
        value_serializer=lambda x: json.dumps(x).encode('utf-8')
    )

def test_single_lexrank():
    """Test LexRank với single document"""
    print("="*70)
    print("TEST SINGLE LEXRANK")
    print("="*70)
    
    # Sample text
    sample_text = """
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
    """
    
    # Encode to base64
    encoded_text = base64.b64encode(sample_text.encode('utf-8')).decode('utf-8')
    
    # Tạo payload với single document
    payload = {
        "user_id": f"test_user_single_{int(time.time())}",
        "sumary_id": f"test_summary_single_lexrank_{int(time.time())}",
        "original_doc_ids": ["doc_single_001"],
        "documents": [
            {
                "documents_id": "doc_single_001",
                "raw_text": encoded_text,
                "file_type": 0,  # 0 = text
                "page_from": 0,
                "page_to": 9999
            }
        ],
        "id_mapAlgTypeAI": [2],  # 2 = LexRank for single doc
        "percent_output": 0.3,
        "is_single": True  # QUAN TRỌNG: True để gửi đến single_root
    }
    
    print(f"\n📋 PAYLOAD:")
    print(f"   User ID:        {payload['user_id']}")
    print(f"   Summary ID:     {payload['sumary_id']}")
    print(f"   Số documents:   {len(payload['documents'])}")
    print(f"   Algorithm ID:   2 (Single LexRank)")
    print(f"   Percent output: {payload['percent_output']}")
    print(f"   Is single:      {payload['is_single']}")
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
        print("   1. Xem logs root-kafka:")
        print("      docker compose logs -f root-kafka")
        print()
        print("   2. Xem logs single-kafka:")
        print("      docker compose logs -f single-kafka")
        print()
        print("   3. Xem logs thuật toán LexRank:")
        print("      docker compose logs -f lexrank")
        print()
        print("   4. Kafka UI:")
        print("      http://localhost:8080")
        print()
        print("   5. Kiểm tra output topic:")
        print(f"      python3 check_kafka_output.py {payload['sumary_id']}")
        print()
        
        return True
        
    except Exception as e:
        print(f"✗ LỖI: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_single_lexrank()
