#!/usr/bin/env python3
"""Draw the solution-process flowchart for Problem 2 as SVG.

No third-party packages are required. The output is a vector SVG that can be
inserted into Word/WPS directly, or exported to PNG by a browser or drawing
software.
"""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "results" / "paper_figures"
OUT_DIR.mkdir(parents=True, exist_ok=True)

W, H = 1500, 1850
FONT = "'Songti SC','SimSun','Microsoft YaHei','PingFang SC','Arial Unicode MS',serif"


def esc(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def lines(text: str) -> list[str]:
    return text.split("\n")


class Canvas:
    def __init__(self) -> None:
        self.parts: list[str] = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
            '<defs>',
            '<marker id="arrow" markerWidth="12" markerHeight="12" refX="10" refY="6" orient="auto" markerUnits="strokeWidth">',
            '<path d="M0,0 L12,6 L0,12 z" fill="#111"/>',
            "</marker>",
            '<marker id="bigArrow" markerWidth="22" markerHeight="22" refX="19" refY="11" orient="auto" markerUnits="userSpaceOnUse">',
            '<path d="M0,0 L22,11 L0,22 z" fill="#000"/>',
            "</marker>",
            "</defs>",
            '<rect width="100%" height="100%" fill="white"/>',
        ]

    def rect(self, x, y, w, h, fill, stroke="#333", sw=2, dash=None, rx=0):
        dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
        self.parts.append(
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" ry="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{dash_attr}/>'
        )

    def text(self, x, y, text, size=32, weight="normal", anchor="middle", color="#000", line_gap=1.18):
        ts = lines(text)
        dy0 = -(len(ts) - 1) * size * line_gap / 2
        self.parts.append(
            f'<text x="{x}" y="{y}" text-anchor="{anchor}" dominant-baseline="middle" '
            f'font-family="{FONT}" font-size="{size}" font-weight="{weight}" fill="{color}">'
        )
        for i, line in enumerate(ts):
            self.parts.append(f'<tspan x="{x}" dy="{dy0 if i == 0 else size * line_gap}">{esc(line)}</tspan>')
        self.parts.append("</text>")

    def box(self, x, y, w, h, text, fill="#F7F7F7", rx=0, size=30, weight="normal", stroke="#333"):
        self.rect(x, y, w, h, fill, stroke=stroke, sw=2.2, rx=rx)
        self.text(x + w / 2, y + h / 2, text, size=size, weight=weight)

    def arrow(self, x1, y1, x2, y2, big=False, sw=2.2):
        marker = "bigArrow" if big else "arrow"
        self.parts.append(
            f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
            f'stroke="#111" stroke-width="{sw}" marker-end="url(#{marker})"/>'
        )

    def polyline_arrow(self, pts, sw=2.0):
        points = " ".join(f"{x},{y}" for x, y in pts)
        self.parts.append(
            f'<polyline points="{points}" fill="none" stroke="#333" stroke-width="{sw}" '
            f'marker-end="url(#arrow)"/>'
        )

    def save(self, path: Path) -> None:
        self.parts.append("</svg>")
        path.write_text("\n".join(self.parts), encoding="utf-8")


