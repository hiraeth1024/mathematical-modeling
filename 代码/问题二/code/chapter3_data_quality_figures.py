#!/usr/bin/env python3
"""Draw Chapter 3 data-quality figures for Brent crude data.

Generated figures:
  - Fig. 3-1 missing-value counts by field
  - Fig. 3-2 boxplot of Brent close prices

The script uses only Python standard library modules and writes SVG files.
"""

from __future__ import annotations

import csv
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CSV_PATH = ROOT / "附件1.布伦特原油期货主力合约价格数据.csv"
OUT_DIR = ROOT / "代码" / "问题二" / "results" / "chapter3_figures"
OUT_DIR.mkdir(parents=True, exist_ok=True)

FIELD_LABELS = {
    "time": "交易日期",
    "thscode": "合约代码",
    "preClose": "前收盘价",
    "open": "开盘价",
    "high": "最高价",
    "low": "最低价",
    "close": "收盘价",
}


def is_missing(value: str) -> bool:
    return value is None or value.strip() == "" or value.strip().upper() == "NA"


def read_data() -> list[dict[str, str]]:
    with CSV_PATH.open("r", encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


def percentile(values: list[float], p: float) -> float:
    if not values:
        raise ValueError("empty values")
    xs = sorted(values)
    pos = (len(xs) - 1) * p
    lo = math.floor(pos)
    hi = math.ceil(pos)
    if lo == hi:
        return xs[lo]
    return xs[lo] * (hi - pos) + xs[hi] * (pos - lo)


def svg_text(x: float, y: float, text: str, *, size=14, anchor="middle", weight="normal", rotate=None) -> str:
    transform = f' transform="rotate({rotate} {x} {y})"' if rotate is not None else ""
    return (
        f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" dominant-baseline="middle"'
        f'{transform} font-family="Songti SC, SimSun, Microsoft YaHei, PingFang SC, Arial Unicode MS, serif"'
        f' font-size="{size}" font-weight="{weight}">{text}</text>'
    )


def draw_missing_bar(rows: list[dict[str, str]]) -> Path:
    fields = list(rows[0].keys())
    counts = [sum(1 for row in rows if is_missing(row.get(field, ""))) for field in fields]

    width, height = 980, 580
    left, right, top, bottom = 88, 38, 70, 105
    plot_w = width - left - right
    plot_h = height - top - bottom
    max_count = max(max(counts), 1)
    y_max = max_count if max_count <= 5 else math.ceil(max_count / 5) * 5

    def sx(i: int) -> float:
        return left + (i + 0.5) * plot_w / len(fields)

    def sy(v: float) -> float:
        return top + (y_max - v) / y_max * plot_h

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        svg_text(width / 2, 32, "图3-1 布伦特原油价格数据缺失值统计图", size=22, weight="bold"),
    ]

    # Grid and axis.
    for tick in range(0, y_max + 1):
        y = sy(tick)
        parts.append(f'<line x1="{left}" y1="{y:.1f}" x2="{width-right}" y2="{y:.1f}" stroke="#E5E5E5"/>')
        parts.append(svg_text(left - 12, y, str(tick), size=12, anchor="end"))
    parts.append(f'<line x1="{left}" y1="{height-bottom}" x2="{width-right}" y2="{height-bottom}" stroke="#333" stroke-width="1.5"/>')
    parts.append(f'<line x1="{left}" y1="{top}" x2="{left}" y2="{height-bottom}" stroke="#333" stroke-width="1.5"/>')

    bar_w = plot_w / len(fields) * 0.58
    for i, (field, count) in enumerate(zip(fields, counts)):
        x = sx(i) - bar_w / 2
        y = sy(count)
        bar_h = height - bottom - y
        parts.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_w:.1f}" height="{bar_h:.1f}" fill="#4E79A7"/>')
        parts.append(svg_text(sx(i), y - 14, str(count), size=13, weight="bold"))
        parts.append(svg_text(sx(i), height - bottom + 28, FIELD_LABELS.get(field, field), size=13, rotate=-25))

    parts.append(svg_text(width / 2, height - 22, "字段名称", size=15))
    parts.append(svg_text(24, height / 2, "缺失值数量", size=15, rotate=-90))
    parts.append("</svg>")

    path = OUT_DIR / "fig3_1_missing_values.svg"
    path.write_text("\n".join(parts), encoding="utf-8")
    return path


