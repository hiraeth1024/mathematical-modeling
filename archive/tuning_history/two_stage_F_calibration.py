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


# Fixed current best structure except F_t under test
BETA = 0.08
TAU_R = 10
R_MAX = 550.0
C_MAX = 400.0
K_C = 0.003
TAU_B = 15
B_SLOPE = 25.0
B_MAX = 300.0

# Two-stage L_t fixed from previous step
L1 = 1600.0
L2 = 1500.0
L3 = 1150.0
T1 = 25
T2 = 60


def load_actual(path: Path) -> dict[str, float]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return {row["date"]: float(row["close"]) for row in csv.DictReader(f)}


def panic_factor(t: int, f0: float, t_hold: int, t_switch: int, k1: float, k2: float) -> float:
    if t < t_hold:
        return f0
    if t < t_switch:
        return f0 * math.exp(-k1 * (t - t_hold))
    stage1_end = f0 * math.exp(-k1 * (t_switch - t_hold))
    return stage1_end * math.exp(-k2 * (t - t_switch))


def simulate(
    f0: float,
    t_hold: int,
    t_switch: int,
    k1: float,
    k2: float,
) -> dict[str, float]:
    inventory = I0
    price = P0
    prices: dict[str, float] = {}

    for t in range(NUM_DAYS + 1):
        current_date = (START_DATE + timedelta(days=t)).isoformat()

        if t < T1:
            lt = L1
        elif t < T2:
            lt = L2
        else:
            lt = L3

        rt = 0.0 if t < TAU_R else R_MAX
        ct = min(C_MAX * math.exp(-K_C * t), inventory)
        bt = 0.0 if t < TAU_B else min(B_SLOPE * (t - TAU_B), B_MAX)
        ft = panic_factor(t, f0, t_hold, t_switch, k1, k2)

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
        "f0": [0.16, 0.18, 0.20, 0.22],
        "t_hold": [8, 10, 12],
        "t_switch": [35, 40, 45, 50],
        "k1": [0.02, 0.03, 0.04, 0.05],
        "k2": [0.12, 0.16, 0.20, 0.24, 0.30],
    }

    results = []
    for f0, t_hold, t_switch, k1, k2 in itertools.product(
        grid["f0"], grid["t_hold"], grid["t_switch"], grid["k1"], grid["k2"]
    ):
        if t_switch <= t_hold:
            continue
        if k2 <= k1:
            continue
        sim_prices = simulate(f0, t_hold, t_switch, k1, k2)
        metrics = build_loss(sim_prices, actual)[1]
        results.append(
            {
                "f0": f0,
                "t_hold": t_hold,
                "t_switch": t_switch,
                "k1": k1,
                "k2": k2,
                **metrics,
            }
        )

    results.sort(key=lambda x: x["loss"])

    with Path("two_stage_F_calibration_results.csv").open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["f0", "t_hold", "t_switch", "k1", "k2", "sse", "peak", "mid_mean", "late_mean", "jump_pct", "loss"],
        )
        writer.writeheader()
        writer.writerows(results)

    best = results[0]
    best_prices = simulate(best["f0"], best["t_hold"], best["t_switch"], best["k1"], best["k2"])

    with Path("two_stage_F_best_summary.txt").open("w", encoding="utf-8") as f:
        f.write("best_params\n")
        for key in ["f0", "t_hold", "t_switch", "k1", "k2", "sse", "peak", "mid_mean", "late_mean", "jump_pct", "loss"]:
            f.write(f"{key}={best[key]}\n")

    with Path("two_stage_F_best_simulation.csv").open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["date", "sim_price", "actual_close"])
        writer.writerow(["2026-02-27", f"{P0:.4f}", f"{P0:.2f}"])
        for d in sorted(best_prices):
            writer.writerow([d, f"{best_prices[d]:.4f}", actual.get(d, "")])

    print(f"tested={len(results)}")
    print(
        "best="
        f"f0={best['f0']},t_hold={best['t_hold']},t_switch={best['t_switch']},"
        f"k1={best['k1']},k2={best['k2']}"
    )
    print(f"sse={best['sse']:.4f}")
    print(f"peak={best['peak']:.4f}")
    print(f"mid_mean={best['mid_mean']:.4f}")
    print(f"late_mean={best['late_mean']:.4f}")
    print(f"jump_pct={best['jump_pct']:.4f}")
    print(f"loss={best['loss']:.4f}")


if __name__ == "__main__":
    main()
