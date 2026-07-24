# Câu 1.1 — Độ nhạy của temperature

*Sinh tự động bởi `exercise_scripts/exercise_1_1_temperature.py` lúc 2026-07-24 16:27.*

## Cấu hình thí nghiệm

| Tham số | Giá trị |
|---|---|
| Model | `gemini-3.6-flash` |
| Prompt | Hãy kể cho tôi một sự thật thú vị về Hà Nội. |
| Temperature | 0.0, 0.7, 1.2, 1.8 |
| top_p | 1.0 (tắt nucleus sampling để chỉ temperature thay đổi) |
| max_tokens | 1500 |
| Số lần chạy mỗi mức | 2 |

## Bảng tổng hợp

| Temp | Số lần OK | Độ dài TB (ký tự) | Độ trễ TB | Các lần chạy giống nhau? |
|---|---|---|---|---|
| 0.0 | 2/2 | 1091 | 9.72s | không |
| 0.7 | 2/2 | 824 | 10.07s | không |
| 1.2 | 2/2 | 1075 | 9.49s | không |
| 1.8 | 2/2 | 1187 | 9.67s | không |

## Phản hồi đầy đủ

### Temperature = 0.0

#### Lần 1 — 9.88s, 956 ký tự

````text
Một sự thật rất thú vị và độc đáo về Hà Nội gắn liền với văn hóa ẩm thực: **Món "Cà phê trứng" nổi tiếng thế giới thực chất được ra đời từ... sự thiếu hụt nguyên liệu.**

Vào những năm 1940 (thời kỳ Pháp thuộc), sữa tươi và sữa đặc ở Hà Nội vô cùng khan hiếm và đắt đỏ. Cụ Nguyễn Văn Giảng, khi đó đang làm pha chế (bartender) tại khách sạn sang trọng Sofitel Legend Metropole, đã muốn làm món Cappuccino cho khách nhưng lại không có sữa. 

Trong cái khó ló cái khôn, cụ đã nghĩ ra giải pháp sáng tạo: **dùng lòng đỏ trứng gà đánh bông lên để thay thế cho bọt sữa.**

Thật bất ngờ, lớp kem trứng ngậy, mịn màng khi kết hợp với vị đắng của cà phê phin truyền thống không những không bị tanh mà còn tạo ra một hương vị thơm béo, đậm đà vô cùng đặc biệt. Sau đó, cụ Giảng đã nghỉ việc ở khách sạn và mở quán "Cà phê Giảng" – quán cà phê trứng đầu tiên ở Hà Nội, hiện vẫn tồn tại đến ngày nay.

Từ một giải pháp "thay thế tạm thời" trong lúc thiếu thốn, Cà phê
````

#### Lần 2 — 9.57s, 1227 ký tự

````text
Một trong những sự thật thú vị và "ngon lành" nhất về Hà Nội chính là **nguồn gốc ra đời của món Cà phê trứng** – thức uống nổi tiếng thế giới mà bất kỳ ai đến Hà Nội cũng muốn thử.

Món uống độc đáo này **được sáng tạo ra từ sự thiếu hụt nguyên liệu trong chiến tranh**:

* **Hoàn cảnh ra đời:** Vào những năm 1940 (thời kỳ Kháng chiến chống Pháp), sữa tươi và sữa đặc vô cùng hiếm hoi và đắt đỏ tại Hà Nội. 
* **Tác giả:** Cụ Nguyễn Văn Giảng, khi đó đang làm pha chế tại khách sạn hạng sang Sofitel Legend Metropole, đã nghĩ ra một cách thông minh để thay thế sữa: **dùng lòng đỏ trứng gà đánh bông**.
* **Kết quả:** Lớp kem trứng béo ngậy, thơm lừng đánh tan vị đắng của cà phê phin, tạo ra một hương vị tuyệt vời giống như món bánh Tiramisu dạng liquid. 

Sau đó, cụ Giảng đã nghỉ việc ở khách sạn và mở quán **Cà phê Giảng** vào năm 1946. Đến nay, thương hiệu này vẫn tồn tại qua nhiều thế hệ và công thức làm cà phê trứng truyền thống vẫn được giữ bí mật trong gia đình.

Từ một giải pháp "chữa cháy" trong lúc thiếu thốn, cà phê trứng đã trở thành một biểu tượng văn hóa ẩm thực của Thủ đô, được báo chí quốc tế (như CNN, National Geographic) liên tục ngợi khen và phục vụ các nguyên thủ quốc gia khi đến thăm Việt Nam!
````

### Temperature = 0.7

#### Lần 1 — 10.15s, 878 ký tự

