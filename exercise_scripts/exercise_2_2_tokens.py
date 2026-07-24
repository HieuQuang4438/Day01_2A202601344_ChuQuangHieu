"""
Câu 2.2 — tiktoken vs ước lượng đếm từ (exercises.md)

So sánh ba cách đếm token cho một đoạn văn tiếng Việt:
    1. Ước lượng thô của Part 1:  số từ / 0.75
    2. tiktoken thật, bộ mã hóa o200k_base  (gpt-4o, gpt-4o-mini)
    3. tiktoken thật, bộ mã hóa cl100k_base (gpt-4, gpt-3.5-turbo đời cũ)
cộng với count_tokens() theo model đang cấu hình trong .env, để thấy rõ khi
nào hàm rơi vào nhánh dự phòng len(text) // 4.

KHÔNG gọi API — tiktoken chạy cục bộ, nên chạy bao nhiêu lần cũng không tốn
hạn mức miễn phí. (Lần chạy đầu tiên cần mạng để tải bảng mã hóa về cache.)

Chạy (từ thư mục gốc của lab):
    python exercise_scripts/exercise_2_2_tokens.py
    python exercise_scripts/exercise_2_2_tokens.py duong/dan/den/file.txt
"""

import sys
from datetime import datetime
from pathlib import Path

LAB_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(LAB_DIR))

from template import OPENAI_MODEL, count_tokens  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

OUTPUT_MD = Path(__file__).resolve().parent / "cau_2_2_tokens.md"
FENCE = "````"

# Đoạn văn mặc định (~175 từ) lấy từ chính phản hồi trong cau_1_1_temperature.md
DEFAULT_TEXT = (
    "Một trong những sự thật thú vị và ngon lành nhất về Hà Nội chính là "
    "nguồn gốc ra đời của món Cà phê trứng, thức uống nổi tiếng thế giới mà "
    "bất kỳ ai đến Hà Nội cũng muốn thử. Món uống độc đáo này được sáng tạo "
    "ra từ sự thiếu hụt nguyên liệu trong chiến tranh. Vào những năm 1940, "
    "thời kỳ Kháng chiến chống Pháp, sữa tươi và sữa đặc vô cùng hiếm hoi và "
    "đắt đỏ tại Hà Nội. Cụ Nguyễn Văn Giảng, khi đó đang làm pha chế tại "
    "khách sạn hạng sang Sofitel Legend Metropole, đã nghĩ ra một cách thông "
    "minh để thay thế sữa, đó là dùng lòng đỏ trứng gà đánh bông. Lớp kem "
    "trứng béo ngậy, thơm lừng đánh tan vị đắng của cà phê phin, tạo ra một "
    "hương vị tuyệt vời. Sau đó, cụ Giảng đã nghỉ việc ở khách sạn và mở quán "
    "Cà phê Giảng vào năm 1946, đến nay thương hiệu này vẫn tồn tại qua nhiều "
    "thế hệ."
)

# Câu tiếng Anh cùng ý, để đối chứng số token trên mỗi từ giữa hai ngôn ngữ
ENGLISH_TEXT = (
    "One of the most interesting facts about Hanoi is the origin of egg "
    "coffee, a world famous drink that anyone visiting Hanoi wants to try."
)

ENCODINGS = [
    ("o200k_base", "gpt-4o, gpt-4o-mini"),
    ("cl100k_base", "gpt-4, gpt-3.5-turbo (đời cũ)"),
]

# Vài từ mổ xẻ để thấy chữ có dấu bị tách vụn thế nào
SAMPLE_WORDS = ["nghỉ", "Giảng", "trứng", "người", "coffee", "Hanoi"]

ROUGH_RATIO = 0.75   # hệ số "0.75 từ ≈ 1 token" mà Part 1 dùng


def rough_estimate(text: str) -> float:
    return len(text.split()) / ROUGH_RATIO


def measure(text: str) -> dict:
    """Đếm token của text theo từng bộ mã hóa. Trả về dict để dựng báo cáo."""
    import tiktoken

    words = len(text.split())
    rough = rough_estimate(text)
    rows = []
    for enc_name, models in ENCODINGS:
        enc = tiktoken.get_encoding(enc_name)
        n = len(enc.encode(text))
        rows.append({
            "encoding": enc_name,
            "models": models,
            "tokens": n,
            "per_word": n / words,
            # Ước lượng thô lệch bao nhiêu % so với số token thật
            "deviation": (rough - n) / n * 100,
        })
    return {"words": words, "rough": rough, "rows": rows}


def sample_breakdown() -> list[tuple[str, int, list[str]]]:
    import tiktoken
    enc = tiktoken.get_encoding("o200k_base")
    out = []
    for word in SAMPLE_WORDS:
        ids = enc.encode(word)
        out.append((word, len(ids), [enc.decode([i]) for i in ids]))
    return out


