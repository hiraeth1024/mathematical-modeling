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


def simulate(
    beta: float,
    tau_r: int,
    r_max: float,
    c_max: float,
    k_c: float,
    f0: float,
    k_f: float,
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
        rt = 0.0 if t < tau_r else r_max
        ct = min(c_max * math.exp(-k_c * t), inventory)
        if t < tau_b:
            bt = 0.0
        else:
            bt = min(b_slope * (t - tau_b), b_max)
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
    mid_dates = [
        "2026-04-29",
        "2026-04-30",
        "2026-05-01",
        "2026-05-04",
        "2026-05-05",
    ]
    late_mean = mean_on_dates(sim_prices, late_dates)
    mid_mean = mean_on_dates(sim_prices, mid_dates)
    jump = early_jump(sim_prices)

    peak_err = (peak - 114.06) ** 2
    mid_err = (mid_mean - 111.384) ** 2
    late_err = (late_mean - 97.68) ** 2
    jump_err = (jump - 6.64) ** 2

    loss = base_sse + 4.0 * peak_err + 6.0 * mid_err + 10.0 * late_err + 2.0 * jump_err
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
        "beta": [0.065, 0.07, 0.075, 0.08],
        "tau_r": [7, 10],
        "r_max": [350.0, 450.0, 550.0],
        "c_max": [400.0, 450.0, 500.0],
        "k_c": [0.003, 0.005, 0.007],
        "f0": [0.14, 0.15, 0.16],
        "k_f": [0.18, 0.20, 0.22, 0.25],
        "l_early": [1600.0],
        "l_late": [1300.0, 1350.0, 1400.0],
        "t_late": [25, 30],
        "tau_b": [12, 15],
        "b_slope": [25.0, 30.0, 35.0],
        "b_max": [300.0, 350.0],
    }

    results = []
    combos = itertools.product(
        grid["beta"],
        grid["tau_r"],
        grid["r_max"],
        grid["c_max"],
        grid["k_c"],
        grid["f0"],
        grid["k_f"],
        grid["l_early"],
        grid["l_late"],
        grid["t_late"],
        grid["tau_b"],
        grid["b_slope"],
        grid["b_max"],
    )

    for vals in combos:
        (
            beta,
            tau_r,
            r_max,
            c_max,
            k_c,
            f0,
            k_f,
            l_early,
            l_late,
            t_late,
            tau_b,
            b_slope,
            b_max,
        ) = vals
        if l_late > l_early:
            continue
        sim_prices = simulate(
            beta,
            tau_r,
            r_max,
            c_max,
            k_c,
            f0,
            k_f,
            l_early,
            l_late,
            t_late,
            tau_b,
            b_slope,
            b_max,
        )
        metrics = build_loss(sim_prices, actual)[1]
        results.append(
            {
                "beta": beta,
                "tau_r": tau_r,
                "r_max": r_max,
                "c_max": c_max,
                "k_c": k_c,
                "f0": f0,
                "k_f": k_f,
                "l_early": l_early,
                "l_late": l_late,
                "t_late": t_late,
                "tau_b": tau_b,
                "b_slope": b_slope,
                "b_max": b_max,
                **metrics,
            }
        )

    results.sort(key=lambda x: x["loss"])

    with Path("joint_refined_calibration_results.csv").open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "beta",
                "tau_r",
                "r_max",
                "c_max",
                "k_c",
                "f0",
                "k_f",
                "l_early",
                "l_late",
                "t_late",
                "tau_b",
                "b_slope",
                "b_max",
                "sse",
                "peak",
                "mid_mean",
                "late_mean",
                "jump_pct",
                "loss",
            ],
        )
        writer.writeheader()
        writer.writerows(results)

    best = results[0]
    best_prices = simulate(
        best["beta"],
        best["tau_r"],
        best["r_max"],
        best["c_max"],
        best["k_c"],
        best["f0"],
        best["k_f"],
        best["l_early"],
        best["l_late"],
        best["t_late"],
        best["tau_b"],
        best["b_slope"],
        best["b_max"],
    )

    with Path("joint_refined_best_summary.txt").open("w", encoding="utf-8") as f:
        f.write("best_params\n")
        for key in [
            "beta",
            "tau_r",
            "r_max",
            "c_max",
            "k_c",
            "f0",
            "k_f",
            "l_early",
            "l_late",
            "t_late",
            "tau_b",
            "b_slope",
            "b_max",
            "sse",
            "peak",
            "mid_mean",
            "late_mean",
            "jump_pct",
            "loss",
        ]:
            f.write(f"{key}={best[key]}\n")

    with Path("joint_refined_best_simulation.csv").open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["date", "sim_price", "actual_close"])
        writer.writerow(["2026-02-27", f"{P0:.4f}", f"{P0:.2f}"])
        for d in sorted(best_prices):
            writer.writerow([d, f"{best_prices[d]:.4f}", actual.get(d, "")])

    print(f"tested={len(results)}")
    print(
        "best="
        f"beta={best['beta']},tau_r={best['tau_r']},r_max={best['r_max']},"
        f"c_max={best['c_max']},k_c={best['k_c']},f0={best['f0']},k_f={best['k_f']},"
        f"l_late={best['l_late']},t_late={best['t_late']},tau_b={best['tau_b']},"
        f"b_slope={best['b_slope']},b_max={best['b_max']}"
    )
    print(f"sse={best['sse']:.4f}")
    print(f"peak={best['peak']:.4f}")
    print(f"mid_mean={best['mid_mean']:.4f}")
    print(f"late_mean={best['late_mean']:.4f}")
    print(f"jump_pct={best['jump_pct']:.4f}")
    print(f"loss={best['loss']:.4f}")


if __name__ == "__main__":
    main()
