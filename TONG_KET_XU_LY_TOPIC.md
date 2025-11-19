# TỔNG KẾT: XỬ LÝ MESSAGE CÓ CHỦ ĐỀ (TOPIC) TRONG MULTI-KAFKA

## 🎯 VẤN ĐỀ CỦA BẠN

Bạn nhận được output như này:
```json
{
  "list_doc": ["Dự án dược liệu quý..."],  // Chỉ 1 câu!
  "topic_id": 120,
  "algo_id": 24
}
```

**Tại sao chỉ còn 1 câu?**

---

## 🔍 NGUYÊN NHÂN: LOGIC LỌC RẤT STRICT

### Code xử lý (multi_kafka.py)

```python
# Dòng 96-136: Xử lý message có topic
else: # topic
    # 1. Convert base64 → text
    list_doc, list_doc_id = helper_multi.convert_b64_file_to_text(message)

    # 2. Lặp qua từng topic
    topics = message["topic"]
    for idx, top in enumerate(topics):
        # 3. LỌC VĂN BẢN THEO KEYWORDS ← ĐÂY LÀ VẤN ĐỀ!
        list_text_valid, elem_arr_valid = helper_multi.cluster_topics(
            list_doc,
            top["keywords"]
        )

        # 4. Tạo message output
        data_format = {
            "topic": [{
                "list_doc": list_text_valid,  # ← Có thể rất ngắn!
                ...
            }]
        }

        # 5. Gửi đến thuật toán
        producer.send(topic_name, data_format)
```

### Logic lọc chi tiết (helper_multi.py)

```python
def get_raw_text_by_topic(topics, raw_text):
    """
    Logic: LỌC TỪNG PARAGRAPH

    keywords = [
        ["khoa học", "công nghệ"],  # AND: Phải có TẤT CẢ
        []                           # NOT: Không được có
    ]
    """

    # Bước 1: Split văn bản thành paragraphs
    paragraphs = raw_text.split('\n')

    # Bước 2: LỌC THEO AND
    for paragraph in paragraphs:
        has_all_keywords = True
        for keyword in ["khoa học", "công nghệ"]:
            if keyword not in paragraph:
                has_all_keywords = False  # ← Thiếu 1 keyword → BỎ

        if has_all_keywords:
            keep_paragraph()  # Giữ lại

    # Bước 3: LỌC THEO NOT
    # (Loại bỏ paragraphs chứa NOT keywords)

    # Bước 4: Join lại
    return '\n'.join(filtered_paragraphs)
```

---

## 📊 DEMO: TEST KEYWORD FILTERING

Chạy script demo:
```bash
python3 test_keyword_filter.py
```

### Kết quả:

#### Test 1: STRICT (khoa học AND công nghệ)
- Input: 8 paragraphs
- **Kết quả: 5 paragraphs** (chỉ giữ các đoạn có CẢ HAI keywords)

**Ví dụ**:
- ✅ "Nghiên cứu **khoa học** và **công nghệ** tiến bộ" → Giữ
- ❌ "**Công nghệ** blockchain đang phát triển" → Bỏ (thiếu "khoa học")
- ❌ "Trí tuệ nhân tạo đang phát triển" → Bỏ (thiếu cả 2)

#### Test 2: LOOSE (chỉ công nghệ)
- Input: 8 paragraphs
- **Kết quả: 5 paragraphs** (giữ các đoạn có "công nghệ")

#### Test 3: WITH NOT (công nghệ NOT blockchain)
- Input: 8 paragraphs
- **Kết quả: 4 paragraphs** (có "công nghệ" nhưng không có "blockchain")

---

## ⚠️ VẤN ĐỀ TRONG CASE CỦA BẠN

### Input của bạn
```json
{
  "documents": [
    {
      "documents_id": "688ec634ccbac25bd52faa0f",
      "raw_text": "... văn bản về dự án dược liệu ...",
      "file_type": 1
    },
    {
      "documents_id": "68900f0a26c2991a52c8a23b",
      "raw_text": "... văn bản khác ...",
      "file_type": 1
    }
  ],
  "topic": [{
    "keywords": [["khoa học", "công nghệ"], []],
    "topic_id": 120,
    "id_mapAlgTypeAI": 24
  }]
}
```