def build_markdown(text: str, vi: dict, en: dict, samples: list) -> str:
    lines = [
        "# Câu 2.2 — tiktoken vs ước lượng đếm từ",
        "",
        f"*Sinh tự động bởi `exercise_scripts/{Path(__file__).name}` "
        f"lúc {datetime.now():%Y-%m-%d %H:%M}. Không gọi API.*",
        "",
        "## Đoạn văn dùng để đo",
        "",
        FENCE + "text", text, FENCE,
        "",
        f"Số từ (tách theo khoảng trắng): **{vi['words']}**  ",
        f"Ước lượng thô của Part 1 (`số từ / {ROUGH_RATIO}`): "
        f"**{vi['rough']:.0f} token**",
        "",
        "## Kết quả đếm",
        "",
        "| Bộ mã hóa | Model dùng bộ này | Token thật | Token/từ | Ước lượng thô lệch |",
        "|---|---|---|---|---|",
    ]
    for r in vi["rows"]:
        verdict = "thiếu" if r["deviation"] < 0 else "thừa"
        lines.append(
            f"| `{r['encoding']}` | {r['models']} | **{r['tokens']}** | "
            f"{r['per_word']:.2f} | {r['deviation']:+.1f}% (dự toán {verdict}) |"
        )

    lines += [
        "",
        f"Cùng nội dung bằng tiếng Anh ({en['words']} từ) để đối chứng:",
        "",
        "| Bộ mã hóa | Token | Token/từ |",
        "|---|---|---|",
    ]
    for r in en["rows"]:
        lines.append(f"| `{r['encoding']}` | {r['tokens']} | {r['per_word']:.2f} |")

    lines += [
        "",
        "## count_tokens() theo model đang cấu hình",
        "",
        f"`.env` đang đặt model **`{OPENAI_MODEL}`**:",
        "",
        f"- `count_tokens(text)` → **{count_tokens(text)} token**",
        f"- `count_tokens(text, model=\"gpt-4o\")` → "
        f"**{count_tokens(text, model='gpt-4o')} token**",
        "",
    ]
    if "gemini" in OPENAI_MODEL or "llama" in OPENAI_MODEL:
        lines += [
            "> ⚠️ tiktoken **không có** bảng mã hóa cho model này, nên "
            "`count_tokens(text)` rơi vào nhánh dự phòng `len(text) // 4` — đó là "
            "ước lượng theo ký tự, **không phải** đếm token thật. Muốn có số liệu "
            "đúng cho Câu 2.2 phải truyền `model=\"gpt-4o\"` tường minh.",
            "",
        ]

    lines += [
        "## Vì sao tiếng Việt tốn token hơn",
        "",
        "Chữ có dấu bị tách thành nhiều mảnh, trong khi từ tiếng Anh thông dụng "
        "thường gọn trong một token (`o200k_base`):",
        "",
        "| Từ | Số token | Bị tách thành |",
        "|---|---|---|",
    ]
    for word, n, pieces in samples:
        pretty = " + ".join(f"`{p}`" for p in pieces)
        lines.append(f"| `{word}` | {n} | {pretty} |")

    lines += ["", ""]
    return "\n".join(lines)


def main() -> None:
    if len(sys.argv) > 1:
        text = Path(sys.argv[1]).read_text(encoding="utf-8").strip()
        print(f"Đọc đoạn văn từ: {sys.argv[1]}")
    else:
        text = DEFAULT_TEXT

    try:
        vi = measure(text)
        en = measure(ENGLISH_TEXT)
        samples = sample_breakdown()
    except Exception as e:
        print(f"Không dùng được tiktoken ({type(e).__name__}: {e}).")
        print("Lần chạy đầu cần mạng để tải bảng mã hóa về cache.")
        sys.exit(1)

    print(f"Số từ: {vi['words']}   |   Ước lượng thô: {vi['rough']:.0f} token\n")
    print(f"{'Bộ mã hóa':<14}{'Token':>7}{'Token/từ':>11}{'Thô lệch':>12}")
    for r in vi["rows"]:
        print(f"{r['encoding']:<14}{r['tokens']:>7}{r['per_word']:>11.2f}"
              f"{r['deviation']:>11.1f}%")

    print(f"\ncount_tokens(text) với {OPENAI_MODEL}: {count_tokens(text)} token")
    print(f"count_tokens(text, model='gpt-4o')      : "
          f"{count_tokens(text, model='gpt-4o')} token")

    OUTPUT_MD.write_text(build_markdown(text, vi, en, samples), encoding="utf-8")
    print(f"\nĐã ghi báo cáo: {OUTPUT_MD.relative_to(LAB_DIR)}")


if __name__ == "__main__":
    main()
