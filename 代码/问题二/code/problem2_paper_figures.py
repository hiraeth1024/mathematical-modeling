#!/usr/bin/env python3
"""Generate paper-ready figures and tables for Problem 2.

The script uses only Python standard library modules. It reads the scenario
paths produced by problem2_oil_model.py and writes SVG figures plus CSV tables.
"""

from __future__ import annotations

import csv
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
FIG_DIR = RESULTS / "paper_figures"
TABLE_DIR = RESULTS / "paper_tables"
SCENARIOS = {
    "optimistic": "乐观情景",
    "baseline": "基准情景",
    "pessimistic": "悲观情景",
}
COLORS = {
    "optimistic": "#2ca02c",
    "baseline": "#1f77b4",
    "pessimistic": "#d62728",
    "bypass": "#4e79a7",
    "extra_output": "#59a14f",
    "strategic_release": "#f28e2b",
    "commercial_draw": "#b07aa1",
    "risk": "#d62728",
    "stock": "#1f77b4",
}


def read_rows(path: Path) -> list[dict[str, float]]:
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        return [{k: float(v) for k, v in row.items()} for row in csv.DictReader(file)]


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def svg_header(width: int, height: int, title: str) -> list[str]:
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        f'<text x="{width / 2}" y="30" text-anchor="middle" font-family="Arial, PingFang SC, Microsoft YaHei" font-size="18">{title}</text>',
    ]


def line_chart(
    series: dict[str, list[tuple[float, float]]],
    title: str,
    y_label: str,
    path: Path,
    y_min: float | None = None,
    y_max: float | None = None,
) -> None:
    width, height = 920, 540
    left, right, top, bottom = 78, 32, 50, 65
    xs = [x for values in series.values() for x, _ in values]
    ys = [y for values in series.values() for _, y in values]
    min_x, max_x = min(xs), max(xs)
    min_y = math.floor((min(ys) if y_min is None else y_min) / 10.0) * 10.0
    max_y = math.ceil((max(ys) if y_max is None else y_max) / 10.0) * 10.0

    def sx(x: float) -> float:
        return left + (x - min_x) / (max_x - min_x) * (width - left - right)

    def sy(y: float) -> float:
        return top + (max_y - y) / (max_y - min_y) * (height - top - bottom)

    parts = svg_header(width, height, title)
    for tick in range(int(min_y), int(max_y) + 1, max(10, int((max_y - min_y) / 6))):
        yy = sy(tick)
        parts.append(f'<line x1="{left}" y1="{yy:.1f}" x2="{width-right}" y2="{yy:.1f}" stroke="#dddddd"/>')
        parts.append(f'<text x="{left-10}" y="{yy+4:.1f}" text-anchor="end" font-family="Arial" font-size="12">{tick}</text>')
    for tick in range(int(min_x), int(max_x) + 1, 15):
        xx = sx(tick)
        parts.append(f'<line x1="{xx:.1f}" y1="{top}" x2="{xx:.1f}" y2="{height-bottom}" stroke="#eeeeee"/>')
        parts.append(f'<text x="{xx:.1f}" y="{height-bottom+22}" text-anchor="middle" font-family="Arial" font-size="12">{tick}</text>')
    parts.append(f'<line x1="{left}" y1="{height-bottom}" x2="{width-right}" y2="{height-bottom}" stroke="#333"/>')
    parts.append(f'<line x1="{left}" y1="{top}" x2="{left}" y2="{height-bottom}" stroke="#333"/>')
    parts.append(f'<text x="{width/2}" y="{height-18}" text-anchor="middle" font-family="Arial, PingFang SC, Microsoft YaHei" font-size="13">封锁后天数</text>')
    parts.append(f'<text x="18" y="{height/2}" transform="rotate(-90 18 {height/2})" text-anchor="middle" font-family="Arial, PingFang SC, Microsoft YaHei" font-size="13">{y_label}</text>')

    for idx, (name, values) in enumerate(series.items()):
        key = next((k for k, label in SCENARIOS.items() if label == name), name)
        color = COLORS.get(key, COLORS.get(name, "#333333"))
        points = " ".join(f"{sx(x):.1f},{sy(y):.1f}" for x, y in values)
        parts.append(f'<polyline fill="none" stroke="{color}" stroke-width="2.4" points="{points}"/>')
        lx, ly = width - 185, 70 + idx * 24
        parts.append(f'<line x1="{lx}" y1="{ly}" x2="{lx+24}" y2="{ly}" stroke="{color}" stroke-width="3"/>')
        parts.append(f'<text x="{lx+32}" y="{ly+5}" font-family="Arial, PingFang SC, Microsoft YaHei" font-size="13">{name}</text>')
    parts.append("</svg>")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(parts), encoding="utf-8")


