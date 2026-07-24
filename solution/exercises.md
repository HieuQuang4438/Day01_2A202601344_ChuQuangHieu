# K4 — Ngày 1: Bài Tập & Phản Ánh
## Khám Phá LLM API | Phiếu Thực Hành

**Thời lượng:** 14h00–18h00
**Cách làm:** Trả lời từng câu ngay sau khi hoàn thành block tương ứng —
đừng để dồn hết về cuối buổi. Thay dòng `*Câu trả lời của bạn*` bằng câu
trả lời thật (chấm tự động sẽ đếm số câu đã trả lời).

---

## Block 1 — API Cơ Bản (trả lời sau Checkpoint 1)

### Câu 1.1 — Độ nhạy của temperature
Gọi `call_openai` với temperature 0.0, 0.7, 1.2 và 1.8 dùng prompt
**"Hãy kể cho tôi một sự thật thú vị về Hà Nội."**

**Bạn nhận thấy quy luật gì qua bốn phản hồi? Ở mức nào phản hồi bắt đầu
kém mạch lạc?** (2–3 câu)
> *Chạy cả 4 mức tempperature, phản hồi đều liên quan tới cà phê trứng -> đưa ra thông tin tương tự nhau, chỉ khác về diễn đạt và bố cục. Đáng chú ý, 2 chạy 0.0 2 lần vẫn ra kết quả khác nhau, càng lên cao càng khác biệt. ở 0.7 và 1.8 model trả lời cả tiếng Anh lẫn lộn với tiếng Việt ("sữa condensed", "lớp kem xốp mịn floating"), ở 1.2 có lần lan man sang hẳn một chủ đề phụ không ai hỏi (giải nghĩa tên "Hà Nội"), còn ở 1.8 xuất hiện chi tiết bịa thêm nghe rất lạ ("một chút mật chiết xuất") -> bắt đầu kém mạch lạc ở 1.2.*

### Câu 1.2 — Chọn temperature cho sản phẩm
**Bạn sẽ đặt temperature bao nhiêu cho trợ lý soạn thảo hợp đồng pháp lý,
và bao nhiêu cho trợ lý viết slogan quảng cáo? Giải thích khác biệt.**
> *Với trợ lý soạn thảo hợp đồng pháp lý: temp 0-0.2; trợ lý viết slogan quảng cáo: 1-1.3. Lý do nằm ở chi phí của một câu trả lời sai: trong hợp đồng pháp lý, chỉ cần model sáng tạo thay 1 thuật ngữ bằng đồng nghĩa là nghĩa của điều khoản có thể bị đổi, gây hậu quả pháp lý nghiêm trọng -> nên cần ưu tiên chính xác, thống nhất, đồng thời 2-3 lần chạy phải cho kết quả gần như nhau để đổi chiếu, rà soát và giải trình đc. Ngược lại, một solgan kém/dở thì bỏ đi là đc, giá trị của model ở đây là có thể tạo ra nhiều phiên bản/biến thể để cho con người chọn -> ưu tiên sự đa dạng, sáng tạo thay vì sự chính xác, ổn định.*

### Câu 1.3 — Đánh đổi chi phí
Kịch bản: 20.000 người dùng hoạt động mỗi ngày, mỗi người gọi API 2 lần,
mỗi lần trung bình ~500 token đầu ra.

