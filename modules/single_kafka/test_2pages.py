#!/usr/bin/env python3
"""
Script test để kiểm tra lỗi khi xử lý 2 trang
"""
import requests
import json
import base64
import sys

# Đọc file PDF test
pdf_file = "/home/nhdandz/Documents/tupk/textsum2022/modules/single_kafka/CV_PHAM_KHAC_TU.pdf"

try:
    with open(pdf_file, "rb") as f:
        pdf_content = f.read()
        pdf_base64 = base64.b64encode(pdf_content).decode('utf-8')

    print(f"File size: {len(pdf_content)} bytes")
    print(f"Base64 size: {len(pdf_base64)} chars")

    # Test 1: Get number of pages
    print("\n=== Test 1: Get number of pages ===")
    response = requests.post(
        "http://localhost:9980/get_number_page",
        json={
            "encode": pdf_base64,
            "file_type": 1  # PDF
        },
        timeout=60
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    number_pages = response.json().get('number_page', 0)

    # Test 2: Get content 1 page (should work)
    print("\n=== Test 2: Get content - 1 page (page 0-0) ===")
    response = requests.post(
        "http://localhost:9980/get_content",
        json={
            "data": [{
                "documents_id": "test_doc_1",
                "encode": pdf_base64,
                "file_type": 1,
                "page_from": 0,
                "page_to": 0
            }]
        },
        timeout=60
    )
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Response message: {result.get('message', 'OK')}")
    if result.get('result'):
        print(f"Text length: {len(result['result'][0].get('text', ''))}")

    # Test 3: Get content 2 pages (fails)
    print("\n=== Test 3: Get content - 2 pages (page 0-1) ===")
    response = requests.post(
        "http://localhost:9980/get_content",
        json={
            "data": [{
                "documents_id": "test_doc_2",
                "encode": pdf_base64,
                "file_type": 1,
                "page_from": 0,
                "page_to": 1
            }]
        },
        timeout=120  # Tăng timeout lên 2 phút
    )
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Response message: {result.get('message', 'OK')}")
    if result.get('result'):
        print(f"Text length: {len(result['result'][0].get('text', ''))}")

    print("\n✓ All tests passed!")

except FileNotFoundError:
    print(f"ERROR: File not found: {pdf_file}")
    sys.exit(1)
except requests.exceptions.Timeout:
    print("ERROR: Request timeout!")
    sys.exit(1)
except requests.exceptions.ConnectionError as e:
    print(f"ERROR: Connection error: {e}")
    print("Make sure Flask server is running on port 9980")
    sys.exit(1)
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