def stacked_area_chart(rows: list[dict[str, float]], path: Path) -> None:
    width, height = 920, 540
    left, right, top, bottom = 78, 32, 50, 65
    keys = ["bypass", "extra_output", "strategic_release", "commercial_draw"]
    labels = ["绕道运输", "其他产油国增产", "战略储备释放", "商业库存释放"]
    max_total = max(sum(row[k] for k in keys) for row in rows)
    min_x, max_x = rows[0]["day"], rows[-1]["day"]
    max_y = math.ceil(max_total)

    def sx(x: float) -> float:
        return left + (x - min_x) / (max_x - min_x) * (width - left - right)

    def sy(y: float) -> float:
        return top + (max_y - y) / max_y * (height - top - bottom)

    parts = svg_header(width, height, "图5-2 基准情景下中长期供给调节分解")
    for tick in range(0, int(max_y) + 1, 2):
        yy = sy(tick)
        parts.append(f'<line x1="{left}" y1="{yy:.1f}" x2="{width-right}" y2="{yy:.1f}" stroke="#dddddd"/>')
        parts.append(f'<text x="{left-10}" y="{yy+4:.1f}" text-anchor="end" font-family="Arial" font-size="12">{tick}</text>')
    lower = [0.0] * len(rows)
    for idx, key in enumerate(keys):
        upper = [lower[i] + rows[i][key] for i in range(len(rows))]
        top_points = [f"{sx(rows[i]['day']):.1f},{sy(upper[i]):.1f}" for i in range(len(rows))]
        bottom_points = [f"{sx(rows[i]['day']):.1f},{sy(lower[i]):.1f}" for i in range(len(rows) - 1, -1, -1)]
        color = COLORS[key]
        parts.append(f'<polygon points="{" ".join(top_points + bottom_points)}" fill="{color}" opacity="0.72"/>')
        lower = upper
        lx, ly = width - 210, 70 + idx * 24
        parts.append(f'<rect x="{lx}" y="{ly-10}" width="18" height="12" fill="{color}" opacity="0.72"/>')
        parts.append(f'<text x="{lx+26}" y="{ly}" font-family="Arial, PingFang SC, Microsoft YaHei" font-size="13">{labels[idx]}</text>')
    parts.append(f'<line x1="{left}" y1="{height-bottom}" x2="{width-right}" y2="{height-bottom}" stroke="#333"/>')
    parts.append(f'<line x1="{left}" y1="{top}" x2="{left}" y2="{height-bottom}" stroke="#333"/>')
    parts.append(f'<text x="{width/2}" y="{height-18}" text-anchor="middle" font-family="Arial, PingFang SC, Microsoft YaHei" font-size="13">封锁后天数</text>')
    parts.append(f'<text x="18" y="{height/2}" transform="rotate(-90 18 {height/2})" text-anchor="middle" font-family="Arial, PingFang SC, Microsoft YaHei" font-size="13">调节量（百万桶/日）</text>')
    parts.append("</svg>")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(parts), encoding="utf-8")


def elasticity_chart(path: Path) -> None:
    p0, d0, epsilon = 75.0, 100.0, -0.18
    quantities = [86 + i * 0.25 for i in range(57)]
    demand_curve = [(q, p0 * (q / d0) ** (1.0 / epsilon)) for q in quantities]
    width, height = 920, 540
    left, right, top, bottom = 78, 32, 50, 65
    min_x, max_x = 86.0, 100.0
    min_y, max_y = 70.0, 190.0

    def sx(x: float) -> float:
        return left + (x - min_x) / (max_x - min_x) * (width - left - right)

    def sy(y: float) -> float:
        return top + (max_y - y) / (max_y - min_y) * (height - top - bottom)

    parts = svg_header(width, height, "图5-4 长期需求弹性下的供需平衡点")
    for tick in range(70, 191, 20):
        yy = sy(tick)
        parts.append(f'<line x1="{left}" y1="{yy:.1f}" x2="{width-right}" y2="{yy:.1f}" stroke="#dddddd"/>')
        parts.append(f'<text x="{left-10}" y="{yy+4:.1f}" text-anchor="end" font-family="Arial" font-size="12">{tick}</text>')
    points = " ".join(f"{sx(q):.1f},{sy(p):.1f}" for q, p in demand_curve)
    parts.append(f'<polyline fill="none" stroke="#333333" stroke-width="2.4" points="{points}"/>')
    for label, supply, price, color in [
        ("乐观", 96.5, 83.91, COLORS["optimistic"]),
        ("基准", 94.0, 105.77, COLORS["baseline"]),
        ("悲观", 89.5, 138.90, COLORS["pessimistic"]),
    ]:
        xx, yy = sx(supply), sy(price)
        parts.append(f'<line x1="{xx:.1f}" y1="{top}" x2="{xx:.1f}" y2="{height-bottom}" stroke="{color}" stroke-dasharray="6,5"/>')
        parts.append(f'<circle cx="{xx:.1f}" cy="{yy:.1f}" r="5" fill="{color}"/>')
        parts.append(f'<text x="{xx+8:.1f}" y="{yy-8:.1f}" font-family="Arial, PingFang SC, Microsoft YaHei" font-size="13">{label}({price:.1f})</text>')
    parts.append(f'<line x1="{left}" y1="{height-bottom}" x2="{width-right}" y2="{height-bottom}" stroke="#333"/>')
    parts.append(f'<line x1="{left}" y1="{top}" x2="{left}" y2="{height-bottom}" stroke="#333"/>')
    parts.append(f'<text x="{width/2}" y="{height-18}" text-anchor="middle" font-family="Arial, PingFang SC, Microsoft YaHei" font-size="13">有效供给/需求（百万桶/日）</text>')
    parts.append(f'<text x="18" y="{height/2}" transform="rotate(-90 18 {height/2})" text-anchor="middle" font-family="Arial, PingFang SC, Microsoft YaHei" font-size="13">油价（美元/桶）</text>')
    parts.append("</svg>")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(parts), encoding="utf-8")