**Ước tính chi phí mỗi ngày của model lớn so với model nhỏ cho workload này
(dựa trên bảng giá trong template). Nêu một trường hợp model lớn xứng đáng
với chi phí và một trường hợp model nhỏ là lựa chọn đúng:**
> *Ước tính: 20.000 người × 2 lượt = 40.000 lượt gọi/ngày, mỗi lượt ~500 token đầu ra → 20 triệu token đầu ra/ngày (= 20.000K token). Theo bảng giá trong template.py cho cặp model tôi đang chạy: gemini-3.5-flash tốn 20.000 × $0,009 = $180/ngày (~$5.400/tháng), còn gemini-3.5-flash-lite tốn 20.000 × $0,0025 = $50/ngày (~$1.500/tháng) — chênh $130/ngày, tức $3.900/tháng, model lớn đắt gấp 3,6 lần. (Đề bài chỉ cho token đầu ra; nếu tính thêm ~200 token đầu vào mỗi lượt thì thành $192 so với $52,4 mỗi ngày — chi phí đầu ra vẫn áp đảo, nên muốn tiết kiệm thì cắt độ dài câu trả lời hiệu quả hơn nhiều so với cắt prompt.) Đáng chú ý là khoảng cách này phụ thuộc mạnh vào cặp model: với cặp gốc của lab, gpt-4o ($200/ngày) đắt hơn gpt-4o-mini ($12/ngày) tới 16,7 lần, nên lập luận "dùng model nhỏ để tiết kiệm" mạnh hơn hẳn ở OpenAI so với cặp Gemini tôi đang dùng. Model lớn xứng đáng khi chi phí của một câu trả lời sai lớn hơn $130/ngày. Ví dụ trợ lý rà soát hợp đồng hoặc sinh code chạy thẳng lên production: nếu model nhỏ sai thêm 5% thì mỗi ngày có 2.000 lượt sai, mỗi lượt tốn 5 phút người kiểm tra sửa lại là đã hơn 160 giờ công/ngày — vượt xa khoản tiết kiệm $130. Ở đây tiền API không phải là chi phí chính, chi phí sửa sai mới là. Model nhỏ là lựa chọn đúng khi tác vụ đơn giản và lỗi rẻ. Ví dụ phân loại ý định tin nhắn (đặt hàng / khiếu nại / hỏi giá), gợi ý câu trả lời nhanh cho FAQ, hay tóm tắt một đoạn ngắn: chất lượng hai model gần như không phân biệt được với người dùng, sai thì họ chỉ cần hỏi lại, mà tiết kiệm được 72% chi phí. Thực tế tôi sẽ kết hợp cả hai — cho model nhỏ xử lý trước, chỉ chuyển lên model lớn khi nó không đủ tự tin — để giữ chi phí gần mức $50 mà vẫn có chất lượng cao ở những ca khó.*

---

## Block 2 — System Prompt & Token (trả lời sau Checkpoint 2)

### Câu 2.1 — Sức mạnh của persona
Gọi `chat_with_system_prompt` hai lần với cùng câu hỏi
**"Giải thích máy học (machine learning) là gì?"** nhưng hai system prompt
khác nhau:
- "Bạn là một nhà thơ, trả lời mọi thứ bằng hình ảnh ví von, tránh thuật ngữ."
- "Bạn là kỹ sư phần mềm senior, trả lời chính xác, có ví dụ code khi phù hợp."

**Hai phản hồi khác nhau như thế nào (giọng văn, độ dài, mức kỹ thuật)?
Từ đó rút ra system prompt điều khiển được những khía cạnh nào của phản hồi?**
(3–4 câu)
> *Hai phản hồi khác nhau gần như hoàn toàn dù câu hỏi y hệt. Persona nhà thơ trả về 969 ký tự dưới dạng thơ có vần — mở đầu bằng hình ảnh "Hãy tưởng tượng một chú chim non vừa mới chào đời, / Chưa biết gió ngàn sâu, chưa tỏ lối mây trôi", rồi ví việc máy học như con chim tự nhận ra quả chín khác hòn đá sau khi nhìn hàng nghìn lần, và không dùng một thuật ngữ kỹ thuật nào. Persona kỹ sư senior trả về 3.310 ký tự, gấp 3,4 lần, viết bằng văn xuôi kỹ thuật có tiêu đề markdown ("### 1. Machine Learning là gì? (Sự dịch chuyển tư duy lập trình)"), gạch đầu dòng, so sánh trực diện với lập trình truyền thống và dẫn cả ví dụ code. Từ đó thấy system prompt điều khiển được giọng văn, độ dài, mức độ kỹ thuật của từ vựng, và cả định dạng trình bày (thơ so với heading + bullet) — tức là gần như toàn bộ "hình thức" của câu trả lời, trong khi nội dung cốt lõi vẫn là cùng một khái niệm; nói cách khác nó định hình model nói như ai, chứ không thay đổi model biết gì.*

