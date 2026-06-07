#!/usr/bin/env python3
"""Draw the solution-process flowchart for Problem 1 as SVG.

No third-party packages are required. The chart summarizes the short-term
dynamic supply-demand balance model for 0-90 days after the Hormuz blockade.
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


class Canvas:
    def __init__(self) -> None:
        self.parts: list[str] = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
            "<defs>",
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

    def text(self, x, y, text, size=30, weight="normal", anchor="middle", color="#000", line_gap=1.18):
        lines = text.split("\n")
        dy0 = -(len(lines) - 1) * size * line_gap / 2
        self.parts.append(
            f'<text x="{x}" y="{y}" text-anchor="{anchor}" dominant-baseline="middle" '
            f'font-family="{FONT}" font-size="{size}" font-weight="{weight}" fill="{color}">'
        )
        for i, line in enumerate(lines):
            self.parts.append(f'<tspan x="{x}" dy="{dy0 if i == 0 else size * line_gap}">{esc(line)}</tspan>')
        self.parts.append("</text>")

    def box(self, x, y, w, h, text, fill="#F7F7F7", rx=0, size=28, weight="normal"):
        self.rect(x, y, w, h, fill, sw=2.2, rx=rx)
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

    # Background bands.
    c.rect(80, 55, 1340, 245, "#FCE4D6", stroke="#D9D9D9", sw=1)
    c.rect(80, 300, 1340, 520, "#EAF2FF", stroke="#D9D9D9", sw=1)
    c.rect(80, 820, 1340, 455, "#F3F3F3", stroke="#D9D9D9", sw=1)
    c.rect(80, 1275, 1340, 570, "#E8F4DF", stroke="#D9D9D9", sw=1)

    # Start and input.
    c.box(620, 80, 260, 65, "开始", fill="#FCE4D6", rx=32, size=32)
    c.arrow(750, 145, 750, 185, sw=2.8)
    c.box(455, 185, 590, 68, "读取价格数据与基础供需参数", fill="#FCE4D6", size=31, weight="bold")
    c.arrow(750, 253, 750, 330, big=True, sw=5)

    # Layer 1: short-term shock and buffer model.
    c.text(142, 560, "短期冲击\n与缓冲机制\n建模", size=24)
    y1, h1 = 405, 310
    boxes1 = [
        (190, "确定\n0—90天\n日度尺度"),
        (355, "霍尔木兹\n封锁造成\n供给中断"),
        (520, "恐慌需求\n与预期\n放大"),
        (685, "战略储备\n启动延迟\n与释放"),
        (850, "商业库存\n缓冲\n消耗"),
        (1015, "绕道运输\n能力恢复"),
        (1180, "形成实际\n有效供需\n缺口"),
    ]
    c.rect(320, 380, 1000, 360, "none", stroke="#E46C0A", sw=2.2, dash="22 16")
    for x, label in boxes1:
        c.box(x, y1, 125, h1, label, fill="#EDF4FF", size=27)
    for (x, _), (nx, _) in zip(boxes1[:-1], boxes1[1:]):
        c.arrow(x + 125, y1 + h1 / 2, nx, y1 + h1 / 2, sw=2)
    c.arrow(750, 745, 750, 865, big=True, sw=5)

    # Layer 2: price update and calibration.
    c.text(142, 1035, "日度价格\n递推与校准", size=24)
    y2, h2 = 910, 270
    left = [
        (205, "建立日度\n供需平衡\n方程"),
        (400, "引入短期\n需求价格\n弹性"),
        (595, "供需缺口\n驱动价格\n更新"),
        (790, "利用布伦特\n价格数据\n校准参数"),
    ]
    right = [
        (1040, "识别峰值\n平台期\n回落段"),
    ]
    c.rect(180, 885, 825, 320, "none", stroke="#E46C0A", sw=2.2, dash="22 16")
    c.rect(1020, 885, 200, 320, "none", stroke="#E46C0A", sw=2.2, dash="22 16")
    for x, label in left:
        c.box(x, y2, 135, h2, label, fill="#F7F7F7", size=27)
    for x, label in right:
        c.box(x, y2, 155, h2, label, fill="#F7F7F7", size=27)
    for (x, _), (nx, _) in zip(left[:-1], left[1:]):
        c.arrow(x + 135, y2 + h2 / 2, nx, y2 + h2 / 2, sw=2)
    c.arrow(left[-1][0] + 135, y2 + h2 / 2, right[0][0], y2 + h2 / 2, sw=2)
    c.arrow(750, 1215, 750, 1320, big=True, sw=5)

    # Layer 3: output.
    c.box(500, 1335, 500, 70, "输出短期油价冲击结果", fill="#E8F4DF", size=32, weight="bold")
    c.arrow(750, 1405, 750, 1450, sw=2.2)
    out = [
        (200, "0—90天\n油价动态\n演化路径"),
        (520, "价格峰值\n高位维持\n回落解释"),
        (840, "缓冲机制\n边际贡献\n分析"),
        (1160, "未突破\n200美元/桶\n原因说明"),
    ]
    for x, label in out:
        c.box(x, 1460, 230, 92, label, fill="#E8F4DF", size=25)
        c.polyline_arrow([(750, 1450), (750, 1440), (x + 115, 1440), (x + 115, 1460)], sw=1.8)

    c.box(390, 1620, 720, 70, "形成问题一动态供需平衡模型结论", fill="#E8F4DF", size=30)
    for x, _ in out:
        c.polyline_arrow([(x + 115, 1552), (x + 115, 1595), (750, 1595), (750, 1620)], sw=1.8)
    c.arrow(750, 1690, 750, 1725, sw=2.2)
    c.box(650, 1730, 200, 62, "结束", fill="#E8F4DF", rx=31, size=32)


    path = OUT_DIR / "fig4_0_problem1_solution_flowchart.svg"
    c.save(path)
    return path


if __name__ == "__main__":
    output = draw()
    print(f"已生成：{output}")
