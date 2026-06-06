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


# Fixed from previous best round, except L_t structure under test
BETA = 0.08
TAU_R = 10
R_MAX = 550.0
C_MAX = 400.0
K_C = 0.003
F0 = 0.16
K_F = 0.18
TAU_B = 15
B_SLOPE = 25.0
B_MAX = 300.0


def load_actual(path: Path) -> dict[str, float]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return {row["date"]: float(row["close"]) for row in csv.DictReader(f)}


def simulate(
    l1: float,
    l2: float,
    l3: float,
    t1: int,
    t2: int,
) -> dict[str, float]:
    inventory = I0
    price = P0
    prices: dict[str, float] = {}

    for t in range(NUM_DAYS + 1):
        current_date = (START_DATE + timedelta(days=t)).isoformat()

        if t < t1:
            lt = l1
        elif t < t2:
            lt = l2
        else:
            lt = l3

        rt = 0.0 if t < TAU_R else R_MAX
        ct = min(C_MAX * math.exp(-K_C * t), inventory)
        bt = 0.0 if t < TAU_B else min(B_SLOPE * (t - TAU_B), B_MAX)
        ft = F0 if t < 10 else F0 * math.exp(-K_F * (t - 10))

        supply = S0 - lt + rt + ct + bt
        demand = D0 * (1.0 + ft) * ((price / P0) ** EPSILON)
        gap = (demand - supply) / S0

        prices[current_date] = price
        price = price * (1.0 + BETA * gap)
        inventory = max(inventory - ct, 0.0)

    return prices


def sse(sim_prices: dict[str, float], obs_prices: dict[str, float]) -> float:
    total = 0.0
    for d, obs in obs_prices.items():
        if d in sim_prices:
            total += (sim_prices[d] - obs) ** 2
    return total


def mean_on_dates(sim_prices: dict[str, float], dates: list[str]) -> float:
    vals = [sim_prices[d] for d in dates if d in sim_prices]
    return sum(vals) / len(vals)


def peak_price(sim_prices: dict[str, float]) -> float:
    return max(sim_prices.values())


def early_jump(sim_prices: dict[str, float]) -> float:
    return (sim_prices["2026-03-02"] / P0 - 1.0) * 100.0


def build_loss(sim_prices: dict[str, float], obs_prices: dict[str, float]) -> tuple[float, dict[str, float]]:
    base_sse = sse(sim_prices, obs_prices)
    peak = peak_price(sim_prices)
    mid_dates = [
        "2026-04-29",
        "2026-04-30",
        "2026-05-01",
        "2026-05-04",
        "2026-05-05",
    ]
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
    mid_mean = mean_on_dates(sim_prices, mid_dates)
    late_mean = mean_on_dates(sim_prices, late_dates)
    jump = early_jump(sim_prices)

    peak_err = (peak - 114.06) ** 2
    mid_err = (mid_mean - 111.384) ** 2
    late_err = (late_mean - 97.68) ** 2
    jump_err = (jump - 6.64) ** 2

    loss = base_sse + 5.0 * peak_err + 8.0 * mid_err + 10.0 * late_err + 2.0 * jump_err
    return loss, {
        "sse": base_sse,
        "peak": peak,
        "mid_mean": mid_mean,
        "late_mean": late_mean,
        "jump_pct": jump,
        "loss": loss,
    }


def main() -> None:
    actual = load_actual(Path("brent_event_window.csv"))
    grid = {
        "l1": [1600.0, 1650.0, 1700.0],
        "l2": [1500.0, 1550.0, 1600.0],
        "l3": [1150.0, 1200.0, 1250.0, 1300.0],
        "t1": [25, 30, 35],
        "t2": [60, 65, 70, 75],
    }

    results = []
    for l1, l2, l3, t1, t2 in itertools.product(
        grid["l1"], grid["l2"], grid["l3"], grid["t1"], grid["t2"]
    ):
        if not (l1 >= l2 >= l3):
            continue
        if not (t1 < t2):
            continue
        sim_prices = simulate(l1, l2, l3, t1, t2)
        metrics = build_loss(sim_prices, actual)[1]
        results.append(
            {
                "l1": l1,
                "l2": l2,
                "l3": l3,
                "t1": t1,
                "t2": t2,
                **metrics,
            }
        )

    results.sort(key=lambda x: x["loss"])

    with Path("two_stage_L_calibration_results.csv").open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["l1", "l2", "l3", "t1", "t2", "sse", "peak", "mid_mean", "late_mean", "jump_pct", "loss"],
        )
        writer.writeheader()
        writer.writerows(results)

    best = results[0]
    best_prices = simulate(best["l1"], best["l2"], best["l3"], best["t1"], best["t2"])

    with Path("two_stage_L_best_summary.txt").open("w", encoding="utf-8") as f:
        f.write("best_params\n")
        for key in ["l1", "l2", "l3", "t1", "t2", "sse", "peak", "mid_mean", "late_mean", "jump_pct", "loss"]:
            f.write(f"{key}={best[key]}\n")

    with Path("two_stage_L_best_simulation.csv").open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["date", "sim_price", "actual_close"])
        writer.writerow(["2026-02-27", f"{P0:.4f}", f"{P0:.2f}"])
        for d in sorted(best_prices):
            writer.writerow([d, f"{best_prices[d]:.4f}", actual.get(d, "")])

    print(f"tested={len(results)}")
    print(f"best=l1={best['l1']},l2={best['l2']},l3={best['l3']},t1={best['t1']},t2={best['t2']}")
    print(f"sse={best['sse']:.4f}")
    print(f"peak={best['peak']:.4f}")
    print(f"mid_mean={best['mid_mean']:.4f}")
    print(f"late_mean={best['late_mean']:.4f}")
    print(f"jump_pct={best['jump_pct']:.4f}")
    print(f"loss={best['loss']:.4f}")


if __name__ == "__main__":
    main()
