#!/usr/bin/env python3
"""Problem 2: medium and long term oil-price adjustment model.

The model simulates days 90-180 after a Hormuz Strait blockade. It combines
long-run price elasticity, delayed supply substitution, strategic stock release,
commercial inventory drawdown, and an inventory-depletion risk premium.
"""

from __future__ import annotations

import argparse
import csv
import math
from dataclasses import dataclass, replace
from pathlib import Path


@dataclass(frozen=True)
class ModelParams:
    baseline_supply: float = 100.0
    baseline_demand: float = 100.0
    baseline_price: float = 75.0
    initial_price: float = 95.25
    long_run_elasticity: float = -0.18
    adjustment_speed: float = 0.16
    blockade_loss: float = 16.0
    bypass_day90: float = 2.4
    bypass_cap: float = 3.0
    extra_output_day90: float = 1.0
    extra_output_cap: float = 4.5
    strategic_release_day90: float = 5.0
    strategic_release_day180: float = 2.0
    commercial_stock_day90: float = 355.0
    commercial_draw_cap_day90: float = 2.0
    commercial_draw_cap_day180: float = 0.5
    demand_adaptation_day90: float = 0.0
    demand_adaptation_day180: float = 0.0
    risk_stock_threshold: float = 90.0
    risk_premium_cap: float = 38.0
    start_day: int = 90
    end_day: int = 180

    def risk_premium(self, commercial_stock: float) -> float:
        """Inventory-depletion premium in USD/barrel."""
        if commercial_stock >= self.risk_stock_threshold:
            return 0.0
        shortage_ratio = 1.0 - max(commercial_stock, 0.0) / self.risk_stock_threshold
        return self.risk_premium_cap * shortage_ratio * shortage_ratio


def ramp(day: int, start_day: int, end_day: int, start_value: float, end_value: float) -> float:
    if day <= start_day:
        return start_value
    if day >= end_day:
        return end_value
    weight = (day - start_day) / (end_day - start_day)
    return start_value + weight * (end_value - start_value)


def equilibrium_price(base_price: float, demand_scale: float, effective_supply: float, elasticity: float) -> float:
    """Solve D0 * (P/P0)^e = S for P."""
    if effective_supply <= 0:
        raise ValueError("effective_supply must be positive")
    if demand_scale <= 0:
        raise ValueError("demand_scale must be positive")
    if elasticity >= 0:
        raise ValueError("elasticity must be negative")
    return base_price * (effective_supply / demand_scale) ** (1.0 / elasticity)


def daily_components(day: int, stock: float, params: ModelParams) -> dict[str, float]:
    bypass = ramp(day, params.start_day, params.end_day, params.bypass_day90, params.bypass_cap)
    extra_output = ramp(day, params.start_day, params.end_day, params.extra_output_day90, params.extra_output_cap)
    strategic_release = ramp(
        day,
        params.start_day,
        params.end_day,
        params.strategic_release_day90,
        params.strategic_release_day180,
    )
    draw_cap = ramp(day, params.start_day, params.end_day, params.commercial_draw_cap_day90, params.commercial_draw_cap_day180)
    demand_adaptation = ramp(
        day,
        params.start_day,
        params.end_day,
        params.demand_adaptation_day90,
        params.demand_adaptation_day180,
    )
    nonstock_supply = (
        params.baseline_supply
        - params.blockade_loss
        + bypass
        + extra_output
        + strategic_release
    )
    demand_scale = params.baseline_demand - demand_adaptation
    physical_gap = max(0.0, demand_scale - nonstock_supply)
    commercial_draw = min(draw_cap, stock, physical_gap)
    effective_supply = nonstock_supply + commercial_draw
    residual_gap = max(0.0, demand_scale - effective_supply)
    return {
        "bypass": bypass,
        "extra_output": extra_output,
        "strategic_release": strategic_release,
        "commercial_draw": commercial_draw,
        "demand_scale": demand_scale,
        "nonstock_supply": nonstock_supply,
        "effective_supply": effective_supply,
        "residual_gap": residual_gap,
    }


