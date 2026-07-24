"""
Câu 2.1 — Sức mạnh của persona (exercises.md)

Gọi chat_with_system_prompt hai lần với CÙNG một câu hỏi nhưng hai system
prompt khác nhau (nhà thơ vs kỹ sư senior), rồi so sánh giọng văn, độ dài và
mức độ kỹ thuật của hai phản hồi.

Kết quả vừa in ra màn hình, vừa ghi thành file markdown cạnh script này.

Tốn 2 lượt gọi API mỗi lần chạy. Bậc miễn phí giới hạn ~20 lượt/ngày cho TỪNG
model — hết hạn mức model này thì truyền tên model khác vào:
    python exercise_scripts/exercise_2_1_persona.py gemini-3.5-flash-lite

Chạy (từ thư mục gốc của lab):
    python exercise_scripts/exercise_2_1_persona.py
"""

import re
import sys
import time
from datetime import datetime
from pathlib import Path

LAB_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(LAB_DIR))

from template import OPENAI_MODEL, chat_with_system_prompt  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

QUESTION = "Giải thích máy học (machine learning) là gì?"

# Hai persona lấy nguyên văn từ đề bài Câu 2.1 trong exercises.md
PERSONAS = {
    "Nhà thơ": "Bạn là một nhà thơ, trả lời mọi thứ bằng hình ảnh ví von, "
               "tránh thuật ngữ.",
    "Kỹ sư senior": "Bạn là kỹ sư phần mềm senior, trả lời chính xác, "
                    "có ví dụ code khi phù hợp.",
}

TEMPERATURE = 0.7
# Gemini 3.x tính cả thinking token (ẩn) vào max_tokens, nên phần chữ thấy được
# ít hơn con số này khá nhiều. 2000 là mức đã dùng cho số liệu trích trong
# câu trả lời; nếu cột "Bị cắt?" báo có thì tăng lên 4000 rồi chạy lại.
MAX_TOKENS = 2000
MAX_RETRIES = 2
PAUSE = 2.0

MODEL = sys.argv[1] if len(sys.argv) > 1 else OPENAI_MODEL

OUTPUT_MD = Path(__file__).resolve().parent / "cau_2_1_persona.md"
FENCE = "````"

# Từ khóa kỹ thuật để ĐO mức độ chuyên ngành thay vì chỉ cảm nhận
JARGON = [
    "thuật toán", "dữ liệu", "mô hình", "huấn luyện", "train", "model",
    "code", "hàm", "tham số", "input", "output", "python", "AI",
    "machine learning", "deep learning", "neural", "dataset",
]


def looks_truncated(text: str) -> bool:
    """Phỏng đoán phản hồi bị cắt vì hết max_tokens (dựa vào dấu câu cuối)."""
    s = text.rstrip()
    return bool(s) and s[-1] not in '.!?…:;"\')»”*`'


def profile(text: str) -> dict:
    """Đo vài đặc điểm hình thức để so sánh hai persona bằng số, không cảm tính."""
    lower = text.lower()
    return {
        "chars": len(text),
        "words": len(text.split()),
        "headings": len(re.findall(r"^#{1,6}\s", text, re.M)),
        "bullets": len(re.findall(r"^\s*[-*•]\s", text, re.M)),
        "code_blocks": text.count("```") // 2,
        "jargon": sum(lower.count(k.lower()) for k in JARGON),
        "truncated": looks_truncated(text),
    }


def call_with_retry(system_prompt: str) -> tuple[str, float]:
    for attempt in range(MAX_RETRIES + 1):
        try:
            return chat_with_system_prompt(
                system_prompt, QUESTION,
                model=MODEL, temperature=TEMPERATURE, max_tokens=MAX_TOKENS,
            )
        except Exception as e:
            if attempt == MAX_RETRIES:
                raise
            match = re.search(r"retry in ([\d.]+)s", str(e))
            delay = min(float(match.group(1)) + 1, 90.0) if match else 2.0 * (2 ** attempt)
            print(f"    (lỗi tạm thời — chờ {delay:.0f}s rồi thử lại)")
            time.sleep(delay)


