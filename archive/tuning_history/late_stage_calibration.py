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


# Fixed from coarse calibration
BETA = 0.07
C_MAX = 450.0
K_C = 0.005
F0 = 0.15
K_F = 0.20


def reserve_release(t: int) -> float:
    if t < 7:
        return 0.0
    return 450.0


def simulate(
    l_early: float,
    l_late: float,
    t_late: int,
    tau_b: int,
    b_slope: float,
    b_max: float,
) -> dict[str, float]:
    inventory = I0
    price = P0
    prices: dict[str, float] = {}

    for t in range(NUM_DAYS + 1):
        current_date = (START_DATE + timedelta(days=t)).isoformat()

        lt = l_early if t < t_late else l_late
        rt = reserve_release(t)
        ct = min(C_MAX * math.exp(-K_C * t), inventory)
        if t < tau_b:
            bt = 0.0
        else:
            bt = min(b_slope * (t - tau_b), b_max)
        ft = F0 if t < 10 else F0 * math.exp(-K_F * (t - 10))

        supply = S0 - lt + rt + ct + bt
        demand = D0 * (1.0 + ft) * ((price / P0) ** EPSILON)
        gap = (demand - supply) / S0

        prices[current_date] = price
        price = price * (1.0 + BETA * gap)
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


def weighted_loss(sim_prices: dict[str, float], obs_prices: dict[str, float]) -> float:
    base_sse = sse(sim_prices, obs_prices)
    peak_err = (peak_price(sim_prices) - 114.06) ** 2
    late_err = (late_mean(sim_prices) - 97.68) ** 2
    return base_sse + 6.0 * late_err + 2.0 * peak_err


def main() -> None:
    actual = load_actual(Path("brent_event_window.csv"))
    grid = {
        "l_early": [1600.0, 1550.0],
        "l_late": [1450.0, 1400.0, 1350.0, 1300.0],
        "t_late": [20, 25, 30],
        "tau_b": [10, 12, 15],
        "b_slope": [25.0, 30.0, 35.0, 40.0],
        "b_max": [300.0, 350.0, 400.0],
    }

    results = []
    for values in itertools.product(
        grid["l_early"],
        grid["l_late"],
        grid["t_late"],
        grid["tau_b"],
        grid["b_slope"],
        grid["b_max"],
    ):
        l_early, l_late, t_late, tau_b, b_slope, b_max = values
        if l_late > l_early:
            continue
        sim_prices = simulate(l_early, l_late, t_late, tau_b, b_slope, b_max)
        rec = {
            "l_early": l_early,
            "l_late": l_late,
            "t_late": t_late,
            "tau_b": tau_b,
            "b_slope": b_slope,
            "b_max": b_max,
            "sse": sse(sim_prices, actual),
            "peak": peak_price(sim_prices),
            "late_mean": late_mean(sim_prices),
            "loss": weighted_loss(sim_prices, actual),
        }
        results.append(rec)

    results.sort(key=lambda x: x["loss"])

    with Path("late_stage_calibration_results.csv").open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "l_early",
                "l_late",
                "t_late",
                "tau_b",
                "b_slope",
                "b_max",
                "sse",
                "peak",
                "late_mean",
                "loss",
            ],
        )
        writer.writeheader()
        writer.writerows(results)

    best = results[0]
    best_prices = simulate(
        best["l_early"],
        best["l_late"],
        best["t_late"],
        best["tau_b"],
        best["b_slope"],
        best["b_max"],
    )

    with Path("late_stage_best_summary.txt").open("w", encoding="utf-8") as f:
        f.write("best_params\n")
        for key in [
            "l_early",
            "l_late",
            "t_late",
            "tau_b",
            "b_slope",
            "b_max",
            "sse",
            "peak",
            "late_mean",
            "loss",
        ]:
            f.write(f"{key}={best[key]}\n")

    with Path("late_stage_best_simulation.csv").open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["date", "sim_price", "actual_close"])
        writer.writerow(["2026-02-27", f"{P0:.4f}", f"{P0:.2f}"])
        for d in sorted(best_prices):
            writer.writerow([d, f"{best_prices[d]:.4f}", actual.get(d, "")])

    print(f"tested={len(results)}")
    print(
        "best="
        f"l_early={best['l_early']},l_late={best['l_late']},t_late={best['t_late']},"
        f"tau_b={best['tau_b']},b_slope={best['b_slope']},b_max={best['b_max']}"
    )
    print(f"sse={best['sse']:.4f}")
    print(f"peak={best['peak']:.4f}")
    print(f"late_mean={best['late_mean']:.4f}")
    print(f"loss={best['loss']:.4f}")


if __name__ == "__main__":
    main()
