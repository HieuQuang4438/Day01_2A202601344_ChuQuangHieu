"""
Câu 1.1 — Độ nhạy của temperature (exercises.md)

Gọi call_openai với temperature 0.0 / 0.7 / 1.2 / 1.8 trên cùng một prompt.
Mỗi mức chạy RUNS lần để thấy được tính ổn định: temperature thấp thì các
lần chạy gần như giống nhau, temperature cao thì mỗi lần một khác.

Kết quả vừa in ra màn hình, vừa ghi thành file markdown cạnh script này.

Chạy (từ thư mục gốc của lab):
    python exercise_scripts/exercise_1_1_temperature.py
"""

import re
import sys
import time
from datetime import datetime
from pathlib import Path

# Script nằm trong thư mục con nên thư mục gốc của lab chưa có trong sys.path
# -> thêm vào trước khi import template
LAB_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(LAB_DIR))

from template import OPENAI_MODEL, call_openai  # noqa: E402

# Console Windows mặc định là cp1252 — không in được tiếng Việt nếu không đổi
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

PROMPT = "Hãy kể cho tôi một sự thật thú vị về Hà Nội."
TEMPERATURES = [0.0, 0.7, 1.2, 1.8]
RUNS = 2            # số lần chạy mỗi mức temperature
MAX_TOKENS = 1500   # rộng tay: Gemini tính cả thinking token vào max_tokens
TOP_P = 1.0         # tắt nucleus sampling để CHỈ temperature thay đổi
PAUSE = 2.0         # nghỉ giữa các lời gọi, tránh đụng giới hạn mỗi phút
MAX_RETRIES = 2     # số lần thử lại khi API báo lỗi tạm thời (429)

# Bậc miễn phí giới hạn số lượt gọi MỖI NGÀY cho TỪNG model. Hết hạn mức của
# model này thì truyền tên model khác vào để chạy tiếp:
#     python exercise_scripts/exercise_1_1_temperature.py gemini-3.5-flash-lite
MODEL = sys.argv[1] if len(sys.argv) > 1 else OPENAI_MODEL

OUTPUT_MD = Path(__file__).resolve().parent / "cau_1_1_temperature.md"

# Phản hồi của model có sẵn markdown (###, **) — bọc trong fence 4 backtick
# để giữ nguyên văn, không phá cấu trúc file báo cáo
FENCE = "````"


def retry_delay(exc: Exception, fallback: float) -> float:
    """API 429 thường kèm 'Please retry in 31.1s' — dùng đúng con số đó nếu có."""
    match = re.search(r"retry in ([\d.]+)s", str(exc))
    if match:
        return min(float(match.group(1)) + 1, 90.0)
    return fallback


def call_with_retry(temp: float) -> tuple[str, float]:
    """Gọi call_openai, thử lại với exponential backoff khi gặp lỗi tạm thời."""
    for attempt in range(MAX_RETRIES + 1):
        try:
            return call_openai(
                PROMPT,
                model=MODEL,
                temperature=temp,
                top_p=TOP_P,
                max_tokens=MAX_TOKENS,
            )
        except Exception as e:
            if attempt == MAX_RETRIES:
                raise
            delay = retry_delay(e, fallback=2.0 * (2 ** attempt))
            print(f"    (lỗi tạm thời — chờ {delay:.0f}s rồi thử lại)")
            time.sleep(delay)


def run_experiment() -> dict[float, list[dict]]:
    """Chạy toàn bộ thí nghiệm, trả về {temperature: [{text, latency, error}]}."""
    results = {}
    for temp in TEMPERATURES:
        print("=" * 72)
        print(f"TEMPERATURE = {temp}")
        print("=" * 72)
        runs = []
        for i in range(1, RUNS + 1):
            try:
                text, latency = call_with_retry(temp)
                text = text.strip()
                runs.append({"text": text, "latency": latency, "error": None})
                print(f"\n--- Lần {i}  [{latency:.2f}s, {len(text)} ký tự] ---")
                print(text)
            except Exception as e:
                msg = f"{type(e).__name__}: {e}"
                runs.append({"text": "", "latency": 0.0, "error": msg})
                print(f"\n--- Lần {i}  LỖI: {msg}")
            finally:
                time.sleep(PAUSE)
        results[temp] = runs
        print()
    return results