def simulate_path(params: ModelParams) -> list[dict[str, float]]:
    rows: list[dict[str, float]] = []
    price = params.initial_price
    stock = params.commercial_stock_day90

    for day in range(params.start_day, params.end_day + 1):
        comp = daily_components(day, stock, params)
        eq_price = equilibrium_price(
            params.baseline_price,
            comp["demand_scale"],
            max(comp["effective_supply"], 1e-9),
            params.long_run_elasticity,
        )
        risk = params.risk_premium(stock)
        target_price = eq_price + risk
        price = price + params.adjustment_speed * (target_price - price)
        stock = max(0.0, stock - comp["commercial_draw"])

        row = {
            "day": float(day),
            "price": price,
            "equilibrium_price": eq_price,
            "target_price": target_price,
            "risk_premium": risk,
            "commercial_stock": stock,
        }
        row.update(comp)
        rows.append(row)

    return rows


def load_latest_close(csv_path: Path) -> float:
    latest = None
    with csv_path.open("r", encoding="utf-8-sig", newline="") as file:
        for row in csv.DictReader(file):
            close = row.get("close", "")
            if close and close != "NA":
                latest = float(close)
    if latest is None:
        raise ValueError(f"No close price found in {csv_path}")
    return latest


def resolve_csv_path(csv_path: Path) -> Path:
    """Find the Brent CSV from the current directory or nearby parent folders."""
    if csv_path.exists():
        return csv_path
    search_roots = [Path.cwd(), *Path(__file__).resolve().parents]
    for root in search_roots:
        candidate = root / csv_path.name
        if candidate.exists():
            return candidate
    raise FileNotFoundError(f"Could not find {csv_path}")


def write_rows(rows: list[dict[str, float]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    columns = list(rows[0].keys())
    with output_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: round(value, 6) for key, value in row.items()})


def scenario_params(base: ModelParams) -> dict[str, ModelParams]:
    return {
        "baseline": base,
        "optimistic": replace(
            base,
            blockade_loss=14.0,
            extra_output_cap=5.5,
            strategic_release_day180=3.0,
            commercial_stock_day90=390.0,
        ),
        "pessimistic": replace(
            base,
            blockade_loss=18.0,
            extra_output_cap=3.0,
            strategic_release_day180=1.0,
            commercial_stock_day90=130.0,
            risk_premium_cap=52.0,
        ),
    }


def plot_scenarios(results: dict[str, list[dict[str, float]]], output_path: Path) -> Path:
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        svg_path = output_path.with_suffix(".svg")
        write_svg_plot(results, svg_path)
        return svg_path

    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(9, 5.2))
    for name, rows in results.items():
        plt.plot([r["day"] for r in rows], [r["price"] for r in rows], label=name)
    plt.xlabel("Days after blockade")
    plt.ylabel("Brent price (USD/barrel)")
    plt.title("Problem 2: Medium- and long-term Brent price adjustment")
    plt.grid(True, alpha=0.25)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path, dpi=180)
    plt.close()
    return output_path