````text
Một sự thật rất thú vị và đậm chất văn hóa về Hà Nội liên quan đến món đồ uống nổi tiếng thế giới của thành phố này: **Cà phê trứng được ra đời hoàn toàn do... thiếu sữa!**

Vào những năm 1940 (thời kỳ Pháp thuộc), sữa tươi và sữa condensed (sữa đặc) là những mặt hàng cực kỳ đắt đỏ và hiếm hoi tại Hà Nội. Lúc bấy giờ, ông **Nguyễn Văn Giảng** – một pha chế viên (bartender) làm việc tại khách sạn 5 sao sang trọng Grand Hotel Métropole Hà Nội – rất muốn tạo ra một món đồ uống có vị béo ngậy giống như Cappuccino của phương Tây để phục vụ khách hàng.

Vì không có sữa, ông Giảng đã nảy ra một ý tưởng táo bạo: **dùng lòng đỏ trứng gà đánh bông với đường** để thay thế cho bọt sữa. 

Kết quả thật bất ngờ: vị đắng đậm đà của cà phê phin Việt Nam khi kết hợp với lớp bọt trứng béo ngậy, thơm lừng (mà không hề bị tanh) đã tạo nên một hương vị vô cùng độc đáo. 

Sau đó, ông nghỉ
````

#### Lần 2 — 10.00s, 770 ký tự

````text
Một trong những sự thật thú vị và độc đáo nhất về Hà Nội chính là **nguồn gốc ra đời của món "Cà phê trứng"** – một thức uống biểu tượng đã vươn tầm thế giới.

Món uống sang trọng và béo ngậy này thực chất lại được ra đời từ **sự thiếu hụt và cái khó ló cái khôn**:

* **Hoàn cảnh:** Vào những năm 1940 (thời kỳ Pháp thuộc), mặt hàng sữa tươi và sữa đặc ở Hà Nội cực kỳ hiếm hoi và đắt đỏ do chiến tranh.
* **Sự sáng tạo:** Cụ Nguyễn Văn Giảng, khi đó đang làm pha chế tại khách sạn 5 sao sang trọng Sofitel Legend Metropole Hà Nội, đã nghĩ ra một giải pháp táo bạo: **dùng lòng đỏ trứng gà đánh bông lên để thay thế cho sữa**.
* **Kết quả:** Vị đắng của cà phê phin kết hợp với lớp kem trứng béo ngậy, thơm lừng (mà không hề bị tanh) đã tạo nên một hương vị bùng nổ. Cụ
````

### Temperature = 1.2

#### Lần 1 — 9.79s, 655 ký tự

````text
Một sự thật rất thú vị và "ngọt ngào" về Hà Nội: **Món "Cà phê trứng" nổi tiếng thế giới thực chất được ra đời từ sự thiếu thốn.**

Vào những năm 1940, trong thời kỳ chiến tranh, mặt hàng sữa tươi và sữa đặc ở Hà Nội vô cùng khan hiếm và đắt đỏ. Cụ Nguyễn Văn Giảng, khi đó đang làm pha chế (bartender) tại khách sạn sang trọng 5 sao **Sofitel Legend Metropole**, đã nghĩ ra một giải pháp thay thế táo bạo: **dùng lòng đỏ trứng gà đánh bông với đường để tạo độ ngậy thay cho sữa.**

Khi lớp kem trứng xốp mịn kết hợp với cà phê phin nóng hổi, nó tạo ra một hương vị bùi béo, thơm ngậy mà không hề bị tanh. Du khách nước ngoài khi đến Hà Nội thường gọi đây
````

#### Lần 2 — 9.18s, 1495 ký tự

````text
Một sự thật rất thú vị và đậm chất văn hóa về Hà Nội mà có thể bạn chưa biết: **Cà phê trứng – thức uống nổi tiếng thế giới của Hà Nội – thực chất được ra đời từ sự thiếu thốn trong thời chiến.**

### Câu chuyện đằng sau ly cà phê trứng:
Vào những năm 1940 (thời kỳ Chiến tranh Đông Dương), mặt hàng **sữa tươi và sữa đặc vô cùng khan hiếm và đắt đỏ** tại Hà Nội. 

Lúc bấy giờ, cụ Nguyễn Văn Giảng, vốn là pha chế trưởng cho khách sạn 5 sao Metropole Hanoi, rất muốn làm món cà phê Cappuccino lừng danh của phương Tây cho du khách nhưng lại không có sữa để tạo bọt.

Trong cái khó ló cái khôn, cụ Giảng đã nghĩ ra một giải pháp táo bạo: **dùng lòng đỏ trứng gà đánh bông với đường** để thay thế cho bọt sữa. Sự kết hợp giữa vị đắng đậm đà của cà phê phin Việt Nam và vị béo ngậy, thơm lừng không ngờ của trứng đánh bông đã tạo nên món **Cà phê trứng** huyền thoại.