def draw() -> Path:
    c = Canvas()

    # Background bands, matching the reference style.
    c.rect(80, 55, 1340, 245, "#FCE4D6", stroke="#D9D9D9", sw=1)
    c.rect(80, 300, 1340, 520, "#EAF2FF", stroke="#D9D9D9", sw=1)
    c.rect(80, 820, 1340, 455, "#F3F3F3", stroke="#D9D9D9", sw=1)
    c.rect(80, 1275, 1340, 570, "#E8F4DF", stroke="#D9D9D9", sw=1)

    # Start and data input.
    c.box(620, 80, 260, 65, "开始", fill="#FCE4D6", rx=32, size=32)
    c.arrow(750, 145, 750, 185, sw=2.8)
    c.box(490, 185, 520, 68, "数据载入与参数初始化", fill="#FCE4D6", size=32, weight="bold")
    c.arrow(750, 253, 750, 330, big=True, sw=5)

    # Layer 1: model construction.
    c.text(142, 560, "中长期\n供需调节\n模型构建", size=24)
    y1, h1 = 405, 310
    boxes1 = [
        (190, "确定\n90—\n180天\n封锁情景"),
        (355, "其他\n产油国\n增产响应\n建模"),
        (520, "绕道运输\n瓶颈约束"),
        (685, "战略储备\n释放衰减"),
        (850, "商业库存\n释放约束"),
        (1015, "长期需求\n弹性修正"),
        (1180, "形成有效\n供给序列"),
    ]
    c.rect(320, 380, 1000, 360, "none", stroke="#E46C0A", sw=2.2, dash="22 16")
    for x, label in boxes1:
        c.box(x, y1, 125, h1, label, fill="#EDF4FF", size=28)
    for (x, _), (nx, _) in zip(boxes1[:-1], boxes1[1:]):
        c.arrow(x + 125, y1 + h1 / 2, nx, y1 + h1 / 2, sw=2)
    c.arrow(750, 745, 750, 865, big=True, sw=5)

    # Layer 2: equilibrium and jump risk.
    c.text(142, 1035, "平衡点\n与跳变风险\n求解", size=24)
    y2, h2 = 910, 270
    left = [
        (215, "建立长期\n需求函数\nD(P)"),
        (430, "供需均衡\n条件\nD(P*)=S"),
        (645, "求解理论\n平衡价\nP*"),
    ]
    right = [
        (900, "库存阈值\nImin判断"),
        (1115, "风险溢价\nRisk(t)\n计算"),
    ]
    c.rect(185, 885, 650, 320, "none", stroke="#E46C0A", sw=2.2, dash="22 16")
    c.rect(870, 885, 500, 320, "none", stroke="#E46C0A", sw=2.2, dash="22 16")
    for x, label in left + right:
        c.box(x, y2, 135, h2, label, fill="#F7F7F7", size=28)
    for (x, _), (nx, _) in zip(left[:-1], left[1:]):
        c.arrow(x + 135, y2 + h2 / 2, nx, y2 + h2 / 2, sw=2)
    c.arrow(left[-1][0] + 135, y2 + h2 / 2, right[0][0], y2 + h2 / 2, sw=2)
    c.arrow(right[0][0] + 135, y2 + h2 / 2, right[1][0], y2 + h2 / 2, sw=2)
    c.arrow(750, 1215, 750, 1320, big=True, sw=5)

    # Layer 3: output and analysis.
    c.box(500, 1335, 500, 70, "输出预测与分析结果", fill="#E8F4DF", size=32, weight="bold")
    c.arrow(750, 1405, 750, 1450, sw=2.2)
    out = [
        (230, "90—180天\n油价预测路径"),
        (570, "三情景\n价格平衡区间"),
        (910, "库存跳变\n风险判断"),
    ]
    for x, label in out:
        c.box(x, 1460, 260, 78, label, fill="#E8F4DF", size=27)
        c.polyline_arrow([(750, 1450), (750, 1440), (x + 130, 1440), (x + 130, 1460)], sw=1.8)
    c.box(435, 1605, 630, 70, "调节因素敏感性与论文图表输出", fill="#E8F4DF", size=30)
    for x, _ in out:
        c.polyline_arrow([(x + 130, 1538), (x + 130, 1580), (750, 1580), (750, 1605)], sw=1.8)
    c.arrow(750, 1675, 750, 1718, sw=2.2)
    c.box(650, 1725, 200, 62, "结束", fill="#E8F4DF", rx=31, size=32)


    path = OUT_DIR / "fig5_0_problem2_solution_flowchart.svg"
    c.save(path)
    return path


if __name__ == "__main__":
    output = draw()
    print(f"已生成：{output}")
