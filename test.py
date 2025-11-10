from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
tokenizer = AutoTokenizer.from_pretrained("pengold/t5-vietnamese-summarization")  
model = AutoModelForSeq2SeqLM.from_pretrained("pengold/t5-vietnamese-summarization")
model.cuda()


sentence = "Thế giớiPhân tíchThứ ba, 29/7/2025, 19:00 (GMT+7)\
Những yếu tố thúc đẩy Thái Lan - Campuchia ngừng bắn\
Vai trò trung gian của Malaysia, nước chủ tịch ASEAN, cùng áp lực từ cả trong và ngoài nước đã thúc đẩy Thái Lan, Campuchia đàm phán để ngừng bắn.\
Quyền Thủ tướng Thái Lan Phumtham Wechayachai và Thủ tướng Campuchia Hun Manet chiều 28/7 gặp nhau tại thủ đô hành chính Putrajaya, Malaysia, để đàm phán chấm dứt xung đột tại biên giới hai nước. Sau cuộc đàm phán, hai nước nhất trí ngừng bắn vô điều kiện từ 0h ngày 29/7, chấm dứt 5 ngày giao tranh.\
Đây là bước quan trọng đầu tiên nhằm hướng tới giảm căng thẳng và khôi phục hòa bình. Hai bên cũng đồng ý nối lại đối thoại trực tiếp ở cấp Thủ tướng, Ngoại trưởng và Bộ trưởng Quốc phòng, Thủ tướng Malaysia Anwar Ibrahim cho biết tại cuộc họp báo cùng ngày.\
Giới chuyên gia đánh giá nỗ lực hòa giải xung đột Thái Lan - Campuchia thành công nhờ nhiều yếu tố, trong đó có áp lực từ cộng đồng quốc tế để thúc đẩy hai bên đối thoại và vai trò trung gian của Malaysia, nước Chủ tịch ASEAN, góp phần thể hiện vai trò của khối là cơ chế hiệu quả trong giải quyết tranh chấp khu vực.\
Giao tranh Campuchia - Thái Lan bùng phát gần đền Ta Moan Thom sáng 24/7, sau đó lan sang các khu vực khác dọc biên giới hai nước. Đây là cuộc giao tranh nghiêm trọng nhất giữa hai nước láng giềng trong hơn 10 năm qua.\
Ngay sau khi xung đột bùng phát, các quốc gia ASEAN đã bày tỏ lo ngại, kêu gọi Thái Lan và Campuchia giải quyết hòa bình các bất đồng trên cơ sở những nguyên tắc cơ bản của luật pháp quốc tế.\
Với tư cách là quốc gia chủ tịch luân phiên ASEAN, Malaysia đã chủ động thúc đẩy biện pháp ngoại giao để hạ nhiệt tình hình. Ông Anwar ngày 25/7 đã điện đàm trực tiếp với ông Phumtham và ông Hun Manet, kêu gọi hai lãnh đạo lập tức ngừng bắn vô điều kiện, tạo không gian cho đối thoại hòa bình và giải pháp ngoại giao.\
Nỗ lực này gặp một số thách thức, bởi Campuchia ban đầu chọn đưa vấn đề ra Hội đồng Bảo an Liên Hợp Quốc, trong khi Thái Lan cho rằng đây là vấn đề song phương, không cần bên thứ ba hòa giải.\
Sau khi Hội đồng Bảo an không thể nhất trí về nghị quyết kêu gọi hai bên ngừng bắn, vai trò trung gian hòa giải của ASEAN nổi lên, đặc biệt là khi Tổng thống Donald Trump điện đàm với lãnh đạo Campuchia và Thái Lan, cảnh báo Mỹ sẽ dừng đàm phán thương mại với cả hai nước nếu họ không dừng xung đột.\
Tiến sĩ Julia Roknifard, giảng viên cao cấp tại Khoa Luật và Quản trị, Đại học Taylor's của Malaysia, cho rằng ông Trump là động lực đẩy nhanh tiến trình hòa giải theo cơ chế đã được Thủ tướng Anwar đề xuất, đề cao vai trò trung tâm của ASEAN trong giải quyết công việc nội bộ của khối.\
Ban đầu, hai nước không cởi mở với ý tưởng ASEAN có thể tham gia hòa giải và tuyên bố muốn giải quyết song phương. Nhưng rồi chính ASEAN lại trở thành cơ chế hiệu quả buộc hai bên phải tuân thủ trật tự, và họ đã làm vậy, bà Roknifard nói với Bernama.\
Trong bối cảnh hai quốc gia đang xung đột và nghi kỵ nhau, vị thế và uy tín của Malaysia trong ASEAN được phát huy. Malaysia là một trong những quốc gia sáng lập ASEAN, có truyền thống ngoại giao trung lập và luôn ưu tiên cách tiếp cận mang tính xây dựng, tôn trọng chủ quyền các nước. Malaysia không có tranh chấp trực tiếp với cả Thái Lan và Campuchia, giúp giảm bớt những lo ngại về thiên vị hoặc định kiến trong quá trình hòa giải.\
Những yếu tố trên giúp Malaysia trở thành lựa chọn phù hợp khi các bên muốn tìm kiếm giải pháp hòa bình, nhà phân tích chính trị độc lập Ahmad Martadha Mohamed nhận định.\
Cương vị chủ tịch luân phiên ASEAN giúp Malaysia có thêm lợi thế về quyền hạn. Và điều quan trọng là Malaysia biết phát huy vai trò này một cách linh hoạt, giáo sư Khoo Ying Hooi, Khoa Quốc tế và Nghiên cứu Chiến lược, Đại học Malaya, nói. Niềm tin được xây dựng khi Malaysia thể hiện sự sẵn sàng chấp nhận rủi ro về mặt ngoại giao để giúp xoa dịu căng thẳng.\
Malaysia còn phối hợp với Mỹ và Trung Quốc nhằm tăng áp lực đa phương, khuyến khích hai bên đạt được và tuân thủ thỏa thuận ngừng bắn. Mỹ và Trung Quốc là hai quốc gia có lợi ích kinh tế và chiến lược lớn với Thái Lan và Campuchia.\
Phát huy lợi thế này, Mỹ đã tham gia cùng Malaysia tổ chức cuộc đàm phán, trong khi Trung Quốc đóng vai trò quan sát viên. Đại sứ Mỹ tại Malaysia Edgard Kagan và người đồng cấp Trung Quốc Ouyang Yujing cũng tham gia vào quá trình thảo luận giữa các bên.\
Tuy nhiên, giới quan sát cho rằng việc thực thi lệnh ngừng bắn sẽ gặp nhiều khó khăn, do ASEAN còn thiếu công cụ cho mục đích này. Thái Lan cho hay giao tranh vẫn xảy ra tại vài điểm dọc biên giới sau 0h ngày 29/7, trong khi Campuchia nói tình hình đã lắng xuống sau khi lệnh ngừng bắn có hiệu lực.\
Lệnh ngừng bắn chỉ là là giải pháp tức thời và ngắn hạn. Điều quan trọng là duy trì hòa bình trong dài hạn và Thái Lan, Campuchia giải quyết được bất đồng biên giới, Abdul Rahman Yaacob, nhà nghiên cứu tại Viện Lowy, bình luận. Một cơ chế khả thi là triển khai quan sát viên Malaysia hoặc từ ASEAN đến biên giới Thái Lan - Campuchia. Đây là điều quan trọng, bởi Thái Lan và Campuchia đã mất niềm tin chiến lược vào nhau"
# text =  "vietnews: " + sentence + " </s>"

print(tokenizer.model_max_length)

encoding = tokenizer(sentence, return_tensors="pt")
input_ids, attention_masks = encoding["input_ids"].to("cuda"), encoding["attention_mask"].to("cuda")
while 1:
    outputs = model.generate(
        input_ids=input_ids, attention_mask=attention_masks,
        max_length=2048,
        # early_stopping=True,
        num_beams=5,           # Beam search để tạo kết quả tốt hơn
        # temperature=0.0,       # Điều chỉnh sự sáng tạo của kết quả
        length_penalty=1.5,    # Khuyến khích tạo ra câu dài hơn
    )
for output in outputs:
    line = tokenizer.decode(output, skip_special_tokens=True)
    print(line)
