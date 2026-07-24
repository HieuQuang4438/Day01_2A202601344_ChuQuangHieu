# Câu 2.2 — tiktoken vs ước lượng đếm từ

*Sinh tự động bởi `exercise_scripts/exercise_2_2_tokens.py` lúc 2026-07-24 23:40. Không gọi API.*

## Đoạn văn dùng để đo

````text
Một trong những sự thật thú vị và ngon lành nhất về Hà Nội chính là nguồn gốc ra đời của món Cà phê trứng, thức uống nổi tiếng thế giới mà bất kỳ ai đến Hà Nội cũng muốn thử. Món uống độc đáo này được sáng tạo ra từ sự thiếu hụt nguyên liệu trong chiến tranh. Vào những năm 1940, thời kỳ Kháng chiến chống Pháp, sữa tươi và sữa đặc vô cùng hiếm hoi và đắt đỏ tại Hà Nội. Cụ Nguyễn Văn Giảng, khi đó đang làm pha chế tại khách sạn hạng sang Sofitel Legend Metropole, đã nghĩ ra một cách thông minh để thay thế sữa, đó là dùng lòng đỏ trứng gà đánh bông. Lớp kem trứng béo ngậy, thơm lừng đánh tan vị đắng của cà phê phin, tạo ra một hương vị tuyệt vời. Sau đó, cụ Giảng đã nghỉ việc ở khách sạn và mở quán Cà phê Giảng vào năm 1946, đến nay thương hiệu này vẫn tồn tại qua nhiều thế hệ.
````

Số từ (tách theo khoảng trắng): **175**  
Ước lượng thô của Part 1 (`số từ / 0.75`): **233 token**

## Kết quả đếm

| Bộ mã hóa | Model dùng bộ này | Token thật | Token/từ | Ước lượng thô lệch |
|---|---|---|---|---|
| `o200k_base` | gpt-4o, gpt-4o-mini | **239** | 1.37 | -2.4% (dự toán thiếu) |
| `cl100k_base` | gpt-4, gpt-3.5-turbo (đời cũ) | **398** | 2.27 | -41.4% (dự toán thiếu) |

Cùng nội dung bằng tiếng Anh (25 từ) để đối chứng:

| Bộ mã hóa | Token | Token/từ |
|---|---|---|
| `o200k_base` | 27 | 1.08 |
| `cl100k_base` | 29 | 1.16 |

## count_tokens() theo model đang cấu hình

`.env` đang đặt model **`gemini-3.5-flash`**:

- `count_tokens(text)` → **196 token**
- `count_tokens(text, model="gpt-4o")` → **239 token**

> ⚠️ tiktoken **không có** bảng mã hóa cho model này, nên `count_tokens(text)` rơi vào nhánh dự phòng `len(text) // 4` — đó là ước lượng theo ký tự, **không phải** đếm token thật. Muốn có số liệu đúng cho Câu 2.2 phải truyền `model="gpt-4o"` tường minh.

## Vì sao tiếng Việt tốn token hơn

Chữ có dấu bị tách thành nhiều mảnh, trong khi từ tiếng Anh thông dụng thường gọn trong một token (`o200k_base`):

| Từ | Số token | Bị tách thành |
|---|---|---|
| `nghỉ` | 3 | `ng` + `h` + `ỉ` |
| `Giảng` | 2 | `Gi` + `ảng` |
| `trứng` | 2 | `tr` + `ứng` |
| `người` | 2 | `ng` + `ười` |
| `coffee` | 1 | `coffee` |
| `Hanoi` | 2 | `H` + `anoi` |