### Câu 2.2 — tiktoken vs đếm từ
Chọn một đoạn văn tiếng Việt ~150 từ. So sánh số token theo `count_tokens`
(tiktoken) với ước lượng `số từ / 0.75` mà Part 1 đã dùng.

**Hai con số chênh nhau bao nhiêu phần trăm? Nếu dùng ước lượng thô để dự
toán ngân sách API cho ứng dụng tiếng Việt, bạn sẽ dự toán thiếu hay thừa —
và vì sao?**
> *Với một đoạn văn tiếng Việt 175 từ, ước lượng thô cho 175 / 0.75 = 233 token, còn count_tokens dùng tiktoken thật (bộ mã hóa o200k_base của gpt-4o) đếm được 239 token — chỉ chênh −2,4%, tức ước lượng thô dự toán thiếu nhưng gần như không đáng kể. Lý do là o200k_base có vốn từ phủ tiếng Việt khá tốt, trung bình chỉ 1,37 token/từ (tiếng Anh là 1,08), nên hệ số 1/0,75 = 1,33 vốn hiệu chỉnh cho tiếng Anh lại tình cờ khớp. Nhưng kết luận này phụ thuộc hoàn toàn vào bộ mã hóa: cùng đoạn văn đó, cl100k_base (gpt-4/gpt-3.5 đời cũ) đếm tới 398 token = 2,27 token/từ, lúc này ước lượng thô dự toán thiếu tới 41% — dự toán 1 triệu đô sẽ vỡ thành 1,7 triệu. Nguyên nhân là chữ có dấu bị tách vụn: nghỉ thành 3 token ['ng','h','ỉ'], trứng thành 2 token, trong khi coffee chỉ 1 token. Vì vậy tôi sẽ luôn đếm bằng tiktoken với đúng bộ mã hóa của model sắp dùng, chứ không nhân hệ số từ; và với ứng dụng tiếng Việt thì luôn cộng thêm biên an toàn, vì mọi sai số của cách ước lượng thô đều lệch về phía thiếu tiền.*

---

## Block 3 — Streaming & Độ Bền (trả lời sau Checkpoint 3)

### Câu 3.1 — Trải nghiệm người dùng với streaming
**Xét ba ứng dụng: (a) chatbot văn bản, (b) trợ lý giọng nói đọc to phản hồi,
(c) pipeline dịch tài liệu chạy ngầm ban đêm. Ứng dụng nào hưởng lợi nhiều
nhất từ streaming, ứng dụng nào không cần — và tại sao?** (1 đoạn văn)
> *Trợ lý giọng nói (b) hưởng lợi nhiều nhất, vì trong hội thoại bằng giọng nói thì im lặng vài giây là cực kỳ khó chịu — người dùng sẽ tưởng máy hỏng và nói chen vào; có streaming thì hệ thống chỉ cần đợi đủ câu đầu tiên là đã bắt đầu đọc to, phần sau vừa sinh vừa đọc gối đầu nhau, kéo độ trễ cảm nhận từ vài giây xuống dưới một giây (đo thực tế trong lab, một phản hồi đầy đủ của gemini-3.5-flash mất 4–13 giây, im lặng chừng đó là không chấp nhận được). Điểm cần lưu ý là với giọng nói phải gom chunk đến hết câu hoặc hết mệnh đề rồi mới đưa sang bộ đọc, chứ không đọc được nửa từ như hiển thị chữ. Chatbot văn bản (a) cũng hưởng lợi rõ nhưng ít gay gắt hơn: chữ hiện dần cho người dùng biết máy đang chạy và đọc được ngay từ dòng đầu, song nhìn ô trống vài giây vẫn dễ chịu hơn nghe im lặng vài giây. Pipeline dịch tài liệu chạy ngầm ban đêm (c) hoàn toàn không cần streaming vì không có ai ngồi đợi — thứ duy nhất quan trọng là tổng thời gian và chi phí của cả lô; thêm streaming chỉ làm code phức tạp hơn (phải ghép chunk, xử lý đứt giữa chừng, khó retry nguyên lượt) mà không đổi lấy lợi ích nào, thậm chí còn cản việc dùng batch API vốn rẻ hơn nhiều. Nói ngắn gọn: streaming cải thiện độ trễ CẢM NHẬN chứ không làm model sinh chữ nhanh hơn, nên nó chỉ đáng giá khi có người đang chờ, và càng đáng giá khi kênh giao tiếp càng khó chấp nhận khoảng lặng.*

