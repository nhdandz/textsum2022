#!/usr/bin/env python3
"""
Test routing mechanism from id_mapAI to Kafka topics
"""

import requests
import json

ALGO_CONTROL_URL = "http://192.168.210.42:6789"

def test_routing(id_mapAI):
    """Test get_detail_algo API"""
    url = f"{ALGO_CONTROL_URL}/get_detail_algo"

    response = requests.post(url, json={"id_mapAI": id_mapAI})

    if response.status_code == 200:
        data = response.json()
        topic = data.get("topic")
        algo_id = data.get("algo_id")
        return topic, algo_id
    else:
        return None, None

def main():
    print("=" * 80)
    print("🔍 TESTING ROUTING MECHANISM")
    print("=" * 80)

    print(f"\n📡 Algorithm Control API: {ALGO_CONTROL_URL}")
    print(f"\n{'ID':<6} {'AlgoID':<10} {'Topic':<30} {'Status'}")
    print("-" * 80)

    # Test cases for Ollama services
    test_cases = [
        (32, 32, "7_single_ollama", "Single Ollama"),
        (33, 33, "33_multi_ollama", "Multi Ollama"),
        (7, 7, "7_single_bigbirdarvix", "BigBird Arxiv"),
        (13, 13, "1_single_lexrank", "LexRank"),
        (14, 14, "2_single_textrank", "TextRank"),
    ]

    for id_mapAI, expected_algo_id, expected_topic, description in test_cases:
        topic, algo_id = test_routing(id_mapAI)

        if topic and algo_id:
            status = "✅" if (topic == expected_topic and algo_id == expected_algo_id) else "⚠️"
            print(f"{id_mapAI:<6} {algo_id:<10} {topic:<30} {status} {description}")
        else:
            print(f"{id_mapAI:<6} {'N/A':<10} {'NOT FOUND':<30} ❌ {description}")

    print("-" * 80)

    # Detailed test for Ollama
    print("\n" + "=" * 80)
    print("📊 DETAILED OLLAMA ROUTING TEST")
    print("=" * 80)

    print("\n🔹 Single Document Ollama (ID 32):")
    topic, algo_id = test_routing(32)
    if topic:
        print(f"   ✅ id_mapAI: 32")
        print(f"   ✅ algorId: {algo_id}")
        print(f"   ✅ Topic: {topic}")
        print(f"   ✅ Service: ollama-service")
        print(f"\n   Flow: topic_input_ai → single_root → {topic} → ollama-service")
    else:
        print(f"   ❌ Routing not configured!")

    print("\n🔹 Multi Document Ollama (ID 33):")
    topic, algo_id = test_routing(33)
    if topic:
        print(f"   ✅ id_mapAI: 33")
        print(f"   ✅ algorId: {algo_id}")
        print(f"   ✅ Topic: {topic}")
        print(f"   ✅ Service: multi-ollama-service")
        print(f"\n   Flow: topic_input_ai → multi_root → {topic} → multi-ollama-service")
    else:
        print(f"   ❌ Routing not configured!")

    print("\n" + "=" * 80)

    # Show mapping explanation
    print("\n📚 ROUTING MECHANISM EXPLANATION:")
    print("=" * 80)
    print("""
┌─────────────────────────────────────────────────────────────────┐
│ USER REQUEST                                                     │
│ { "id_mapAlgTypeAI": [32], ... }                                │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 1: Backend → Kafka topic_input_ai                          │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 2: root-kafka checks is_single                             │
│   - is_single=true  → send to "single_root"                     │
│   - is_single=false → send to "multi_root"                      │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 3: single-kafka / multi-kafka                              │
│   - Read id_mapAlgTypeAI from message                           │
│   - Call API: /get_detail_algo with id_mapAI                    │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 4: algo-control service                                    │
│   1. Read maptype.json → find algorId by id_mapAI               │
│      Example: id=32 → algorId=32                                │
│                                                                  │
│   2. Read algo.json → find topic by algorId                     │
│      Example: algorId=32 → topic="7_single_ollama"              │
│                                                                  │
│   3. Return: {"topic": "7_single_ollama", "algo_id": 32}        │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 5: single-kafka sends to topic                             │
│   - Send message to Kafka topic: "7_single_ollama"              │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 6: ollama-service consumes and processes                   │
│   - Subscribe to "7_single_ollama"                              │
│   - Call Ollama API for summarization                           │
│   - Send result to "result_ai"                                  │
└─────────────────────────────────────────────────────────────────┘
""")

    print("\n📝 FILES INVOLVED:")
    print("   1. maptype.json  - Maps id_mapAI → algorId")
    print("   2. algo.json     - Maps algorId → topic name")
    print("   3. single_root.py - Reads id_mapAlgTypeAI and routes")
    print("   4. multi_root.py  - Same for multi-document")

    print("\n" + "=" * 80)

if __name__ == "__main__":
    main()