def build_markdown(results: dict[float, list[dict]]) -> str:
    """Dựng nội dung file báo cáo markdown từ kết quả thí nghiệm."""
    lines = [
        "# Câu 1.1 — Độ nhạy của temperature",
        "",
        f"*Sinh tự động bởi `exercise_scripts/{Path(__file__).name}` "
        f"lúc {datetime.now():%Y-%m-%d %H:%M}.*",
        "",
        "## Cấu hình thí nghiệm",
        "",
        "| Tham số | Giá trị |",
        "|---|---|",
        f"| Model | `{MODEL}` |",
        f"| Prompt | {PROMPT} |",
        f"| Temperature | {', '.join(str(t) for t in TEMPERATURES)} |",
        f"| top_p | {TOP_P} (tắt nucleus sampling để chỉ temperature thay đổi) |",
        f"| max_tokens | {MAX_TOKENS} |",
        f"| Số lần chạy mỗi mức | {RUNS} |",
        "",
        "## Bảng tổng hợp",
        "",
        "| Temp | Số lần OK | Độ dài TB (ký tự) | Độ trễ TB | Các lần chạy giống nhau? |",
        "|---|---|---|---|---|",
    ]

    for temp, runs in results.items():
        ok = [r for r in runs if r["error"] is None]
        if not ok:
            lines.append(f"| {temp} | 0 | — | — | — |")
            continue
        avg_len = sum(len(r["text"]) for r in ok) // len(ok)
        avg_lat = sum(r["latency"] for r in ok) / len(ok)
        identical = "**có**" if len({r["text"] for r in ok}) == 1 else "không"
        lines.append(
            f"| {temp} | {len(ok)}/{RUNS} | {avg_len} | {avg_lat:.2f}s | {identical} |"
        )

    lines += ["", "## Phản hồi đầy đủ", ""]

    for temp, runs in results.items():
        lines += [f"### Temperature = {temp}", ""]
        for i, r in enumerate(runs, start=1):
            if r["error"]:
                lines += [f"#### Lần {i} — LỖI", "", f"`{r['error']}`", ""]
                continue
            lines += [
                f"#### Lần {i} — {r['latency']:.2f}s, {len(r['text'])} ký tự",
                "",
                FENCE + "text",
                r["text"],
                FENCE,
                "",
            ]

    return "\n".join(lines) + "\n"


def main() -> None:
    print(f"Model: {MODEL}")
    print(f"Prompt: {PROMPT}")
    print(f"Mỗi mức chạy {RUNS} lần, top_p={TOP_P} (chỉ đổi temperature)\n")

    results = run_experiment()

    print("=" * 72)
    print("BẢNG TỔNG HỢP")
    print("=" * 72)
    print(f"{'Temp':<8}{'Số lần OK':<12}{'Độ dài TB':<12}{'Giống nhau?'}")
    for temp, runs in results.items():
        ok = [r for r in runs if r["error"] is None]
        if not ok:
            print(f"{temp:<8}{'0':<12}{'—':<12}—")
            continue
        avg_len = sum(len(r["text"]) for r in ok) // len(ok)
        identical = "có" if len({r["text"] for r in ok}) == 1 else "không"
        print(f"{temp:<8}{len(ok):<12}{avg_len:<12}{identical}")

    OUTPUT_MD.write_text(build_markdown(results), encoding="utf-8")
    print(f"\nĐã ghi báo cáo: {OUTPUT_MD.relative_to(LAB_DIR)}")
    print(
        "Gợi ý quan sát: temperature càng cao thì các lần chạy càng khác nhau;"
        "\nđể ý mức nào bắt đầu sai ngữ pháp hoặc lủng củng — đó là câu trả lời"
        "\ncho Câu 1.1."
    )


if __name__ == "__main__":
    main()