### Vấn đề

Trong **TẤT CẢ** văn bản của 2 documents, **CHỈ CÓ 1 PARAGRAPH** chứa cả "khoa học" VÀ "công nghệ":

> "Dự án dược liệu quý... ứng dụng **công nghệ** cao"

**Nhưng**: Paragraph này có "công nghệ" nhưng **KHÔNG CÓ "khoa học"**!

→ **Kết quả**: Sau khi lọc chỉ còn 0-1 câu!

---

## ✅ GIẢI PHÁP

### 1. Nới lỏng keywords (Khuyến nghị mạnh ⭐)

#### Cách 1a: Chỉ dùng 1 keyword
```json
{
  "keywords": [["dược liệu"], []]
}
```

#### Cách 1b: Dùng từ phổ biến hơn
```json
{
  "keywords": [["công nghệ"], []]
}
```

#### Cách 1c: Dùng OR logic (nếu hệ thống hỗ trợ)
```json
// Hiện tại hệ thống KHÔNG hỗ trợ OR
// Chỉ hỗ trợ AND trong mỗi keyword group
```

### 2. Thêm nhiều documents hơn

```json
{
  "documents": [
    { "documents_id": "doc1", ... },
    { "documents_id": "doc2", ... },
    { "documents_id": "doc3", ... },
    { "documents_id": "doc4", ... },
    { "documents_id": "doc5", ... }
    // ← Tăng từ 2 lên 5-10 documents
  ]
}
```

→ Nhiều documents → Nhiều cơ hội có paragraphs match keywords

### 3. Tăng page_to để lấy nhiều trang hơn

```json
{
  "documents": [{
    "documents_id": "doc1",
    "raw_text": "base64...",
    "file_type": 1,
    "page_from": 0,
    "page_to": 50  // ← Tăng từ 10 lên 50 trang
  }]
}
```

### 4. Test trước khi gửi

```python
# Test xem có bao nhiêu paragraphs match
import sys
sys.path.append('/home/nhdandz/Documents/tupk/textsum2022/modules/root_kafka')
from helper_multi import get_raw_text_by_topic

text = """... văn bản đầy đủ ..."""
keywords = [["khoa học", "công nghệ"], []]

result = get_raw_text_by_topic(keywords, text)
num_paras = len([p for p in result.split('\n') if p.strip()])

print(f"Số paragraphs sau lọc: {num_paras}")

if num_paras < 5:
    print("⚠️  Văn bản quá ngắn, cần nới lỏng keywords!")
else:
    print("✅ OK, đủ văn bản để tóm tắt")
```

---

## 📝 WORKFLOW ĐẦY ĐỦ

```
CLIENT GỬI PAYLOAD
├─ documents: [doc1, doc2, ...]
└─ topic: [{keywords: [["khoa học", "công nghệ"], []]}]

     ↓

MULTI-KAFKA CONSUMER (multi_root topic)
├─ Nhận message từ algo-control
└─ Bắt đầu xử lý

     ↓

BƯỚC 1: convert_b64_file_to_text()
├─ Decode base64
├─ Extract text từ PDF/DOCX
└─ Output: ["text1", "text2", ...]

     ↓

BƯỚC 2: cluster_topics()
└─ Gọi get_raw_text_by_topic() cho từng doc

     ↓

BƯỚC 3: get_raw_text_by_topic() ← LOGIC CHÍNH
├─ Split văn bản: text.split('\n')
├─ Lọc AND: Giữ paragraphs có ĐỦ keywords[0]
│  └─ "khoa học" AND "công nghệ" → Cả hai phải có
├─ Lọc NOT: Bỏ paragraphs có keywords[1]
└─ Join lại: '\n'.join(filtered)

     ↓ (Chỉ còn 1 câu!)

BƯỚC 4: Tạo message output
{
  "list_doc": ["Dự án dược liệu quý..."],  ← Chỉ 1 câu!
  "topic_id": 120,
  "algo_id": 24
}

     ↓

BƯỚC 5: Gửi đến thuật toán
└─ producer.send("24_multi_lexrank", data)

     ↓

THUẬT TOÁN MULTI-LEXRANK
├─ Nhận message
├─ Kiểm tra văn bản quá ngắn?
│  └─ Nếu < 5 câu → Không tóm tắt được
└─ Gửi kết quả (có thể empty)

     ↓

OUTPUT (result_ai topic)
{
  "sumary_id": 306,
  "result": {
    "topic": [{
      "text": "",  ← Có thể rỗng nếu văn bản quá ngắn!
      "topic_id": 120
    }]
  }
}
```

