#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script test và visualize quá trình lọc keywords
"""

def get_raw_text_by_topic(topics, raw_text):
    """
    Copy từ helper_multi.py để test
    """
    def removeDuplicates(lst):
        return list(set([i for i in lst]))

    list_pragrab = raw_text.split('\n')
    list_raw = []
    topic_choose = topics[0]
    topic_not = topics[1]

    # AND Logic
    if len(topic_choose) != 0:
        for key_words in topic_choose:
            key_word = key_words.split(',')
            for pragrab in list_pragrab:
                is_choose = True
                for word in key_word:
                    if word.lower() not in pragrab.lower():
                        is_choose = False
                if is_choose == True:
                    index = list_pragrab.index(pragrab)
                    list_raw.append((index, pragrab))
    else:
        count = 0
        for pragrab in list_pragrab:
            list_raw.append((count, pragrab))
            count += 1

    list_raw = removeDuplicates(list_raw)
    list_raw_process = sorted(list_raw, key=lambda tup: tup[0])

    # NOT Logic
    list_raw_final = []
    if len(topic_not) != 0:
        for key_words in topic_not:
            key_word = key_words.split(',')
            for pragrab in list_raw_process:
                is_choose = True
                for word in key_word:
                    if ' ' + word.strip().lower() + ' ' in pragrab[1].lower():
                        is_choose = False
                if is_choose == True:
                    list_raw_final.append(pragrab)
    else:
        list_raw_final = list_raw_process

    list_raw_final = removeDuplicates(list_raw_final)
    list_raw_final_process = sorted(list_raw_final, key=lambda tup: tup[0])

    list_text_topic = []
    for text_topic in list_raw_final_process:
        list_text_topic.append(text_topic[1])

    return '\n'.join(list_text_topic)


def analyze_filtering(text, keywords):
    """
    Phân tích chi tiết quá trình lọc
    """
    print("=" * 80)
    print("PHÂN TÍCH QUÁ TRÌNH LỌC KEYWORDS")
    print("=" * 80)
    print()

    and_keywords = keywords[0]
    not_keywords = keywords[1]

    print(f"📋 AND Keywords (phải có TẤT CẢ): {and_keywords}")
    print(f"🚫 NOT Keywords (không được có): {not_keywords}")
    print()

    # Split thành paragraphs
    paragraphs = text.split('\n')
    print(f"📄 Tổng số paragraphs: {len(paragraphs)}")
    print()

    # Phân tích từng paragraph
    print("="*80)
    print("PHÂN TÍCH TỪNG PARAGRAPH")
    print("="*80)

    matched_count = 0
    matched_paras = []

    for i, para in enumerate(paragraphs):
        if not para.strip():
            continue

        print(f"\n[Paragraph {i+1}]")
        print(f"Text: {para[:80]}{'...' if len(para) > 80 else ''}")

        # Kiểm tra AND keywords
        and_results = {}
        for kw_group in and_keywords:
            keywords_in_group = kw_group.split(',')
            group_match = True
            for kw in keywords_in_group:
                found = kw.lower() in para.lower()
                and_results[kw] = found
                if not found:
                    group_match = False

            if group_match:
                print(f"  ✅ AND: {and_results}")
                matched_count += 1
                matched_paras.append((i, para))
            else:
                print(f"  ❌ AND: {and_results} (thiếu keyword)")

        # Kiểm tra NOT keywords
        if not_keywords:
            not_results = {}
            has_not = False
            for kw_group in not_keywords:
                keywords_in_group = kw_group.split(',')
                for kw in keywords_in_group:
                    found = ' ' + kw.strip().lower() + ' ' in para.lower()
                    not_results[kw] = found
                    if found:
                        has_not = True

            if has_not:
                print(f"  ⚠️  NOT: {not_results} (chứa NOT keyword → loại bỏ)")
            else:
                print(f"  ✅ NOT: {not_results} (OK)")

    print()
    print("="*80)
    print("KẾT QUẢ LỌC")
    print("="*80)
    print(f"Số paragraphs matched: {matched_count}/{len([p for p in paragraphs if p.strip()])}")
    print()

    # Gọi hàm lọc thực tế
    result = get_raw_text_by_topic(keywords, text)
    result_paras = [p for p in result.split('\n') if p.strip()]

    print(f"Số paragraphs sau lọc: {len(result_paras)}")
    print()

    if result_paras:
        print("Văn bản sau lọc:")
        print("-" * 80)
        print(result)
        print("-" * 80)
    else:
        print("⚠️  KHÔNG CÒN VĂN BẢN SAU KHI LỌC!")

    return result


def test_case_1():
    """Test case: Keywords strict như trong ví dụ của user"""
    print("\n")
    print("🧪 TEST CASE 1: Keywords STRICT (yêu cầu cả 'khoa học' VÀ 'công nghệ')")
    print()

    text = """Trí tuệ nhân tạo đang phát triển mạnh mẽ.
