# Đặc tả Web UI — Trợ lý K4 Ngày 1

> ⚠️ **Quy tắc bắt buộc:** file này phải được cập nhật **cùng lúc** với mọi
> thay đổi trong `webui/index.html` hoặc `webui/server.py`. Sửa UI mà không
> sửa spec là coi như chưa xong việc. Mục [Nhật ký thay đổi](#nhật-ký-thay-đổi)
> ghi lại từng lần sửa.

---

## 1. Mục đích

Thay giao diện dòng lệnh của `run_assistant()` bằng giao diện web, nhưng giữ
**nguyên hành vi**: system prompt cố định, stream token, history 4 lượt cuối,
thống kê token/chi phí.

## 2. Kiến trúc

```
Trình duyệt  ──HTTP──▶  webui/server.py  ──HTTPS──▶  Gemini API
(index.html)            (localhost, giữ key)          (endpoint OpenAI-compat)
```

**Vì sao phải có server, không dùng HTML thuần?**
Trang HTML chạy trong trình duyệt thì mọi thứ nó chứa đều công khai. Muốn gọi
thẳng API thì phải nhúng `OPENAI_API_KEY` vào JavaScript — ai mở trang cũng đọc
được key. Server cục bộ giữ key ở phía máy người dùng; trình duyệt chỉ nói
chuyện với `127.0.0.1`.

**Ràng buộc bảo mật**
- Server **chỉ** bind `127.0.0.1` — không mở ra mạng LAN.
- Key không bao giờ xuất hiện trong HTML, JS, hay response của server.
- `/api/config` chỉ trả `has_api_key: true|false`, không trả giá trị key.

## 3. Danh sách file

| File | Vai trò |
|---|---|
| `webui/server.py` | Server + proxy tới API. Chỉ dùng thư viện chuẩn của Python. |
| `webui/index.html` | Toàn bộ giao diện: HTML + CSS + JS trong một file, không CDN. |
| `webui/UI_SPEC.md` | File này. |

**Tái sử dụng từ `template.py`** (không viết lại logic):
`retry_with_backoff` (Task 3.2), `count_tokens` (Task 2.2),
`estimate_cost` (Task 2.3), `OPENAI_MODEL`, `OPENAI_MINI_MODEL`.

> `run_assistant()` **không** được gọi trực tiếp: nó đọc input qua `get_input()`
> và `print()` ra stdout — không stream về trình duyệt được. Server dựng lại
> đúng vòng lặp một lượt bằng các hàm nhỏ ở trên.

## 4. Cách chạy

```bash
python webui/server.py          # từ thư mục gốc của lab
```
Mở <http://127.0.0.1:8000>. Đổi cổng bằng biến môi trường `WEBUI_PORT`.

## 5. API

### `GET /` → `text/html`
Trả `index.html`, đọc lại từ đĩa mỗi lần gọi (sửa file rồi F5 là thấy ngay,
không cần khởi động lại server).

### `GET /api/config` → `application/json`
```json
{
  "model": "gemini-3.5-flash",
  "mini_model": "gemini-3.5-flash-lite",
  "models": ["gemini-3.6-flash", "gemini-3.5-flash", "..."],
  "default_persona": "Bạn là trợ giảng thân thiện...",
  "max_history_messages": 8,
  "has_api_key": true
}
```

### `POST /api/chat` → `text/event-stream`
Request:
```json
{
  "message": "câu hỏi của người dùng",
  "history": [{"role": "user|assistant", "content": "..."}],
  "persona": "system prompt",
  "model": "gemini-3.6-flash",
  "temperature": 0.7,
  "top_p": 1.0
}
```

Response — chuỗi sự kiện SSE, mỗi sự kiện một dòng `data: {...}`:

| Sự kiện | Ý nghĩa |
|---|---|
| `{"delta": "..."}` | Một mẩu text vừa sinh ra. Client nối vào bong bóng đang mở. |
| `{"notice": "..."}` | Model vừa thử đã hết hạn mức; server đang tự chuyển sang model kế tiếp. Client chèn dòng thông báo màu nhấn **phía trên** bong bóng đang chờ. |
| `{"error": "..."}` | Lỗi thật (mất mạng, hết sạch mọi model…). Client hiện khung đỏ, bỏ bong bóng. |
| `{"done": true, "stats": {...}}` | Kết thúc lượt. |

`stats` gồm: `tokens`, `cost`, `prompt_tokens`, `completion_tokens`,
`context_messages` (số message thực sự gửi lên API sau khi cắt), và `model` —
**model thực sự đã trả lời**, có thể khác model người dùng chọn nếu đã fallback.

### Tự động chuyển model khi hết hạn mức

Bậc miễn phí giới hạn ~20 lượt/ngày cho **từng model** của **từng project**, nên
mỗi model là một hạn mức riêng. Khi model đang chọn trả về 429, server không
chờ (hạn mức NGÀY thì chờ vô ích) mà lần lượt thử các model còn lại trong
`MODELS`, gửi một `notice` mỗi lần chuyển:

```
chain = [model người dùng chọn] + [các model còn lại trong MODELS]
```

`retry_with_backoff` được gọi với `max_retries=0` trong vòng lặp này — retry chỉ
hợp lý cho lỗi mạng chập chờn, không hợp lý cho hạn mức ngày. Lỗi **không phải**
429 thì dừng ngay và báo `error`, không thử model khác.

Chi phí và token được tính theo model đã trả lời, không phải model đã chọn.

Mã lỗi HTTP: `400` (thiếu message / JSON hỏng), `404` (sai đường dẫn),
`500` (thiếu `index.html`).

## 6. Quản lý trạng thái

| Trạng thái | Nơi giữ | Sống qua F5? | Ghi chú |
|---|---|---|---|
| Lịch sử hội thoại | **Client** (biến `history`) | ❌ | Server không nhớ gì giữa các request. |
| Chi tiết từng lượt | **Client** (biến `turnLog`) | ❌ | Dùng để xuất file .md — xem §7.1. |
| Thống kê cộng dồn | **Client** | ❌ | Server chỉ trả số liệu của từng lượt. |
| Cấu hình (persona / model / temperature) | **Client** (`localStorage`) | ✅ | Xem bên dưới. |
| Cắt còn 4 lượt | **Server** (`history[-8:]`) | — | Quy tắc của lab nằm ở server, không tin client. |

Hệ quả: client hiển thị **toàn bộ** hội thoại, nhưng chỉ 8 message cuối được
gửi lên API. UI phải nói rõ điều này (xem §7).

### Lưu cấu hình trong trình duyệt

Khóa `localStorage`: **`k4-webui-settings-v1`**, giá trị là JSON
`{persona, model, temperature, top_p}` (tất cả đều là chuỗi).

Thêm trường mới thì **không** cần đổi số version của khóa: đọc bằng `??` nên
dữ liệu lưu từ trước — thiếu trường mới — vẫn dùng được, trường thiếu lấy giá
trị mặc định. Chỉ đổi lên `-v2` nếu ý nghĩa của một trường cũ thay đổi.

- **Ghi:** mỗi lần người dùng gõ persona (`input`), đổi model (`change`), hoặc
  kéo thanh temperature / top_p (`input`).
- **Đọc:** một lần lúc tải trang, hòa với `/api/config` — giá trị đã lưu thắng,
  thiếu thì lấy mặc định của server.
- **Model đã lưu không còn trong `MODELS`** (danh sách server đã đổi) → bỏ qua,
  quay về `LAB_MODEL` của server. Persona và temperature vẫn được giữ.
- **`localStorage` hỏng hoặc bị tắt** (chế độ ẩn danh, trình duyệt chặn) →
  `loadSettings()`/`saveSettings()` nuốt lỗi và chạy tiếp với mặc định.
- **Temperature và top_p** được gán vào `<input type=range>` rồi **đọc lại**
  trước khi hiển thị, nên giá trị ngoài khoảng hợp lệ tự động bị kẹp về biên.

Cố ý **không** lưu lịch sử hội thoại: mỗi lần mở trang là một phiên mới, giống
`run_assistant()` chạy lại từ đầu. Muốn đổi, phải sửa cả mục này.

> Lưu ý: `localStorage` tách theo origin. `http://127.0.0.1:8000` và
> `http://localhost:8000` là **hai origin khác nhau** — cấu hình lưu ở địa chỉ
> này sẽ không thấy ở địa chỉ kia.

## 7. Thành phần giao diện

Bố cục 2 cột (`320px` + phần còn lại); dưới `860px` xếp dọc thành 1 cột.

### Cột trái — panel “Cấu hình”
Cả bốn ô đều được **nhớ lại sau khi F5** qua `localStorage` (xem §6).

| Thành phần | Kiểu | Mặc định | Hành vi |
|---|---|---|---|
| System prompt | `<textarea>` | từ `/api/config` | Sửa được giữa chừng, áp dụng từ lượt kế tiếp. Để trống → server dùng persona mặc định. |
| Model | `<select>` | `LAB_MODEL` | Danh sách từ `/api/config`. Nếu `LAB_MODEL` trong `.env` không có trong danh sách thì được chèn lên đầu và chọn sẵn. |
| Temperature | `<input type=range>` 0 → 2, bước 0.1 | `0.7` | Giá trị hiện ngay cạnh nhãn. |
| top_p | `<input type=range>` 0 → 1, bước 0.05 | `1.0` | Nucleus sampling. Mặc định 1.0 = **không** cắt bớt phân phối, để temperature một mình quyết định độ ngẫu nhiên. |

> Dưới hai thanh trượt có dòng nhắc: thường chỉ chỉnh **một** trong hai
> (`LAB_GUIDE.md` dòng 89). Chỉnh cả hai cùng lúc thì rất khó quy kết thay đổi
> trong output là do tham số nào.

### Cột trái — panel “Thống kê phiên chat”
`Số lượt`, `Token đã dùng`, `Chi phí ước tính` ($, 8 chữ số thập phân),
`Ngữ cảnh gửi lên` (số message), `Model trả lời` (model thực sự phục vụ lượt
gần nhất — lệch với ô Model nghĩa là đã fallback). Kèm dòng nhắc **“chỉ 4 lượt
cuối được gửi lên API”**.

Hai nút xếp ngang bên dưới:
- **Xuất file .md** — tải nhật ký hội thoại về máy (xem §7.1). Bị khóa
  (`disabled`) khi `turnLog` rỗng.
- **Xóa hội thoại** — xóa `history`, `turnLog`, thống kê về 0, khóa lại nút
  Xuất. **Không** đụng đến cấu hình đã lưu trong `localStorage`.

### 7.1 Xuất hội thoại ra file .md

Chạy **hoàn toàn phía client** — không gọi server, không tốn lượt API. Dựng
chuỗi markdown từ `turnLog` rồi tải xuống bằng `Blob` + `URL.createObjectURL`.

Tên file: `chat-YYYYMMDD-HHmm.md` (theo giờ máy người dùng).

Cấu trúc file:

| Phần | Nội dung |
|---|---|
| Tiêu đề + thời điểm xuất | `# Nhật ký hội thoại — Trợ lý K4 Ngày 1` |
| Bảng **Cấu hình** | Model (danh sách **tất cả** model đã trả lời, khử trùng lặp), temperature, top_p, số lượt, token, chi phí |
| **System prompt** | Nội dung ô persona **tại thời điểm xuất** |
| **Hội thoại** | Mỗi lượt một mục `### Lượt N`: câu hỏi, rồi phản hồi kèm model / token / chi phí / số message ngữ cảnh của **chính lượt đó** |
| Ghi chú cuối | Nhắc rằng chỉ 4 lượt gần nhất được gửi lên API và chi phí chỉ là ước tính |

Mọi nội dung do người dùng và model sinh ra đều được bọc trong fence **4
backtick** (` ```` `) — phản hồi của model thường chứa sẵn `###`/`**`, để trần
sẽ phá cấu trúc file báo cáo. Dùng 4 backtick vì model có thể trả về khối code
bọc bằng 3 backtick.

> Cảnh báo khi sửa: temperature, top_p và persona được đọc từ ô nhập **lúc bấm
> Xuất**, còn model/token/chi phí đọc từ `turnLog` **lúc chạy từng lượt**. Nếu
> người dùng đổi temperature giữa chừng, bảng Cấu hình chỉ phản ánh giá trị
> cuối. Muốn chính xác từng lượt thì phải lưu thêm vào `turnLog`.

### Cột phải — khung chat
- Bong bóng người dùng: căn phải, nền màu nhấn.
- Bong bóng trợ lý: căn trái, nền panel, viền mảnh.
- Khung lỗi: chiếm cả chiều ngang, viền đỏ, chữ đỏ.
- Dòng thông báo (`.msg.note`): chiếm cả chiều ngang, nền `--accent-soft`, chữ
  `--accent`, không viền — dùng cho việc tự chuyển model.
- Đang stream: bong bóng có con trỏ nhấp nháy (`.cursor`), tự cuộn xuống đáy.
- Ô nhập: **Enter** gửi, **Shift+Enter** xuống dòng. Nút Gửi khóa lại khi đang
  chờ phản hồi (`busy`).
- Trạng thái rỗng: dòng hướng dẫn ở giữa khung, biến mất khi có tin nhắn đầu.

## 8. Style

Biến CSS trong `:root`, có bản ghi đè `@media (prefers-color-scheme: dark)` —
giao diện tự theo sáng/tối của hệ điều hành.

| Biến | Sáng | Tối |
|---|---|---|
| `--bg` | `#f7f7f8` | `#17171a` |
| `--panel` | `#ffffff` | `#1f1f23` |
| `--border` | `#e2e2e5` | `#33333a` |
| `--text` | `#1c1c1e` | `#ececf1` |
| `--muted` | `#6b6b72` | `#9a9aa4` |
| `--accent` | `#2f6f4e` | `#6bbd92` |
| `--error` | `#b3261e` | `#f2b8b5` |

Font: `system-ui` stack. Bo góc `--radius: 10px`. Không dùng font/ảnh/script
từ bên ngoài — toàn bộ nằm trong một file.

## 9. Những chỗ dễ sai

| Triệu chứng | Nguyên nhân |
|---|---|
| Server chết ngay khi khởi động, `UnicodeEncodeError` | Console Windows dùng cp1252. Server đã tự `sys.stdout.reconfigure(encoding="utf-8")` — đừng bỏ dòng đó. |
| Hiện dòng “… đã hết hạn mức hôm nay” rồi vẫn có trả lời | Đúng thiết kế: server đã tự chuyển sang model khác. Xem ô **Model trả lời**. |
| Sửa code server rồi mà hành vi không đổi | Server cũ vẫn giữ cổng 8000. Phải tắt tiến trình cũ trước khi chạy lại (`index.html` thì không cần — nó đọc lại từ đĩa mỗi request). |
| Chữ hiện thành từng cục lớn, không mượt | Bình thường: Gemini trả chunk to, không phải từng token một. |
| Trợ lý “quên” điều đã nói | Đúng thiết kế — quá 4 lượt thì message cũ bị cắt. |
| Persona lạ tự hiện lên khi mở trang | Đó là cấu hình lần trước còn lưu trong `localStorage`. Sửa lại ô đó, hoặc xóa khóa `k4-webui-settings-v1` trong DevTools → Application → Local Storage. |
| Cấu hình không được nhớ | Mở bằng `localhost` thay vì `127.0.0.1` (khác origin), hoặc trình duyệt đang chặn `localStorage`. |

### Khi hết sạch hạn mức miễn phí

Hạn mức là **~20 lượt/ngày × mỗi model × mỗi project**. Theo thứ tự nên thử:

1. **Đổi model** — đã tự động; danh sách `MODELS` có 6 model nên tổng cộng
   khoảng 120 lượt/ngày. Thêm model mới vào `MODELS` là thêm hạn mức.
2. **Tạo project mới trong Google AI Studio** và lấy key khác — hạn mức tính
   theo project, nên project mới là một bộ hạn mức mới. Vẫn miễn phí.
3. **Chuyển sang NVIDIA NIM** — luồng miễn phí thứ hai của lab, hào phóng hơn
   nhiều. Chỉ đổi `.env` (mẫu có sẵn), không sửa dòng code nào.
   Xem `LAB_GUIDE.md` Phụ lục C.
4. **Chờ sang ngày hôm sau** — hạn mức tự phục hồi theo chu kỳ ngày. Xem mức
   dùng hiện tại tại <https://ai.dev/rate-limit>.

Lưu ý: `pytest` và `python grade.py` **không** tốn lượt gọi nào — toàn bộ test
đều mock. Hết hạn mức không ảnh hưởng điểm số.

## 10. Nhật ký thay đổi

| Ngày | Thay đổi |
|---|---|
| 2026-07-24 | Bản đầu: server SSE + giao diện 2 cột, chọn model, temperature, thống kê, cắt history 4 lượt. |
| 2026-07-24 | Tự động chuyển model khi gặp 429: thêm sự kiện SSE `notice`, kiểu `.msg.note`, ô thống kê “Model trả lời”; `MODELS` tăng lên 6; chi phí tính theo model đã trả lời. Thêm §9 “Khi hết sạch hạn mức miễn phí”. |
| 2026-07-24 | Lưu persona / model / temperature vào `localStorage` (khóa `k4-webui-settings-v1`) để F5 không mất cấu hình. Lịch sử hội thoại vẫn cố ý không lưu. Thêm §6 “Lưu cấu hình trong trình duyệt”. |
| 2026-07-24 | Thêm thanh trượt **top_p** (0–1, mặc định 1.0), gửi kèm trong `POST /api/chat` và lưu cùng các cấu hình khác. Giữ nguyên khóa `-v1` — dữ liệu cũ thiếu `top_p` vẫn đọc được. |
| 2026-07-24 | Thêm nút **Xuất file .md**: ghi nhật ký hội thoại kèm cấu hình và thống kê từng lượt, chạy hoàn toàn phía client. Thêm biến `turnLog`, kiểu `.actions`, và §7.1. |