def write_svg_plot(results: dict[str, list[dict[str, float]]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    width, height = 900, 520
    left, right, top, bottom = 70, 25, 45, 65
    colors = {"baseline": "#1f77b4", "optimistic": "#2ca02c", "pessimistic": "#d62728"}
    all_days = [r["day"] for rows in results.values() for r in rows]
    all_prices = [r["price"] for rows in results.values() for r in rows]
    min_day, max_day = min(all_days), max(all_days)
    min_price = math.floor(min(all_prices) / 10.0) * 10.0
    max_price = math.ceil(max(all_prices) / 10.0) * 10.0

    def x_scale(day: float) -> float:
        return left + (day - min_day) / (max_day - min_day) * (width - left - right)

    def y_scale(price: float) -> float:
        return top + (max_price - price) / (max_price - min_price) * (height - top - bottom)

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        f'<text x="{width / 2}" y="25" text-anchor="middle" font-family="Arial" font-size="18">Problem 2: Brent price paths</text>',
    ]
    for tick in range(int(min_price), int(max_price) + 1, 20):
        y = y_scale(tick)
        parts.append(f'<line x1="{left}" y1="{y:.1f}" x2="{width-right}" y2="{y:.1f}" stroke="#dddddd"/>')
        parts.append(f'<text x="{left-10}" y="{y+4:.1f}" text-anchor="end" font-family="Arial" font-size="12">{tick}</text>')
    for tick in range(int(min_day), int(max_day) + 1, 15):
        x = x_scale(tick)
        parts.append(f'<line x1="{x:.1f}" y1="{top}" x2="{x:.1f}" y2="{height-bottom}" stroke="#eeeeee"/>')
        parts.append(f'<text x="{x:.1f}" y="{height-bottom+22}" text-anchor="middle" font-family="Arial" font-size="12">{tick}</text>')
    parts.append(f'<line x1="{left}" y1="{height-bottom}" x2="{width-right}" y2="{height-bottom}" stroke="#333333"/>')
    parts.append(f'<line x1="{left}" y1="{top}" x2="{left}" y2="{height-bottom}" stroke="#333333"/>')
    parts.append(f'<text x="{width/2}" y="{height-18}" text-anchor="middle" font-family="Arial" font-size="13">Days after blockade</text>')
    parts.append(f'<text x="18" y="{height/2}" transform="rotate(-90 18 {height/2})" text-anchor="middle" font-family="Arial" font-size="13">USD/barrel</text>')

    legend_y = 58
    for idx, (name, rows) in enumerate(results.items()):
        points = " ".join(f'{x_scale(r["day"]):.1f},{y_scale(r["price"]):.1f}' for r in rows)
        color = colors.get(name, "#333333")
        parts.append(f'<polyline fill="none" stroke="{color}" stroke-width="2.4" points="{points}"/>')
        lx = width - 175
        ly = legend_y + idx * 22
        parts.append(f'<line x1="{lx}" y1="{ly}" x2="{lx+24}" y2="{ly}" stroke="{color}" stroke-width="2.8"/>')
        parts.append(f'<text x="{lx+32}" y="{ly+4}" font-family="Arial" font-size="13">{name}</text>')
    parts.append("</svg>")
    output_path.write_text("\n".join(parts), encoding="utf-8")


def summarize(results: dict[str, list[dict[str, float]]]) -> str:
    lines = ["scenario,day90_price,day180_price,day180_equilibrium,day180_stock,day180_risk"]
    for name, rows in results.items():
        first = rows[0]
        last = rows[-1]
        lines.append(
            ",".join(
                [
                    name,
                    f"{first['price']:.2f}",
                    f"{last['price']:.2f}",
                    f"{last['equilibrium_price']:.2f}",
                    f"{last['commercial_stock']:.2f}",
                    f"{last['risk_premium']:.2f}",
                ]
            )
        )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", type=Path, default=Path("附件1.布伦特原油期货主力合约价格数据.csv"))
    parser.add_argument("--outdir", type=Path, default=Path("results"))
    args = parser.parse_args()

    latest_close = load_latest_close(resolve_csv_path(args.csv))
    base = replace(ModelParams(), initial_price=latest_close)
    results = {name: simulate_path(params) for name, params in scenario_params(base).items()}

    for name, rows in results.items():
        write_rows(rows, args.outdir / f"problem2_{name}_path.csv")
    plot_path = plot_scenarios(results, args.outdir / "problem2_price_paths.png")
    summary = summarize(results)
    (args.outdir / "problem2_summary.csv").write_text(summary + "\n", encoding="utf-8")
    print(summary)
    print(f"plot,{plot_path}")


if __name__ == "__main__":
    main()
