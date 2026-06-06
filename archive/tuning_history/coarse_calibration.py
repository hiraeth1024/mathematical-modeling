from __future__ import annotations

import csv
import itertools
import math
from datetime import date, timedelta
from pathlib import Path


S0 = 10000.0
D0 = 10000.0
P0 = 73.21
I0 = 58000.0
EPSILON = -0.05
START_DATE = date(2026, 2, 28)
NUM_DAYS = 90


def supply_disruption(t: int) -> float:
    if t < 30:
        return 1600.0
    return 1450.0


def reserve_release(t: int) -> float:
    if t < 7:
        return 0.0
    return 450.0


def bypass_recovery(t: int) -> float:
    if t < 15:
        return 0.0
    return min(25.0 * (t - 15), 300.0)


def simulate(beta: float, c_max: float, k_c: float, f0: float, k_f: float) -> dict[str, float]:
    inventory = I0
    price = P0
    prices: dict[str, float] = {}

    for t in range(NUM_DAYS + 1):
        current_date = (START_DATE + timedelta(days=t)).isoformat()
        lt = supply_disruption(t)
        rt = reserve_release(t)
        ct = min(c_max * math.exp(-k_c * t), inventory)
        bt = bypass_recovery(t)
        ft = f0 if t < 10 else f0 * math.exp(-k_f * (t - 10))

        supply = S0 - lt + rt + ct + bt
        demand = D0 * (1.0 + ft) * ((price / P0) ** EPSILON)
        gap = (demand - supply) / S0
        prices[current_date] = price

        price = price * (1.0 + beta * gap)
        inventory = max(inventory - ct, 0.0)

    return prices


def load_actual(path: Path) -> dict[str, float]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return {row["date"]: float(row["close"]) for row in csv.DictReader(f)}


def sse(sim_prices: dict[str, float], obs_prices: dict[str, float]) -> float:
    total = 0.0
    for d, obs in obs_prices.items():
        if d in sim_prices:
            total += (sim_prices[d] - obs) ** 2
    return total


def late_mean(sim_prices: dict[str, float]) -> float:
    late_dates = [
        "2026-05-20",
        "2026-05-21",
        "2026-05-22",
        "2026-05-25",
        "2026-05-26",
        "2026-05-27",
        "2026-05-28",
        "2026-05-29",
    ]
    vals = [sim_prices[d] for d in late_dates if d in sim_prices]
    return sum(vals) / len(vals)


def peak_price(sim_prices: dict[str, float]) -> float:
    return max(sim_prices.values())


def main() -> None:
    actual = load_actual(Path("brent_event_window.csv"))
    grid = {
        "beta": [0.03, 0.04, 0.05, 0.06, 0.07],
        "c_max": [300.0, 350.0, 400.0, 450.0],
        "k_c": [0.005, 0.01, 0.015, 0.02],
        "f0": [0.10, 0.12, 0.15],
        "k_f": [0.10, 0.15, 0.20, 0.25],
    }

    results = []
    for beta, c_max, k_c, f0, k_f in itertools.product(
        grid["beta"], grid["c_max"], grid["k_c"], grid["f0"], grid["k_f"]
    ):
        sim_prices = simulate(beta, c_max, k_c, f0, k_f)
        results.append(
            {
                "beta": beta,
                "c_max": c_max,
                "k_c": k_c,
                "f0": f0,
                "k_f": k_f,
                "sse": sse(sim_prices, actual),
                "peak": peak_price(sim_prices),
                "late_mean": late_mean(sim_prices),
            }
        )

    results.sort(key=lambda x: x["sse"])

    with Path("coarse_calibration_results.csv").open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["beta", "c_max", "k_c", "f0", "k_f", "sse", "peak", "late_mean"],
        )
        writer.writeheader()
        writer.writerows(results)

    best = results[0]
    best_prices = simulate(
        best["beta"], best["c_max"], best["k_c"], best["f0"], best["k_f"]
    )
    with Path("coarse_best_summary.txt").open("w", encoding="utf-8") as f:
        f.write("best_params\n")
        for key in ["beta", "c_max", "k_c", "f0", "k_f", "sse", "peak", "late_mean"]:
            f.write(f"{key}={best[key]}\n")

    with Path("coarse_best_simulation.csv").open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["date", "sim_price", "actual_close"])
        writer.writerow(["2026-02-27", f"{P0:.4f}", f"{P0:.2f}"])
        for d in sorted(best_prices):
            writer.writerow([d, f"{best_prices[d]:.4f}", actual.get(d, "")])

    print(f"tested={len(results)}")
    print(
        "best="
        f"beta={best['beta']},c_max={best['c_max']},k_c={best['k_c']},"
        f"f0={best['f0']},k_f={best['k_f']}"
    )
    print(f"sse={best['sse']:.4f}")
    print(f"peak={best['peak']:.4f}")
    print(f"late_mean={best['late_mean']:.4f}")


if __name__ == "__main__":
    main()
