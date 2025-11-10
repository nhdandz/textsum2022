#!/usr/bin/env python3
import json
from kafka import KafkaProducer

# Test message với id_mapAlgTypeAI = 7 (Single Ollama)
test_message = {
    "user_id": "test_user",
    "sumary_id": "test_999",
    "original_doc_ids": ["doc_001"],
    "id_mapAlgTypeAI": [7],  # ID 7 should route to Single Ollama
    "topic": [],
    "percent_output": 0.3,
    "documents": [{
        "documents_id": "doc_001",
        "raw_text": "Đây là văn bản test để kiểm tra routing đến Ollama. Ollama là một công cụ AI mạnh mẽ. Nó có thể tóm tắt văn bản rất tốt. Chúng ta đang test xem message có được route đúng không.",
        "file_type": "txt",
        "page_from": None,
        "page_to": None
    }]
}

producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda x: json.dumps(x).encode('utf-8')
)

print("Sending test message to 'single_root' topic...")
print(f"id_mapAlgTypeAI: {test_message['id_mapAlgTypeAI']}")
print(f"sumary_id: {test_message['sumary_id']}")

future = producer.send('single_root', test_message)
result = future.get(timeout=10)

print(f"✅ Message sent successfully!")
print(f"   Partition: {result.partition}, Offset: {result.offset}")
print("\nNow check logs:")
print("  docker compose logs --tail=20 single-kafka")
print("  docker compose logs --tail=20 ollama-service")

producer.close()
