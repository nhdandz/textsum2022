#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, '/home/nhdandz/Documents/tupk/textsum2022/TextsumCustom/text_process_app')

from helper import get_raw_text

# Base64 encoded PDF "Hello World"
pdf_base64 = "JVBERi0xLjQKJeLjz9MKNCAwIG9iago8PC9UeXBlL0NhdGFsb2cvUGFnZXMgMiAwIFI+PgplbmRvYmoKMiAwIG9iago8PC9UeXBlL1BhZ2VzL0tpZHNbMyAwIFJdL0NvdW50IDE+PgplbmRvYmoKMyAwIG9iago8PC9UeXBlL1BhZ2UvTWVkaWFCb3hbMCAwIDYxMiA3OTJdL1Jlc291cmNlczw8L0ZvbnQ8PC9GMSA1IDAgUj4+Pj4vQ29udGVudHMgNCAwIFI+PgplbmRvYmoKNCAwIG9iago8PC9MZW5ndGggNDQ+PgpzdHJlYW0KQlQKL0YxIDI0IFRmCjEwMCAzMDAgVGQKKEhlbGxvIFdvcmxkKSBUagpFVAplbmRzdHJlYW0KZW5kb2JqCjUgMCBvYmoKPDwvVHlwZS9Gb250L1N1YnR5cGUvVHlwZTEvQmFzZUZvbnQvSGVsdmV0aWNhPj4KZW5kb2JqCnhyZWYKMCA2CjAwMDAwMDAwMDAgNjU1MzUgZiAKMDAwMDAwMDAxNSAwMDAwMCBuIAowMDAwMDAwMDY0IDAwMDAwIG4gCjAwMDAwMDAxMjEgMDAwMDAgbiAKMDAwMDAwMDIyNiAwMDAwMCBuIAowMDAwMDAwMzE5IDAwMDAwIG4gCnRyYWlsZXIKPDwvU2l6ZSA2L1Jvb3QgMSAwIFI+PgpzdGFydHhyZWYKMzg4CiUlRU9GCg=="

# Test extraction
# file_type = 1 means PDF (from helper.py constants)
print("Testing PDF extraction...")
print("Base64 input length:", len(pdf_base64))

try:
    result = get_raw_text(pdf_base64, file_type=1, page_from=0, page_to=5)
    print("\nExtracted text:")
    print(repr(result))
    print("\nText length:", len(result))
    if result:
        print("SUCCESS: Text extracted successfully!")
    else:
        print("PROBLEM: Empty text returned!")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
