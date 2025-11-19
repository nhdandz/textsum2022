# PHÂN TÍCH CHI TIẾT: XỬ LÝ MESSAGE CÓ CHỦ ĐỀ (TOPIC)

## 📋 TỔNG QUAN WORKFLOW

File: [modules/root_kafka/multi_kafka.py](modules/root_kafka/multi_kafka.py)

```python
# Dòng 96-136: Xử lý message có topic
else: # topic
    # Bước 1: Convert base64 documents → text
    list_doc, list_doc_id = helper_multi.convert_b64_file_to_text(message)

    # Bước 2: Lặp qua từng topic
    topics = message["topic"]
    for idx, top in enumerate(topics):
        # Bước 3: Lọc văn bản theo keywords
        list_text_valid, elem_arr_valid = helper_multi.cluster_topics(list_doc, top["keywords"])

        # Bước 4: Lấy thông tin thuật toán
        id_mapAlgTypeAI = top["id_mapAlgTypeAI"]
        topic_name = init.topics[str(id_mapAlgTypeAI)]["topic_name"]
        algo_id = init.topics[str(id_mapAlgTypeAI)]["algo_id"]

        # Bước 5: Tạo message output
        data_format = {
            "user_id": message["user_id"],
            "sumary_id": message["sumary_id"],
            "topic": [{
                "list_doc": list_text_valid,  # ← Văn bản đã lọc
                "list_doc_id": [list_doc_id[x] for x in elem_arr_valid],
                "topic_id": top["topic_id"],
                "algo_id": algo_id,
                "percent_output": message["percent_output"]
            }],
            "original_doc_ids": message["original_doc_ids"],
            "is_single": False,
            "is_topic": True,
            "cluster": {},
            "is_cluster": False
        }

        # Bước 6: Gửi đến thuật toán
        producer.send(topic_name, data_format)
```

---

## 🔍 PHÂN TÍCH CHI TIẾT TỪNG BƯỚC

### BƯỚC 1: Convert Documents → Text

**File**: `helper_multi.py`, dòng 181-193

```python
def convert_b64_file_to_text(dataInput):
    documents = dataInput["documents"]
    list_doc = []
    list_doc_id = []
    for doc in documents:
        data_file = doc["raw_text"]        # Base64 string
        file_type = int(doc["file_type"])  # 0=txt, 1=pdf, 2=docx, 3=doc
        doc_id = doc["documents_id"]

        # Giải mã và extract text
        r_text = base_64.get_raw_text(data_file, file_type, 0, 99999)
        list_doc.append(r_text)
        list_doc_id.append(doc_id)

    return list_doc, list_doc_id
```

**Input**:
```json
{
  "documents": [
    {
      "documents_id": "doc1",
      "raw_text": "VGhpcyBpcyBhIHRlc3Q=",  // base64
      "file_type": 0
    }
  ]
}
```

**Output**:
```python
list_doc = ["This is a test"]
list_doc_id = ["doc1"]
```

---

### BƯỚC 2: Lặp Qua Từng Topic

```python
topics = message["topic"]  # Mảng các topic
for idx, top in enumerate(topics):
    # Xử lý từng topic riêng biệt
```

**Ví dụ**: Nếu có 2 topics
```json
{
  "topic": [
    {
      "keywords": [["khoa học", "công nghệ"], []],
      "topic_id": 120,
      "id_mapAlgTypeAI": 23
    },
    {
      "keywords": [["y tế", "sức khỏe"], []],
      "topic_id": 121,
      "id_mapAlgTypeAI": 24
    }
  ]
}
```

→ Sẽ gửi **2 messages riêng biệt** đến 2 thuật toán khác nhau

---

### BƯỚC 3: Lọc Văn Bản Theo Keywords ⭐ QUAN TRỌNG NHẤT

**File**: `helper_multi.py`, dòng 137-146 và 227-268

#### 3.1. Hàm `cluster_topics()`