### Câu 3.2 — Vì sao backoff theo cấp số nhân?
**Khi API quá tải và hàng nghìn client cùng retry, exponential backoff giúp
gì so với delay cố định? Tra cứu thêm: kỹ thuật "jitter" (thêm độ trễ ngẫu
nhiên) giải quyết vấn đề gì còn sót lại?**
> *Với delay cố định, hàng nghìn client cùng thử lại đều đặn sau mỗi X giây nên tổng tải đổ vào server gần như không giảm — server đang nghẽn không bao giờ có khoảng trống để xả hàng đợi và hồi phục, lỗi kéo dài bao lâu thì cơn bão request kéo dài bấy nhiêu. Exponential backoff làm khoảng chờ tăng gấp đôi sau mỗi lần (0,1s → 0,2s → 0,4s…), nên tần suất request của cả hệ thống giảm theo cấp số nhân: server càng lỗi lâu thì client càng thưa dần, tự động nhường chỗ cho nó phục hồi, mà vẫn kiên nhẫn chứ không bỏ cuộc ngay từ lần đầu. Nhưng backoff một mình chưa xử lý được vấn đề ĐỒNG BỘ: nếu 1.000 client cùng gặp lỗi tại một thời điểm (ví dụ server vừa khởi động lại), chúng sẽ cùng chờ 0,1s, rồi cùng chờ 0,2s… tức vẫn ập vào thành từng đợt đúng cùng lúc — chỉ là các đợt thưa hơn — và mỗi đợt vẫn đủ sức quật ngã server vừa mới gượng dậy. Jitter thêm một lượng ngẫu nhiên vào thời gian chờ (phổ biến nhất là ngủ một khoảng ngẫu nhiên trong [0, base × 2^lần]) để các client lệch pha nhau, biến những cột sóng nhọn thành dòng tải trải đều — đây chính là thứ hàm `retry_with_backoff` của tôi còn thiếu, vì nó dùng đúng `base_delay * 2**attempt` không có yếu tố ngẫu nhiên. Một điều tôi rút ra khi làm lab: backoff chỉ chữa được quá tải TẠM THỜI; khi tôi gặp 429 vì hết hạn mức MỖI NGÀY của bậc miễn phí thì chờ bao lâu cũng vô ích, lúc đó phải đổi model hoặc đổi key chứ retry chỉ tốn thêm lượt gọi.*

---

## Block 4 — Mini-Project (trả lời sau Checkpoint 4)

### Câu 4.1 — Thiết kế persona
**Viết lại system prompt bạn dùng cho trợ lý của mình. Chỉ ra 2 chỗ trong
prompt mà nếu xóa đi, hành vi trợ lý sẽ thay đổi rõ rệt — và mô tả thay đổi
đó:**
> *System prompt tôi dùng cho trợ lý (trong `template.py` và mặc định của web UI) là: **"Bạn là trợ giảng thân thiện của khóa AI, trả lời ngắn gọn bằng tiếng Việt."** Câu này ngắn nhưng gồm bốn thành phần tách bạch: vai trò (trợ giảng), phạm vi (khóa AI), giọng điệu (thân thiện), và hai ràng buộc đầu ra (ngắn gọn, tiếng Việt). **Chỗ thứ nhất, nếu xóa "trả lời ngắn gọn":** trợ lý sẽ chuyển sang kiểu trả lời dài và có cấu trúc — đúng như tôi quan sát ở Câu 2.1 và Câu 1.1, khi không bị ràng buộc độ dài thì model tự thêm tiêu đề markdown `###`, gạch đầu dòng và viết 1.000–3.300 ký tự cho một câu hỏi đơn giản, trong khi với ràng buộc này nó trả lời gọn trong một câu ("Thủ đô của Việt Nam là thành phố Hà Nội bạn nhé!"). Hệ quả không chỉ là trải nghiệm: theo tính toán ở Câu 1.3, chi phí chủ yếu nằm ở token ĐẦU RA, nên bỏ hai chữ này có thể làm hóa đơn tăng vài lần mà nội dung hữu ích không tăng tương ứng. **Chỗ thứ hai, nếu xóa "bằng tiếng Việt":** trợ lý sẽ trôi dần sang tiếng Anh hoặc pha trộn hai thứ tiếng, nhất là với câu hỏi kỹ thuật nơi thuật ngữ tiếng Anh chiếm ưu thế trong dữ liệu huấn luyện — thực tế ngay cả KHI vẫn giữ ràng buộc này, ở temperature cao model đã chèn "sữa condensed" và "lớp kem xốp mịn floating" vào câu tiếng Việt, nên bỏ hẳn đi thì hiện tượng chắc chắn nặng hơn. Ngược lại, xóa chữ "thân thiện" thì thay đổi mờ nhạt hơn nhiều: câu trả lời chỉ bớt các tiểu từ như "nhé", "bạn ơi" chứ nội dung gần như giữ nguyên — cho thấy ràng buộc về ĐỊNH DẠNG và NGÔN NGỮ có sức nặng lớn hơn ràng buộc về giọng điệu.*

