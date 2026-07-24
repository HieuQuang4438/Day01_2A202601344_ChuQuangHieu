"""
Web UI cho trợ lý — server cục bộ (chỉ dùng thư viện chuẩn, không cài thêm gì).

VÌ SAO CẦN SERVER?
    API key nằm trong .env và KHÔNG được lộ ra trình duyệt. Nếu trang HTML gọi
    thẳng Gemini thì key phải nằm trong JavaScript — ai mở trang cũng đọc được.
    Server này giữ key ở phía máy bạn; trình duyệt chỉ nói chuyện với localhost.

TÁI SỬ DỤNG CODE CỦA LAB
    Server dùng lại đúng các hàm bạn đã viết trong template.py:
    retry_with_backoff (Task 3.2), count_tokens (Task 2.2), estimate_cost
    (Task 2.3), và cùng quy tắc cắt history 4 lượt cuối như run_assistant.

Chạy (từ thư mục gốc của lab):
    python webui/server.py
rồi mở http://127.0.0.1:8000
"""

import json
import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

# Script nằm trong thư mục con -> thêm thư mục gốc của lab vào sys.path
LAB_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(LAB_DIR))

from template import (  # noqa: E402
    OPENAI_MINI_MODEL,
    OPENAI_MODEL,
    count_tokens,
    estimate_cost,
    retry_with_backoff,
)

# Console Windows mặc định là cp1252 — không in được tiếng Việt nếu không đổi
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

HERE = Path(__file__).resolve().parent
INDEX_HTML = HERE / "index.html"

# Chỉ lắng nghe trên máy cục bộ — không mở proxy chứa API key ra mạng LAN
HOST = "127.0.0.1"
PORT = int(os.getenv("WEBUI_PORT", "8000"))

# 4 lượt cuối = 8 message, đúng quy tắc của run_assistant
MAX_HISTORY_MESSAGES = 8

DEFAULT_PERSONA = (
    "Bạn là trợ giảng thân thiện của khóa AI, trả lời ngắn gọn bằng tiếng Việt."
)

# Các model đã kiểm chứng chạy được trên endpoint Gemini của lab.
# Bậc miễn phí giới hạn ~20 lượt/NGÀY cho TỪNG model của TỪNG project. Hạn mức
# là riêng biệt, nên nhiều model = nhiều hạn mức cộng lại. Khi model đang chọn
# hết quota, server tự chuyển xuống model kế tiếp trong danh sách này.
MODELS = [
    "gemini-3.6-flash",
    "gemini-3.5-flash",
    "gemini-3.5-flash-lite",
    "gemini-3.1-flash-lite",
    "gemini-flash-latest",
    "gemini-flash-lite-latest",
]


def is_quota_error(exc: Exception) -> bool:
    """Lỗi hết hạn mức (429) — khác hẳn lỗi mạng tạm thời: retry vô ích."""
    text = str(exc)
    return (
        "429" in text
        or "RESOURCE_EXHAUSTED" in text
        or "quota" in text.lower()
    )