```python
def cluster_topics(list_doc, logic):
    """
    Lọc từng document theo keywords
    """
    elem_arr_valid = []  # Index các doc hợp lệ
    list_text_valid = [] # Text sau khi lọc

    for jdx, doc in enumerate(list_doc):
        # Lọc từng document
        text_input = get_raw_text_by_topic(logic, doc)

        if text_input != "":  # Nếu còn text sau khi lọc
            elem_arr_valid.append(jdx)
            list_text_valid.append(text_input)

    return list_text_valid, elem_arr_valid
```

#### 3.2. Hàm `get_raw_text_by_topic()` - LOGIC CHÍNH

```python
def get_raw_text_by_topic(topics, raw_text):
    """
    Logic lọc văn bản theo keywords

    Args:
        topics: [["AND keywords"], ["NOT keywords"]]
        raw_text: Văn bản đầy đủ

    Returns:
        Văn bản đã lọc (chỉ các đoạn match keywords)
    """

    # BƯỚC 3.2.1: Split văn bản thành paragraphs
    list_pragrab = raw_text.split('\n')
    list_raw = []
    topic_choose = topics[0]  # AND keywords
    topic_not = topics[1]      # NOT keywords

    # BƯỚC 3.2.2: LỌC THEO AND LOGIC
    if len(topic_choose) != 0:
        for key_words in topic_choose:
            key_word = key_words.split(',')  # Split by comma

            for pragrab in list_pragrab:
                is_choose = True

                # Kiểm tra TẤT CẢ keywords phải có trong paragraph
                for word in key_word:
                    if word.lower() not in pragrab.lower():
                        is_choose = False  # Thiếu 1 keyword → bỏ

                if is_choose == True:
                    index = list_pragrab.index(pragrab)
                    list_raw.append((index, pragrab))
    else:
        # Nếu không có AND keywords → lấy tất cả
        count = 0
        for pragrab in list_pragrab:
            list_raw.append((count, pragrab))
            count += 1

    # BƯỚC 3.2.3: Remove duplicates và sort
    list_raw = removeDuplicates(list_raw)
    list_raw_process = sorted(list_raw, key=lambda tup: tup[0])

    # BƯỚC 3.2.4: LỌC THEO NOT LOGIC
    list_raw_final = []
    if len(topic_not) != 0:
        for key_words in topic_not:
            key_word = key_words.split(',')

            for pragrab in list_raw_process:
                is_choose = True

                # Kiểm tra KHÔNG chứa bất kỳ NOT keyword nào
                for word in key_word:
                    if ' ' + word.strip().lower() + ' ' in pragrab[1].lower():
                        is_choose = False  # Có NOT keyword → bỏ

                if is_choose == True:
                    list_raw_final.append(pragrab)
    else:
        list_raw_final = list_raw_process

    # BƯỚC 3.2.5: Final cleanup và join
    list_raw_final = removeDuplicates(list_raw_final)
    list_raw_final_process = sorted(list_raw_final, key=lambda tup: tup[0])

    list_text_topic = []
    for text_topic in list_raw_final_process:
        list_text_topic.append(text_topic[1])

    return '\n'.join(list_text_topic)
```

---

## 📊 VÍ DỤ CỤ THỂ

### Input Payload

```json
{
  "user_id": "user123",
  "sumary_id": 306,
  "documents": [
    {
      "documents_id": "doc1",
      "raw_text": "base64_encoded_text",
      "file_type": 0
    }
  ],
  "topic": [{
    "keywords": [["khoa học", "công nghệ"], []],
    "topic_id": 120,
    "id_mapAlgTypeAI": 24
  }]
}
```

### Văn bản sau decode (doc1)

```
Trí tuệ nhân tạo đang phát triển.
Nghiên cứu khoa học và công nghệ tiến bộ nhanh.
Dự án dược liệu quý được đầu tư.
Công nghệ blockchain là xu hướng mới.
Y học hiện đại sử dụng AI.
Khoa học dữ liệu kết hợp công nghệ máy học.
```

### Quá trình lọc

#### Bước 1: Split thành paragraphs
```python
[
  "Trí tuệ nhân tạo đang phát triển.",
  "Nghiên cứu khoa học và công nghệ tiến bộ nhanh.",
  "Dự án dược liệu quý được đầu tư.",
  "Công nghệ blockchain là xu hướng mới.",
  "Y học hiện đại sử dụng AI.",
  "Khoa học dữ liệu kết hợp công nghệ máy học."
]
```