### Câu 4.2 — Hạn chế & cải thiện
**Trợ lý của bạn giữ history 4 lượt cuối. Hãy mô tả một tình huống hội thoại
cụ thể mà giới hạn này khiến trợ lý trả lời sai/mất ngữ cảnh, và đề xuất một
cách khắc phục (ví dụ: tóm tắt các lượt cũ, tăng giới hạn có chọn lọc...):**
> *Tình huống cụ thể: ở lượt 1 tôi nói "Tôi đang chạy Python 3.8 trên máy công ty, không được cài thư viện ngoài", rồi hỏi tiếp 5 lượt về cách đọc file CSV, tách cột, lọc dòng, tính trung bình và vẽ biểu đồ. Đến lượt 6, câu ràng buộc ở lượt 1 đã bị `history = history[-8:]` cắt mất, nên trợ lý vô tư khuyên tôi `pip install pandas` rồi dùng cú pháp `match` của Python 3.10 — cả hai đều không dùng được, mà nó vẫn trả lời rất tự tin vì không còn biết ràng buộc đó từng tồn tại. Điểm đáng chú ý là persona thì KHÔNG mất, vì trong `run_assistant` system prompt được ghép lại ở đầu `messages` mỗi lượt; thứ bị mất chỉ là ràng buộc do NGƯỜI DÙNG đặt ra — mà đó thường lại là thông tin quan trọng nhất của cả phiên. Cách khắc phục tôi chọn là **ghim (pin) + tóm tắt**: những message chứa ràng buộc lâu dài (phiên bản, môi trường, yêu cầu định dạng) được đánh dấu và luôn giữ lại bất kể cắt bao nhiêu, còn các lượt cũ bị loại thì trước khi bỏ được gộp thành một đoạn tóm tắt 1–2 câu chèn vào ngay sau system prompt, để trợ lý vẫn nhớ đại ý cuộc trò chuyện mà không phải trả tiền cho toàn bộ lịch sử. Ngoài ra tôi sẽ **cắt theo ngân sách token thay vì theo số message**: 8 message có thể là 50 token mà cũng có thể là 5.000 token, dùng `count_tokens` để cắt đến khi vừa hạn mức thì vừa an toàn về chi phí vừa tận dụng được nhiều ngữ cảnh hơn khi các lượt đều ngắn. Chi phí phải trả cho tóm tắt là thêm một lời gọi API mỗi lần cắt, nên thực tế chỉ nên tóm tắt sau mỗi vài lượt chứ không phải mọi lượt.*

---

## Danh Sách Kiểm Tra Nộp Bài

- [ ] `python grade.py` — xem điểm tự động, mục tiêu ≥ 75/100
- [ ] Cả 4 checkpoint pytest đều pass
- [ ] Tất cả 9 câu trong file này đã được trả lời
- [ ] Đã copy bài làm vào folder `solution/`, push lên GitHub cá nhân và nộp link repo vào vlearn (theo hướng dẫn README)
