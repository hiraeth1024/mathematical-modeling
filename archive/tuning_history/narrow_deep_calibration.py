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


# Fixed structure: two-stage L_t + single-stage F_t
L1 = 1600.0
L2 = 1500.0
L3 = 1150.0
T1 = 25
T2 = 60

F0 = 0.16
K_F = 0.18

TAU_B = 15
B_SLOPE = 25.0
B_MAX = 300.0


def load_actual(path: Path) -> dict[str, float]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return {row["date"]: float(row["close"]) for row in csv.DictReader(f)}


def simulate(
    beta: float,
    tau_r: int,
    r_max: float,
    c_max: float,
    k_c: float,
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

        rt = 0.0 if t < tau_r else r_max
        ct = min(c_max * math.exp(-k_c * t), inventory)
        bt = 0.0 if t < TAU_B else min(B_SLOPE * (t - TAU_B), B_MAX)
        ft = F0 if t < 10 else F0 * math.exp(-K_F * (t - 10))

        supply = S0 - lt + rt + ct + bt
        demand = D0 * (1.0 + ft) * ((price / P0) ** EPSILON)
        gap = (demand - supply) / S0

        prices[current_date] = price
        price = price * (1.0 + beta * gap)
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
    mid_dates = ["2026-04-29", "2026-04-30", "2026-05-01", "2026-05-04", "2026-05-05"]
    late_dates = ["2026-05-20", "2026-05-21", "2026-05-22", "2026-05-25", "2026-05-26", "2026-05-27", "2026-05-28", "2026-05-29"]
    tail_dates = ["2026-05-27", "2026-05-28", "2026-05-29"]

    peak = peak_price(sim_prices)
    mid_mean = mean_on_dates(sim_prices, mid_dates)
    late_mean = mean_on_dates(sim_prices, late_dates)
    jump = early_jump(sim_prices)
    tail_err = sum((sim_prices[d] - obs_prices[d]) ** 2 for d in tail_dates if d in sim_prices and d in obs_prices)

    peak_err = (peak - 114.06) ** 2
    mid_err = (mid_mean - 111.384) ** 2
    late_err = (late_mean - 97.68) ** 2
    jump_err = (jump - 6.64) ** 2

    loss = base_sse + 4.0 * peak_err + 6.0 * mid_err + 10.0 * late_err + 8.0 * tail_err + 2.0 * jump_err
    return loss, {
        "sse": base_sse,
        "peak": peak,
        "mid_mean": mid_mean,
        "late_mean": late_mean,
        "jump_pct": jump,
        "tail_err": tail_err,
        "loss": loss,
    }


def main() -> None:
    actual = load_actual(Path("brent_event_window.csv"))
    grid = {
        "beta": [0.078, 0.08, 0.082, 0.085],
        "tau_r": [8, 9, 10, 11],
        "r_max": [500.0, 550.0, 600.0, 650.0],
        "c_max": [350.0, 375.0, 400.0, 425.0],
        "k_c": [0.002, 0.0025, 0.003, 0.0035],
    }

    results = []
    for beta, tau_r, r_max, c_max, k_c in itertools.product(
        grid["beta"], grid["tau_r"], grid["r_max"], grid["c_max"], grid["k_c"]
    ):
        sim_prices = simulate(beta, tau_r, r_max, c_max, k_c)
        metrics = build_loss(sim_prices, actual)[1]
        results.append(
            {
                "beta": beta,
                "tau_r": tau_r,
                "r_max": r_max,
                "c_max": c_max,
                "k_c": k_c,
                **metrics,
            }
        )

    results.sort(key=lambda x: x["loss"])

    out_fields = ["beta", "tau_r", "r_max", "c_max", "k_c", "sse", "peak", "mid_mean", "late_mean", "jump_pct", "tail_err", "loss"]
    with Path("narrow_deep_calibration_results.csv").open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=out_fields)
        writer.writeheader()
        writer.writerows(results)

    best = results[0]
    best_prices = simulate(best["beta"], best["tau_r"], best["r_max"], best["c_max"], best["k_c"])

    with Path("narrow_deep_best_summary.txt").open("w", encoding="utf-8") as f:
        f.write("best_params\n")
        for key in out_fields:
            f.write(f"{key}={best[key]}\n")

    with Path("narrow_deep_best_simulation.csv").open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["date", "sim_price", "actual_close"])
        writer.writerow(["2026-02-27", f"{P0:.4f}", f"{P0:.2f}"])
        for d in sorted(best_prices):
            writer.writerow([d, f"{best_prices[d]:.4f}", actual.get(d, "")])

    print(f"tested={len(results)}")
    print(
        "best="
        f"beta={best['beta']},tau_r={best['tau_r']},r_max={best['r_max']},"
        f"c_max={best['c_max']},k_c={best['k_c']}"
    )
    print(f"sse={best['sse']:.4f}")
    print(f"peak={best['peak']:.4f}")
    print(f"mid_mean={best['mid_mean']:.4f}")
    print(f"late_mean={best['late_mean']:.4f}")
    print(f"jump_pct={best['jump_pct']:.4f}")
    print(f"tail_err={best['tail_err']:.4f}")
    print(f"loss={best['loss']:.4f}")


if __name__ == "__main__":
    main()