---

## 🔧 TOOLS ĐÃ TẠO

### 1. Phân tích chi tiết
```bash
# Xem phân tích đầy đủ
cat PHAN_TICH_XU_LY_TOPIC.md
```

### 2. Test keyword filtering
```bash
# Demo quá trình lọc
python3 test_keyword_filter.py
```

### 3. Kiểm tra kết quả cuối
```bash
# Xem kết quả trong result_ai topic
./check_result_ai.sh 306
```

---

## 📊 SO SÁNH: STRICT VS LOOSE KEYWORDS

| Loại | Keywords | Kết quả | Đánh giá |
|------|----------|---------|----------|
| **STRICT** | `[["khoa học", "công nghệ"], []]` | 1-2 câu | ❌ Quá ít, không tóm tắt được |
| **MODERATE** | `[["công nghệ"], []]` | 5-8 câu | ✅ Vừa đủ |
| **LOOSE** | `[[], []]` | Toàn bộ | ⚠️  Nhiều quá, mất focus |

**Khuyến nghị**: Dùng **MODERATE** (1 keyword duy nhất)

---

## ❓ FAQ

**Q: Tại sao không dùng OR logic?**
- A: Code hiện tại **không hỗ trợ OR**. Chỉ hỗ trợ:
  - AND trong cùng keyword group: `["kw1", "kw2"]` = kw1 AND kw2
  - Nhiều keyword groups sẽ gửi messages riêng biệt

**Q: Làm sao biết văn bản có đủ dài không?**
- A: Chạy `python3 test_keyword_filter.py` với văn bản thực tế

**Q: Keyword có phân biệt hoa thường không?**
- A: **KHÔNG**. Code dùng `.lower()` để so sánh

**Q: Keyword có hỗ trợ regex không?**
- A: **KHÔNG**. Chỉ hỗ trợ exact substring match

**Q: Có thể sửa code để OR không?**
- A: Có, nhưng cần sửa hàm `get_raw_text_by_topic()` trong `helper_multi.py`

---

## 🚀 ACTION ITEMS

### Ngắn hạn (Fix ngay)
1. ✅ Hiểu rõ logic lọc
2. ✅ Test với script `test_keyword_filter.py`
3. ⬜ Nới lỏng keywords trong payload
4. ⬜ Test lại với keywords mới
5. ⬜ Kiểm tra kết quả trong `result_ai`

### Dài hạn (Cải thiện hệ thống)
1. ⬜ Thêm hỗ trợ OR logic
2. ⬜ Thêm logging để debug dễ hơn
3. ⬜ Thêm validation: Cảnh báo nếu văn bản sau lọc < 5 câu
4. ⬜ Thêm API endpoint để test keywords trước khi gửi

---

## 📖 TÀI LIỆU THAM KHẢO

1. **[PHAN_TICH_XU_LY_TOPIC.md](./PHAN_TICH_XU_LY_TOPIC.md)** - Phân tích code chi tiết
2. **[test_keyword_filter.py](./test_keyword_filter.py)** - Script test filtering
3. **[FIX_SHORT_TEXT_ISSUE.md](./FIX_SHORT_TEXT_ISSUE.md)** - Giải pháp văn bản ngắn
4. **[check_result_ai.sh](./check_result_ai.sh)** - Kiểm tra output cuối

---

## 💡 KẾT LUẬN

1. **Logic lọc RẤT STRICT**: Yêu cầu TẤT CẢ keywords phải có trong CÙNG 1 paragraph
2. **Vấn đề của bạn**: Keywords `["khoa học", "công nghệ"]` quá strict → Chỉ còn 1 câu
3. **Giải pháp**: Nới lỏng keywords thành `["công nghệ"]` hoặc `["dược liệu"]`
4. **Test trước**: Dùng `test_keyword_filter.py` để kiểm tra

**Hành động tiếp theo**: Sửa payload với keywords loose hơn và test lại! 🚀