def main() -> None:
    paths = {
        name: read_rows(RESULTS / f"problem2_{name}_path.csv")
        for name in SCENARIOS
    }

    line_chart(
        {SCENARIOS[name]: [(r["day"], r["price"]) for r in rows] for name, rows in paths.items()},
        "图5-1 三种情景下90-180天油价预测路径",
        "油价（美元/桶）",
        FIG_DIR / "fig5_1_price_paths.svg",
        y_min=70,
        y_max=180,
    )
    stacked_area_chart(paths["baseline"], FIG_DIR / "fig5_2_supply_adjustment.svg")
    line_chart(
        {
            "商业库存": [(r["day"], r["commercial_stock"]) for r in paths["pessimistic"]],
            "风险溢价": [(r["day"], r["risk_premium"]) for r in paths["pessimistic"]],
        },
        "图5-3 悲观情景下库存消耗与风险溢价",
        "库存（百万桶）/风险溢价（美元/桶）",
        FIG_DIR / "fig5_3_stock_risk.svg",
        y_min=0,
        y_max=140,
    )
    elasticity_chart(FIG_DIR / "fig5_4_elasticity_equilibrium.svg")

    write_csv(TABLE_DIR / "table5_1_variables.csv", [
        {"符号": "Q0", "含义": "战前全球原油供给", "取值": "100", "单位": "百万桶/日"},
        {"符号": "D0", "含义": "战前全球原油需求", "取值": "100", "单位": "百万桶/日"},
        {"符号": "P0", "含义": "封锁前布伦特基准价", "取值": "75", "单位": "美元/桶"},
        {"符号": "epsilon", "含义": "长期需求价格弹性", "取值": "-0.18", "单位": "-"},
        {"符号": "lambda", "含义": "价格向均衡点收敛速度", "取值": "0.16", "单位": "日^-1"},
        {"符号": "Imin", "含义": "商业库存风险阈值", "取值": "90", "单位": "百万桶"},
    ])
    write_csv(TABLE_DIR / "table5_2_scenarios.csv", [
        {"情景": "乐观情景", "有效中断": "14", "增产上限": "5.5", "战略储备后期释放": "3.0", "第90天库存": "390", "解释": "运输瓶颈缓解、替代供给较强"},
        {"情景": "基准情景", "有效中断": "16", "增产上限": "4.5", "战略储备后期释放": "2.0", "第90天库存": "355", "解释": "供应替代部分生效但缺口仍存在"},
        {"情景": "悲观情景", "有效中断": "18", "增产上限": "3.0", "战略储备后期释放": "1.0", "第90天库存": "130", "解释": "库存接近枯竭并触发风险溢价"},
    ])
    with (RESULTS / "problem2_summary.csv").open("r", encoding="utf-8-sig", newline="") as file:
        summary_rows = list(csv.DictReader(file))
    write_csv(TABLE_DIR / "table5_3_results.csv", [
        {
            "情景": SCENARIOS[row["scenario"]],
            "第90天价格": row["day90_price"],
            "第180天预测价格": row["day180_price"],
            "第180天供需均衡价": row["day180_equilibrium"],
            "第180天商业库存": row["day180_stock"],
            "第180天风险溢价": row["day180_risk"],
        }
        for row in summary_rows
    ])
    write_csv(TABLE_DIR / "table5_4_figures.csv", [
        {"图号": "图5-1", "图名": "三种情景下90-180天油价预测路径", "对应章节": "5.1 问题二分析", "文件": "fig5_1_price_paths.svg"},
        {"图号": "图5-2", "图名": "基准情景下中长期供给调节分解", "对应章节": "5.2.1 其他产油国增产响应建模", "文件": "fig5_2_supply_adjustment.svg"},
        {"图号": "图5-3", "图名": "悲观情景下库存消耗与风险溢价", "对应章节": "5.2.3 库存消耗与运输瓶颈约束", "文件": "fig5_3_stock_risk.svg"},
        {"图号": "图5-4", "图名": "长期需求弹性下的供需平衡点", "对应章节": "5.2.2 长期需求价格弹性修正", "文件": "fig5_4_elasticity_equilibrium.svg"},
    ])
    print(f"figures: {FIG_DIR}")
    print(f"tables: {TABLE_DIR}")


if __name__ == "__main__":
    main()