### Điều đặc biệt ngày nay:
* Quán "Cà phê Giảng" do cụ mở ra từ năm 1946 hiện vẫn tồn tại ở phố Nguyễn Hữu Huân và luôn đông nghịt khách trong nước lẫn quốc tế.
* Món ăn xuất phát từ "sự thiếu thốn" này nay đã trở thành một biểu tượng ẩm thực của Hà Nội, xuất hiện trên nhiều tờ báo lớn như CNN, The Guardian và từng được phục vụ cho các phóng viên quốc tế tại Hội nghị thượng đỉnh Mỹ - Triều năm 2019.

---
** Mẹo nhỏ bonus:** Tên gọi **"Hà Nội"** (được vua Minh Mạng đặt năm 1831) có nghĩa là **"Bên trong các dòng sông"** (*Hà* = sông, *Nội* = bên trong). Thành phố được bao bọc bởi sông Hồng và sông Đáy, đó là lý do vì sao
````

### Temperature = 1.8

#### Lần 1 — 9.47s, 1166 ký tự

````text
Một sự thật rất thú vị và đậm chất lịch sử về Hà Nội liên quan đến món **Cà phê trứng** – một đặc sản nổi tiếng thế giới của Thủ đô:

**Món cà phê này ra đời là do... thiếu sữa!**

Vào những năm 1940 (thời kỳ Pháp thuộc), sữa tươi và sữa đặc là những mặt hàng vô cùng đắt đỏ và hiếm hoi tại Hà Nội. Cụ **Nguyễn Văn Giảng**, khi đó đang làm pha chế tại khách sạn sang trọng Sofitel Legend Metropole, đã nghĩ ra một cách thông minh để giải quyết sự thiếu hụt này: **Dùng lòng đỏ trứng gà đánh bông lên để thay thế cho sữa.**

Cụ Giảng đã đánh bông lòng đỏ trứng với đường và một chút mật chiết xuất, tạo ra một lớp kem ngậy, xốp mịn floating trên nền cà phê đen phin đậm đà. Vị béo ngậy của trứng không hề bị tanh mà còn làm dịu đi vị đắng gắt của cà phê phin Việt Nam.

Sau khi món uống này được khách hàng đón nhận nồng nhiệt, cụ Giảng đã nghỉ việc tại khách sạn Metropole để mở quán "Cà phê Giảng" lừng danh vào năm 1946. 

Ngày nay, từ một giải pháp "chữa cháy" lúc khó khăn, Cà phê trứng đã trở thành biểu tượng ẩm thực độc đáo của Hà Nội, được nhiều báo chí quốc tế (như CNN, National Geographic) ca ngợi và là món nhất định phải thử của du khách khi đến Thủ đô!
````

#### Lần 2 — 9.87s, 1209 ký tự

````text
Một sự thật rất thú vị và độc đáo về Hà Nội gắn liền với một món uống đã trở thành "huyền thoại": **Cà phê trứng ra đời là do... thiếu sữa!**

Vào những năm 1940, dưới thời Pháp thuộc, sữa tươi và sữa đặc là những mặt hàng vô cùng khan hiếm và đắt đỏ tại Hà Nội. Lúc này, cụ **Nguyễn Văn Giảng**, từng là pha chế viên (bartender) cho khách sạn 5 sao sang trọng Metropole, rất muốn làm món cà phê Cappuccino lừng danh của phương Tây để phục vụ khách hàng. 

Tuy nhiên, vì không có sữa để tạo bọt kem, cụ đã nảy ra một sáng kiến táo bạo: **dùng lòng đỏ trứng gà đánh bông lên cùng với đường để thay thế cho sữa.**

Sự kết hợp tưởng chừng như "sai quẻ" này lại tạo ra một thức uống béo ngậy, thơm lừng, làm mất đi vị tanh của trứng và giảm bớt vị đắng gắt của cà phê Robusta Việt Nam. 

**Điều thú vị hơn nữa:**
* Món uống "nhà nghèo" sáng tạo từ sự thiếu hụt năm xưa giờ đây đã trở thành **di sản ẩm thực đặc trưng nhất của Hà Nội**, được truyền thông quốc tế (như CNN, National Geographic) liên tục ngợi ca.
* Quán "Cà phê Giảng" do cụ sáng lập hiện vẫn hoạt động tại phố Nguyễn Hữu Huân (Quận Hoàn Kiếm) và được giữ gìn bởi các con cháu của cụ, trở thành điểm đến không thể bỏ qua của du khách khi tới Hà Nội.
````