#### Bước 2: Lọc theo AND keywords `["khoa học", "công nghệ"]`

- Paragraph 1: ❌ Không có "khoa học"
- Paragraph 2: ✅ Có cả "khoa học" VÀ "công nghệ"
- Paragraph 3: ❌ Không có cả hai
- Paragraph 4: ❌ Chỉ có "công nghệ"
- Paragraph 5: ❌ Không có cả hai
- Paragraph 6: ✅ Có cả "khoa học" VÀ "công nghệ"

**Kết quả sau lọc AND**:
```python
[
  (1, "Nghiên cứu khoa học và công nghệ tiến bộ nhanh."),
  (5, "Khoa học dữ liệu kết hợp công nghệ máy học.")
]
```

#### Bước 3: Lọc theo NOT keywords `[]` (empty)

Không có NOT keywords → Giữ nguyên

#### Bước 4: Join lại

**Output cuối cùng**:
```
Nghiên cứu khoa học và công nghệ tiến bộ nhanh.
Khoa học dữ liệu kết hợp công nghệ máy học.
```

---

## ⚠️ VẤN ĐỀ TRONG CASE CỦA BẠN

### Input keywords
```json
{
  "keywords": [["khoa học", "công nghệ"], []]
}
```

### Văn bản gốc (sau decode)
```
... nhiều đoạn về dược liệu ...
Dự án dược liệu quý: bao gồm: (i). Dự án phát triển vùng trồng dược liệu quý (Dự án vùng trồng dược liệu quý) ; (ii). Dự án Trung tâm nhân giống, bảo tồn và phát triển dược liệu ứng dụng công nghệ cao (Dự án Trung tâm nhân giống).
... nhiều đoạn khác ...
```

### Vấn đề

**Chỉ có 1 câu duy nhất** chứa CẢ HAI từ "khoa học" VÀ "công nghệ":
- Từ "công nghệ" xuất hiện trong: "ứng dụng **công nghệ** cao"
- Từ "khoa học"... **KHÔNG TÌM THẤY** trong văn bản!

❌ **Kết quả**: Sau khi lọc chỉ còn 1 câu (hoặc thậm chí 0 câu nếu không có "khoa học")

---

## 🎯 LOGIC KEYWORDS CHI TIẾT

### Cú pháp Keywords

```json
{
  "keywords": [
    ["AND_keyword1", "AND_keyword2"],  // Mảng thứ 1: AND logic
    ["NOT_keyword1", "NOT_keyword2"]   // Mảng thứ 2: NOT logic
  ]
}
```

### Quy tắc lọc

#### AND Logic (keywords[0])
```python
# TẤT CẢ keywords phải có trong CÙNG 1 paragraph

# Ví dụ 1: ["khoa học", "công nghệ"]
paragraph = "Nghiên cứu khoa học và công nghệ"
→ ✅ Match (có cả 2)

paragraph = "Khoa học dữ liệu rất quan trọng"
→ ❌ Không match (chỉ có "khoa học")

# Ví dụ 2: ["AI,machine learning"]  # Note: dấu phẩy = AND
paragraph = "AI và machine learning"
→ ✅ Match (có cả 2)
```

#### NOT Logic (keywords[1])
```python
# Loại bỏ paragraphs chứa BẤT KỲ NOT keyword nào

# Ví dụ: ["deprecated", "obsolete"]
paragraph = "This API is deprecated"
→ ❌ Loại bỏ (chứa "deprecated")

paragraph = "This is a new API"
→ ✅ Giữ lại (không chứa NOT keywords)
```

#### Kết hợp AND + NOT
```python
keywords = [["python", "programming"], ["deprecated"]]

paragraph = "Python programming tutorial"
→ ✅ PASS (có python + programming, không có deprecated)

paragraph = "Python programming (deprecated)"
→ ❌ FAIL (có deprecated)

paragraph = "Python is great"
→ ❌ FAIL (không có "programming")
```

---

## 🐛 DEBUG: TẠI SAO CHỈ CÒN 1 CÂU?

