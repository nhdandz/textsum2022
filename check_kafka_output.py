#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script để kiểm tra kết quả từ Kafka output topic
"""

from kafka import KafkaConsumer
import json
import sys
from datetime import datetime

# Configuration
KAFKA_BOOTSTRAP = 'localhost:9092'
KAFKA_OUTPUT_TOPIC = 'output_topic'


def check_output(summary_id=None, timeout_seconds=60):
    """Kiểm tra output từ Kafka"""
    print(f"\n{'='*70}")
    print("KIỂM TRA KẾT QUẢ TỪ KAFKA OUTPUT")
    print(f"{'='*70}\n")

    print(f"🔌 Đang kết nối Kafka consumer...")
    print(f"   Topic: {KAFKA_OUTPUT_TOPIC}")
    print(f"   Bootstrap: {KAFKA_BOOTSTRAP}")
    if summary_id:
        print(f"   Lọc theo Summary ID: {summary_id}")
    print(f"   Timeout: {timeout_seconds}s")
    print()

    try:
        consumer = KafkaConsumer(
            KAFKA_OUTPUT_TOPIC,
            bootstrap_servers=KAFKA_BOOTSTRAP,
            auto_offset_reset='earliest',  # Đọc từ đầu
            enable_auto_commit=False,
            value_deserializer=lambda x: json.loads(x.decode('utf-8')),
            consumer_timeout_ms=timeout_seconds * 1000
        )

        print("✓ Đã kết nối consumer")
        print(f"⏳ Đang lắng nghe messages...\n")

        found_count = 0
        target_found = False

        for message in consumer:
            found_count += 1
            data = message.value

            # Extract summary_id from data
            msg_summary_id = data.get('sumary_id') or data.get('summary_id')

            # Kiểm tra có match với summary_id cần tìm không
            is_target = (summary_id is None) or (msg_summary_id == summary_id)

            if is_target:
                target_found = True
                print(f"{'='*70}")
                print(f"✓ TÌM THẤY KẾT QUẢ #{found_count}")
                print(f"{'='*70}")
                print(f"Offset:      {message.offset}")
                print(f"Partition:   {message.partition}")
                print(f"Timestamp:   {datetime.fromtimestamp(message.timestamp/1000)}")
                print(f"Summary ID:  {msg_summary_id}")
                print()

                # Hiển thị payload
                print("📊 PAYLOAD:")
                print(json.dumps(data, indent=2, ensure_ascii=False)[:1000])

                if len(json.dumps(data)) > 1000:
                    print(f"\n... (truncated, total {len(json.dumps(data))} chars)")

                print()

                # Nếu tìm theo summary_id cụ thể thì dừng sau khi tìm thấy
                if summary_id:
                    print("✓ Đã tìm thấy kết quả cần tìm!")
                    break
            else:
                # Chỉ hiển thị thông tin ngắn gọn
                print(f"⏩ Message #{found_count}: {msg_summary_id} (skipped)")

        consumer.close()

        print()
        print(f"{'='*70}")
        print(f"TỔNG KẾT")
        print(f"{'='*70}")
        print(f"Tổng số messages đọc được: {found_count}")

        if summary_id:
            if target_found:
                print(f"✓ Đã tìm thấy kết quả cho Summary ID: {summary_id}")
            else:
                print(f"✗ KHÔNG tìm thấy kết quả cho Summary ID: {summary_id}")
                print(f"\n💡 GỢI Ý:")
                print(f"   1. Kiểm tra logs: docker compose logs -f multi-kafka")
                print(f"   2. Có thể xử lý đang chạy, hãy đợi thêm và thử lại")
                print(f"   3. Kiểm tra lỗi: docker compose logs -f m-textrank m-lexrank m-lsa")
        print()

    except Exception as e:
        print(f"\n✗ LỖI: {str(e)}")
        import traceback
        traceback.print_exc()


def listen_continuously():
    """Lắng nghe liên tục tất cả messages"""
    print(f"\n{'='*70}")
    print("LẮNG NGHE LIÊN TỤC KAFKA OUTPUT")
    print(f"{'='*70}\n")

    print("🔌 Đang kết nối Kafka consumer...")
    print(f"   Topic: {KAFKA_OUTPUT_TOPIC}")
    print(f"   Mode: Continuous (Ctrl+C để dừng)")
    print()

    try:
        consumer = KafkaConsumer(
            KAFKA_OUTPUT_TOPIC,
            bootstrap_servers=KAFKA_BOOTSTRAP,
            auto_offset_reset='latest',  # Chỉ đọc message mới
            enable_auto_commit=True,
            value_deserializer=lambda x: json.loads(x.decode('utf-8'))
        )

        print("✓ Đang lắng nghe... (Nhấn Ctrl+C để dừng)\n")

        count = 0
        for message in consumer:
            count += 1
            data = message.value
            summary_id = data.get('sumary_id') or data.get('summary_id')

            print(f"{'─'*70}")
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Message #{count}")
            print(f"Summary ID: {summary_id}")
            print(f"Offset: {message.offset}, Partition: {message.partition}")
            print()

            # Hiển thị một phần data
            summary_text = data.get('summary') or data.get('result') or data.get('text')
            if summary_text:
                preview = str(summary_text)[:200]
                print(f"Summary: {preview}...")
            print()

    except KeyboardInterrupt:
        print("\n✓ Đã dừng lắng nghe")
    except Exception as e:
        print(f"\n✗ LỖI: {str(e)}")
        import traceback
        traceback.print_exc()


def main():
    print("\n" + "="*70)
    print("  KAFKA OUTPUT CHECKER")
    print("="*70)

    if len(sys.argv) > 1:
        if sys.argv[1] == "--listen":
            # Mode lắng nghe liên tục
            listen_continuously()
        else:
            # Tìm theo summary_id
            summary_id = sys.argv[1]
            timeout = int(sys.argv[2]) if len(sys.argv) > 2 else 60
            check_output(summary_id, timeout)
    else:
        # Hiển thị tất cả messages gần đây
        print("\n💡 CÁCH SỬ DỤNG:")
        print("   python3 check_kafka_output.py <summary_id>           # Tìm theo ID")
        print("   python3 check_kafka_output.py <summary_id> <timeout> # Tìm với timeout")
        print("   python3 check_kafka_output.py --listen               # Lắng nghe liên tục")
        print()
        print("Đang hiển thị tất cả messages gần đây...\n")
        check_output(None, 10)


if __name__ == "__main__":
    main()
