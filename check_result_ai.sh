#!/bin/bash
# Script kiểm tra kết quả cuối cùng từ topic result_ai

SUMMARY_ID=${1:-"306"}

echo "=================================================="
echo "KIỂM TRA KẾT QUẢ CUỐI CÙNG TỪ TOPIC result_ai"
echo "=================================================="
echo ""
echo "Summary ID: $SUMMARY_ID"
echo ""

docker compose exec multi-kafka python3 << EOF
from kafka import KafkaConsumer
import json

consumer = KafkaConsumer(
    'result_ai',
    bootstrap_servers=['kafka-1:9092'],
    auto_offset_reset='earliest',
    value_deserializer=lambda x: json.loads(x.decode('utf-8')),
    consumer_timeout_ms=10000
)

print("🔍 Đang tìm kết quả cho sumary_id: $SUMMARY_ID...\n")

found = False
for msg in consumer:
    data = msg.value
    if str(data.get('sumary_id')) == '$SUMMARY_ID':
        print("✅ TÌM THẤY KẾT QUẢ!")
        print("="*60)
        print(json.dumps(data, indent=2, ensure_ascii=False))
        print("="*60)
        found = True
        break

if not found:
    print("❌ KHÔNG tìm thấy kết quả trong result_ai topic")
    print("\n💡 GỢI Ý:")
    print("   1. Xem logs: docker compose logs -f m-lexrank")
    print("   2. Kiểm tra văn bản có đủ dài không")
    print("   3. Đợi thêm và thử lại")

consumer.close()
EOF