def run_experiment() -> dict:
    results = {}
    for name, persona in PERSONAS.items():
        print("=" * 72)
        print(f"PERSONA: {name}")
        print("=" * 72)
        try:
            text, latency = call_with_retry(persona)
            text = text.strip()
            p = profile(text)
            results[name] = {"persona": persona, "text": text,
                             "latency": latency, "profile": p, "error": None}
            flag = "  ⚠ CÓ VẺ BỊ CẮT" if p["truncated"] else ""
            print(f"[{latency:.2f}s, {p['chars']} ký tự]{flag}\n")
            print(text)
        except Exception as e:
            msg = f"{type(e).__name__}: {e}"
            results[name] = {"persona": persona, "text": "", "latency": 0.0,
                             "profile": None, "error": msg}
            print(f"LỖI: {msg}")
        print()
        time.sleep(PAUSE)
    return results


def build_markdown(results: dict) -> str:
    lines = [
        "# Câu 2.1 — Sức mạnh của persona",
        "",
        f"*Sinh tự động bởi `exercise_scripts/{Path(__file__).name}` "
        f"lúc {datetime.now():%Y-%m-%d %H:%M}.*",
        "",
        "## Cấu hình thí nghiệm",
        "",
        "| Tham số | Giá trị |",
        "|---|---|",
        f"| Model | `{MODEL}` |",
        f"| Câu hỏi (giống nhau cả hai lần) | {QUESTION} |",
        f"| Temperature | {TEMPERATURE} |",
        f"| max_tokens | {MAX_TOKENS} |",
        "",
        "## Bảng so sánh",
        "",
        "| Persona | Độ trễ | Ký tự | Từ | Heading | Gạch đầu dòng | Khối code | Từ kỹ thuật | Bị cắt? |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for name, r in results.items():
        if r["error"]:
            lines.append(f"| {name} | — | — | — | — | — | — | — | — |")
            continue
        p = r["profile"]
        lines.append(
            f"| **{name}** | {r['latency']:.2f}s | {p['chars']} | {p['words']} "
            f"| {p['headings']} | {p['bullets']} | {p['code_blocks']} "
            f"| {p['jargon']} | {'**có**' if p['truncated'] else 'không'} |"
        )

    ok = [r for r in results.values() if r["error"] is None]
    if len(ok) == 2:
        a, b = (r["profile"]["chars"] for r in ok)
        if min(a, b) > 0:
            lines += ["", f"Chênh lệch độ dài: **{max(a, b) / min(a, b):.1f} lần**."]
        if any(r["profile"]["truncated"] for r in ok):
            lines += [
                "",
                f"> ⚠️ Có phản hồi chạm trần `max_tokens={MAX_TOKENS}` nên bị cắt "
                "giữa chừng — cột “ký tự”/“từ” của lượt đó đo ngân sách token còn "
                "lại chứ không đo độ dài dụng ý của model. Tăng `MAX_TOKENS` rồi "
                "chạy lại nếu muốn so sánh độ dài cho chuẩn.",
            ]

    lines += ["", "## Phản hồi đầy đủ", ""]
    for name, r in results.items():
        lines += [f"### {name}", "", "**System prompt:**", "",
                  FENCE + "text", r["persona"], FENCE, ""]
        if r["error"]:
            lines += ["**Kết quả:** LỖI", "", f"`{r['error']}`", ""]
        else:
            lines += ["**Phản hồi:**", "",
                      FENCE + "text", r["text"], FENCE, ""]

    return "\n".join(lines) + "\n"


def main() -> None:
    print(f"Model: {MODEL}")
    print(f"Câu hỏi: {QUESTION}")
    print(f"Hai persona, temperature={TEMPERATURE}\n")

    results = run_experiment()

    print("=" * 72)
    print("BẢNG SO SÁNH")
    print("=" * 72)
    print(f"{'Persona':<16}{'Ký tự':>8}{'Từ':>7}{'Heading':>9}"
          f"{'Code':>6}{'Từ KT':>7}")
    for name, r in results.items():
        if r["error"]:
            print(f"{name:<16}{'LỖI':>8}")
            continue
        p = r["profile"]
        print(f"{name:<16}{p['chars']:>8}{p['words']:>7}{p['headings']:>9}"
              f"{p['code_blocks']:>6}{p['jargon']:>7}")

    OUTPUT_MD.write_text(build_markdown(results), encoding="utf-8")
    print(f"\nĐã ghi báo cáo: {OUTPUT_MD.relative_to(LAB_DIR)}")
    print("Gợi ý: so sánh cột 'Từ kỹ thuật' và 'Heading' — đó là bằng chứng ĐO "
          "ĐƯỢC\ncho việc system prompt điều khiển mức kỹ thuật và định dạng.")


if __name__ == "__main__":
    main()