def draw_close_boxplot(rows: list[dict[str, str]]) -> Path:
    closes = [float(row["close"]) for row in rows if not is_missing(row.get("close", ""))]
    q1 = percentile(closes, 0.25)
    q2 = percentile(closes, 0.50)
    q3 = percentile(closes, 0.75)
    iqr = q3 - q1
    lower_fence = q1 - 1.5 * iqr
    upper_fence = q3 + 1.5 * iqr
    whisker_low = min(v for v in closes if v >= lower_fence)
    whisker_high = max(v for v in closes if v <= upper_fence)
    outliers = [v for v in closes if v < lower_fence or v > upper_fence]

    width, height = 720, 620
    left, right, top, bottom = 105, 70, 70, 88
    plot_h = height - top - bottom
    y_min = math.floor(min(closes) / 10) * 10
    y_max = math.ceil(max(closes) / 10) * 10

    def sy(v: float) -> float:
        return top + (y_max - v) / (y_max - y_min) * plot_h

    cx = (width - left - right) / 2 + left
    box_w = 170
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        svg_text(width / 2, 32, "图3-2 布伦特原油收盘价箱线图", size=22, weight="bold"),
    ]

    for tick in range(int(y_min), int(y_max) + 1, 10):
        y = sy(tick)
        parts.append(f'<line x1="{left}" y1="{y:.1f}" x2="{width-right}" y2="{y:.1f}" stroke="#E5E5E5"/>')
        parts.append(svg_text(left - 12, y, str(tick), size=12, anchor="end"))
    parts.append(f'<line x1="{left}" y1="{height-bottom}" x2="{width-right}" y2="{height-bottom}" stroke="#333" stroke-width="1.5"/>')
    parts.append(f'<line x1="{left}" y1="{top}" x2="{left}" y2="{height-bottom}" stroke="#333" stroke-width="1.5"/>')

    # Whiskers.
    parts.append(f'<line x1="{cx:.1f}" y1="{sy(whisker_high):.1f}" x2="{cx:.1f}" y2="{sy(q3):.1f}" stroke="#333" stroke-width="2"/>')
    parts.append(f'<line x1="{cx:.1f}" y1="{sy(q1):.1f}" x2="{cx:.1f}" y2="{sy(whisker_low):.1f}" stroke="#333" stroke-width="2"/>')
    parts.append(f'<line x1="{cx-box_w/3:.1f}" y1="{sy(whisker_high):.1f}" x2="{cx+box_w/3:.1f}" y2="{sy(whisker_high):.1f}" stroke="#333" stroke-width="2"/>')
    parts.append(f'<line x1="{cx-box_w/3:.1f}" y1="{sy(whisker_low):.1f}" x2="{cx+box_w/3:.1f}" y2="{sy(whisker_low):.1f}" stroke="#333" stroke-width="2"/>')

    # IQR box and median.
    parts.append(
        f'<rect x="{cx-box_w/2:.1f}" y="{sy(q3):.1f}" width="{box_w:.1f}" height="{sy(q1)-sy(q3):.1f}" '
        'fill="#F4B183" stroke="#333" stroke-width="2"/>'
    )
    parts.append(f'<line x1="{cx-box_w/2:.1f}" y1="{sy(q2):.1f}" x2="{cx+box_w/2:.1f}" y2="{sy(q2):.1f}" stroke="#C00000" stroke-width="3"/>')

    # Outliers with deterministic horizontal jitter.
    for i, value in enumerate(outliers):
        jitter = ((i % 9) - 4) * 5.0
        parts.append(f'<circle cx="{cx+jitter:.1f}" cy="{sy(value):.1f}" r="3.2" fill="white" stroke="#4E79A7" stroke-width="1.5"/>')

    parts.append(svg_text(cx, height - bottom + 32, "收盘价", size=15))
    parts.append(svg_text(28, height / 2, "价格（美元/桶）", size=15, rotate=-90))
    note = f"Q1={q1:.2f}  中位数={q2:.2f}  Q3={q3:.2f}  异常点={len(outliers)}个"
    parts.append(svg_text(width / 2, height - 24, note, size=13))
    parts.append("</svg>")

    path = OUT_DIR / "fig3_2_close_boxplot.svg"
    path.write_text("\n".join(parts), encoding="utf-8")
    return path


def main() -> None:
    rows = read_data()
    fig1 = draw_missing_bar(rows)
    fig2 = draw_close_boxplot(rows)
    print(f"已生成：{fig1}")
    print(f"已生成：{fig2}")


if __name__ == "__main__":
    main()