### Kiểm tra văn bản gốc

```bash
docker compose exec multi-kafka python3 << 'EOF'
# Đọc văn bản từ message log
text = """
... paste văn bản gốc ở đây ...
"""

keywords = [["khoa học", "công nghệ"], []]

# Test từng paragraph
for i, para in enumerate(text.split('\n')):
    has_all = all(kw.lower() in para.lower() for kw in ["khoa học", "công nghệ"])
    print(f"{i}: {has_all} - {para[:60]}...")
EOF
```

### Logs multi-kafka có thông tin

```bash
docker compose logs multi-kafka | grep "list_doc"
```

Bạn sẽ thấy:
```json
{
  "list_doc": ["Dự án dược liệu quý..."],  // ← Chỉ 1 câu!
  ...
}
```

---

## ✅ GIẢI PHÁP

### 1. Nới lỏng keywords (Khuyến nghị)

```json
// Thay vì yêu cầu CẢ HAI
{
  "keywords": [["khoa học", "công nghệ"], []]
}

// Chỉ yêu cầu 1 trong 2
{
  "keywords": [["công nghệ"], []]
}
// HOẶC
{
  "keywords": [["khoa học"], []]
}
```

### 2. Thêm nhiều documents hơn

```json
{
  "documents": [
    { "documents_id": "doc1", ... },
    { "documents_id": "doc2", ... },
    { "documents_id": "doc3", ... },
    { "documents_id": "doc4", ... }
    // ← Tăng từ 2 lên 4-5 documents
  ]
}
```

### 3. Kiểm tra nội dung documents trước

```python
# Test xem có bao nhiêu paragraphs match
from modules.root_kafka.helper_multi import get_raw_text_by_topic

text = """... văn bản đầy đủ ..."""
keywords = [["khoa học", "công nghệ"], []]

result = get_raw_text_by_topic(keywords, text)
print(f"Số paragraphs sau lọc: {len(result.split(chr(10)))}")
print(f"Văn bản sau lọc:\n{result}")
```

---

## 📝 TÓM TẮT WORKFLOW

```
INPUT MESSAGE
├─ documents: [doc1, doc2, ...]
└─ topic: [{keywords, id_mapAlgTypeAI}]

     ↓

BƯỚC 1: convert_b64_file_to_text()
├─ Decode base64
├─ Extract text từ PDF/DOCX
└─ Output: list_doc = ["text1", "text2", ...]

     ↓

BƯỚC 2: cluster_topics()
├─ Lặp qua từng document
└─ Gọi get_raw_text_by_topic() cho từng doc

     ↓

BƯỚC 3: get_raw_text_by_topic()  ← LOGIC CHÍNH
├─ Split văn bản thành paragraphs (by \n)
├─ Lọc AND: Giữ paragraphs có ĐỦ keywords[0]
├─ Lọc NOT: Bỏ paragraphs có keywords[1]
└─ Join lại thành text

     ↓

BƯỚC 4: Tạo message output
└─ list_doc: [văn bản đã lọc]  ← Có thể rất ngắn!

     ↓

BƯỚC 5: Gửi đến thuật toán
└─ producer.send(topic_name, data_format)
```

---

## 🔧 CODE QUAN TRỌNG NHẤT

**File**: `modules/root_kafka/helper_multi.py:227-268`

```python
def get_raw_text_by_topic(topics, raw_text):
    # Đây là hàm quyết định văn bản nào được giữ lại!
    # Logic:
    # 1. Split by \n
    # 2. Lọc theo AND (topics[0])
    # 3. Lọc theo NOT (topics[1])
    # 4. Join lại
    ...
    return '\n'.join(list_text_topic)
```

**Vấn đề**: Nếu ít paragraphs match → Output ngắn → Không thể tóm tắt!

---

**KẾT LUẬN**: Code lọc theo keywords **RẤT STRICT**, yêu cầu TẤT CẢ keywords phải có trong CÙNG MỘT paragraph. Trong case của bạn, rất ít (hoặc chỉ 1) paragraph thỏa mãn điều kiện → Văn bản sau lọc quá ngắn.