Nghiên cứu khoa học và công nghệ tiến bộ nhanh chóng.
Dự án dược liệu quý được đầu tư mạnh.
Công nghệ blockchain đang được ứng dụng rộng rãi.
Y học hiện đại sử dụng AI để chẩn đoán.
Khoa học dữ liệu kết hợp công nghệ máy học mang lại nhiều đột phá.
Dự án phát triển vùng trồng dược liệu ứng dụng công nghệ cao.
Nghiên cứu về công nghệ sinh học đang tiến triển."""

    keywords = [["khoa học", "công nghệ"], []]
    result = analyze_filtering(text, keywords)

    return len(result.split('\n'))


def test_case_2():
    """Test case: Keywords loose hơn"""
    print("\n")
    print("🧪 TEST CASE 2: Keywords LOOSE (chỉ cần 'công nghệ')")
    print()

    text = """Trí tuệ nhân tạo đang phát triển mạnh mẽ.
Nghiên cứu khoa học và công nghệ tiến bộ nhanh chóng.
Dự án dược liệu quý được đầu tư mạnh.
Công nghệ blockchain đang được ứng dụng rộng rãi.
Y học hiện đại sử dụng AI để chẩn đoán.
Khoa học dữ liệu kết hợp công nghệ máy học mang lại nhiều đột phá.
Dự án phát triển vùng trồng dược liệu ứng dụng công nghệ cao.
Nghiên cứu về công nghệ sinh học đang tiến triển."""

    keywords = [["công nghệ"], []]
    result = analyze_filtering(text, keywords)

    return len(result.split('\n'))


def test_case_3():
    """Test case: Với NOT keywords"""
    print("\n")
    print("🧪 TEST CASE 3: Keywords với NOT (có 'công nghệ' nhưng KHÔNG có 'blockchain')")
    print()

    text = """Trí tuệ nhân tạo đang phát triển mạnh mẽ.
Nghiên cứu khoa học và công nghệ tiến bộ nhanh chóng.
Dự án dược liệu quý được đầu tư mạnh.
Công nghệ blockchain đang được ứng dụng rộng rãi.
Y học hiện đại sử dụng AI để chẩn đoán.
Khoa học dữ liệu kết hợp công nghệ máy học mang lại nhiều đột phá.
Dự án phát triển vùng trồng dược liệu ứng dụng công nghệ cao.
Nghiên cứu về công nghệ sinh học đang tiến triển."""

    keywords = [["công nghệ"], ["blockchain"]]
    result = analyze_filtering(text, keywords)

    return len(result.split('\n'))


def main():
    print("\n" + "="*80)
    print(" TEST VÀ PHÂN TÍCH KEYWORD FILTERING")
    print("="*80)

    # Chạy các test cases
    count1 = test_case_1()
    count2 = test_case_2()
    count3 = test_case_3()

    # Tổng kết
    print("\n" + "="*80)
    print("TỔNG KẾT")
    print("="*80)
    print(f"Test 1 (STRICT - khoa học AND công nghệ): {count1} paragraphs")
    print(f"Test 2 (LOOSE - chỉ công nghệ):          {count2} paragraphs")
    print(f"Test 3 (WITH NOT - công nghệ NOT blockchain): {count3} paragraphs")
    print()

    print("💡 KẾT LUẬN:")
    print("   - Keywords càng strict → Kết quả càng ít")
    print("   - Nếu văn bản sau lọc < 5 câu → Không đủ để tóm tắt")
    print("   - Khuyến nghị: Dùng ít keywords hơn hoặc nới lỏng điều kiện")
    print()


if __name__ == "__main__":
    main()