class AssistantHandler(BaseHTTPRequestHandler):
    server_version = "K4LabWebUI/1.0"

    # -- tiện ích gửi dữ liệu -------------------------------------------------

    def _send(self, code: int, content_type: str, body: bytes) -> None:
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_json(self, code: int, payload: dict) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self._send(code, "application/json; charset=utf-8", body)

    def _sse(self, payload: dict) -> None:
        """Gửi một sự kiện SSE rồi flush ngay — đó là cách stream về trình duyệt."""
        line = f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"
        self.wfile.write(line.encode("utf-8"))
        self.wfile.flush()

    # -- routing --------------------------------------------------------------

    def do_GET(self) -> None:  # noqa: N802
        if self.path in ("/", "/index.html"):
            if not INDEX_HTML.exists():
                self._send_json(500, {"error": "Thiếu file index.html"})
                return
            body = INDEX_HTML.read_text(encoding="utf-8").encode("utf-8")
            self._send(200, "text/html; charset=utf-8", body)
        elif self.path == "/api/config":
            self._send_json(200, {
                "model": OPENAI_MODEL,
                "mini_model": OPENAI_MINI_MODEL,
                "models": MODELS,
                "default_persona": DEFAULT_PERSONA,
                "max_history_messages": MAX_HISTORY_MESSAGES,
                "has_api_key": bool(os.getenv("OPENAI_API_KEY")),
            })
        else:
            self._send_json(404, {"error": "Không tìm thấy: " + self.path})

    def do_POST(self) -> None:  # noqa: N802
        if self.path != "/api/chat":
            self._send_json(404, {"error": "Không tìm thấy: " + self.path})
            return

        length = int(self.headers.get("Content-Length") or 0)
        try:
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
        except Exception:
            self._send_json(400, {"error": "Body không phải JSON hợp lệ"})
            return

        message = (payload.get("message") or "").strip()
        if not message:
            self._send_json(400, {"error": "Thiếu nội dung tin nhắn"})
            return

        self._stream_reply(payload, message)

    # -- xử lý một lượt chat --------------------------------------------------

    def _stream_reply(self, payload: dict, message: str) -> None:
        persona = (payload.get("persona") or DEFAULT_PERSONA).strip()
        model = payload.get("model") or OPENAI_MODEL
        temperature = float(payload.get("temperature", 0.7))
        # top_p = 1.0 nghĩa là không cắt bớt phân phối (nucleus sampling tắt)
        top_p = float(payload.get("top_p", 1.0))
        history = payload.get("history") or []

        # Cắt còn 4 lượt cuối TRƯỚC khi gửi lên API — giống hệt run_assistant.
        # Client gửi cả lịch sử để hiển thị, nhưng chỉ phần này tốn token.
        trimmed = history[-MAX_HISTORY_MESSAGES:]

        # System prompt luôn đứng đầu → persona không mất khi history bị cắt
        messages = (
            [{"role": "system", "content": persona}]
            + trimmed
            + [{"role": "user", "content": message}]
        )

        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream; charset=utf-8")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("X-Accel-Buffering", "no")
        self.end_headers()

        from openai import OpenAI
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        # Thử model đang chọn trước, hết quota thì lần lượt sang các model còn
        # lại — mỗi model một hạn mức riêng nên tổng số lượt dùng được nhân lên
        chain = [model] + [m for m in MODELS if m != model]
        stream = None
        used_model = model
        last_error = None

        for candidate in chain:
            try:
                stream = retry_with_backoff(
                    lambda: client.chat.completions.create(
                        model=candidate,
                        messages=messages,
                        temperature=temperature,
                        top_p=top_p,
                        stream=True,
                    ),
                    # Hết hạn mức ngày thì chờ bao lâu cũng vô ích — đổi model
                    # nhanh hơn nhiều. Retry chỉ dành cho lỗi mạng chập chờn.
                    max_retries=0,
                )
                used_model = candidate
                break
            except Exception as e:
                last_error = e
                if not is_quota_error(e):
                    self._sse({"error": f"{type(e).__name__}: {e}"})
                    return
                self._sse({"notice": f"{candidate} đã hết hạn mức hôm nay."})

        if stream is None:
            self._sse({
                "error": "Tất cả model trong danh sách đều hết hạn mức hôm nay. "
                         "Xem UI_SPEC.md §9 để biết cách lấy thêm hạn mức miễn phí. "
                         f"Lỗi cuối: {last_error}"
            })
            return

        reply = ""
        try:
            for chunk in stream:
                delta = chunk.choices[0].delta.content or ""
                if delta:
                    reply += delta
                    self._sse({"delta": delta})
        except Exception as e:
            self._sse({"error": f"Đứt stream giữa chừng — {type(e).__name__}: {e}"})
            return

        # Tính chi phí theo model THỰC SỰ đã trả lời, không phải model đã chọn
        cost = estimate_cost(message, reply, used_model)
        self._sse({
            "done": True,
            "stats": {
                "tokens": (count_tokens(message, used_model)
                           + count_tokens(reply, used_model)),
                "cost": cost["total_cost"],
                "prompt_tokens": cost["prompt_tokens"],
                "completion_tokens": cost["completion_tokens"],
                "context_messages": len(trimmed),
                "model": used_model,
            },
        })

    def log_message(self, fmt: str, *args) -> None:
        sys.stderr.write(f"  {self.command} {self.path}\n")


def main() -> None:
    if not os.getenv("OPENAI_API_KEY"):
        print("CẢNH BÁO: chưa có OPENAI_API_KEY trong .env — chat sẽ báo lỗi.\n")
    print(f"Trợ lý web đang chạy:  http://{HOST}:{PORT}")
    print(f"Model mặc định:        {OPENAI_MODEL}")
    print("Nhấn Ctrl+C để dừng.\n")
    server = ThreadingHTTPServer((HOST, PORT), AssistantHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nĐã dừng server.")
        server.server_close()


if __name__ == "__main__":
    main()
