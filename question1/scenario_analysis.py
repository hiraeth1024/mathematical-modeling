from __future__ import annotations

import csv
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


# Final retained structure and parameters
BETA = 0.079
TAU_R = 10
R_MAX = 525.0
C_MAX = 400.0
K_C = 0.003
TAU_Q = 62
Q_MAX = 0.08
K_Q = 0.08

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

MID_DATES = ["2026-04-29", "2026-04-30", "2026-05-01", "2026-05-04", "2026-05-05"]
LATE_DATES = ["2026-05-20", "2026-05-21", "2026-05-22", "2026-05-25", "2026-05-26", "2026-05-27", "2026-05-28", "2026-05-29"]
END_DATE = "2026-05-29"


def load_actual(path: Path) -> dict[str, float]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return {row["date"]: float(row["close"]) for row in csv.DictReader(f)}


def lt_value(t: int) -> float:
    if t < T1:
        return L1
    if t < T2:
        return L2
    return L3


def ft_value(t: int) -> float:
    if t < 10:
        return F0
    return F0 * math.exp(-K_F * (t - 10))


def qt_value(t: int) -> float:
    if t < TAU_Q:
        return 0.0
    return Q_MAX * (1.0 - math.exp(-K_Q * (t - TAU_Q)))


def mean_on_dates(rows: list[dict[str, float | str]], dates: list[str], field: str) -> float:
    vals = [float(row[field]) for row in rows if row["date"] in dates]
    return sum(vals) / len(vals)


def simulate_scenario(name: str, actual: dict[str, float]) -> list[dict[str, float | str]]:
    rows: list[dict[str, float | str]] = []
    inventory = I0
    price = P0

    for t in range(NUM_DAYS + 1):
        current_date = (START_DATE + timedelta(days=t)).isoformat()

        lt = lt_value(t)
        rt = 0.0 if t < TAU_R else R_MAX
        ct = min(C_MAX * math.exp(-K_C * t), inventory)
        bt = 0.0 if t < TAU_B else min(B_SLOPE * (t - TAU_B), B_MAX)
        ft = ft_value(t)
        qt = qt_value(t)

        if name == "baseline":
            pass
        elif name == "no_buffer":
            rt = 0.0
            ct = 0.0
            bt = 0.0
            qt = 0.0
        elif name == "supply_buffer_only":
            qt = 0.0
        elif name == "no_inventory_buffer":
            ct = 0.0
        elif name == "no_late_demand_cut":
            qt = 0.0
        else:
            raise ValueError(f"Unknown scenario: {name}")

        supply = S0 - lt + rt + ct + bt
        demand = D0 * (1.0 + ft) * ((price / P0) ** EPSILON) * (1.0 - qt)
        gap = (demand - supply) / S0

        rows.append(
            {
                "scenario": name,
                "t": t,
                "date": current_date,
                "price": round(price, 4),
                "actual_close": actual.get(current_date, ""),
                "inventory": round(inventory, 4),
                "L_t": round(lt, 4),
                "R_t": round(rt, 4),
                "C_t": round(ct, 4),
                "B_t": round(bt, 4),
                "F_t": round(ft, 6),
                "Q_t": round(qt, 6),
                "S_t": round(supply, 4),
                "D_t": round(demand, 4),
                "g_t": round(gap, 6),
            }
        )

        price = price * (1.0 + BETA * gap)
        inventory = max(inventory - ct, 0.0)

    return rows


def scenario_summary(rows: list[dict[str, float | str]]) -> dict[str, float | str]:
    peak_row = max(rows, key=lambda r: float(r["price"]))
    return {
        "scenario": rows[0]["scenario"],
        "peak_price": round(float(peak_row["price"]), 4),
        "peak_date": peak_row["date"],
        "mid_mean": round(mean_on_dates(rows, MID_DATES, "price"), 4),
        "late_mean": round(mean_on_dates(rows, LATE_DATES, "price"), 4),
        "end_price": round(float(next(r["price"] for r in rows if r["date"] == END_DATE)), 4),
    }


def main() -> None:
    actual = load_actual(Path("brent_event_window.csv"))
    scenario_names = [
        "baseline",
        "no_buffer",
        "supply_buffer_only",
        "no_inventory_buffer",
        "no_late_demand_cut",
    ]

    all_rows: list[dict[str, float | str]] = []
    summaries: list[dict[str, float | str]] = []

    for name in scenario_names:
        rows = simulate_scenario(name, actual)
        all_rows.extend(rows)
        summaries.append(scenario_summary(rows))

    with Path("scenario_paths.csv").open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "scenario", "t", "date", "price", "actual_close", "inventory",
                "L_t", "R_t", "C_t", "B_t", "F_t", "Q_t", "S_t", "D_t", "g_t",
            ],
        )
        writer.writeheader()
        writer.writerows(all_rows)

    with Path("scenario_summary.csv").open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["scenario", "peak_price", "peak_date", "mid_mean", "late_mean", "end_price"],
        )
        writer.writeheader()
        writer.writerows(summaries)

    print("scenarios_generated=5")
    for item in summaries:
        print(
            f"{item['scenario']}: peak={item['peak_price']}, peak_date={item['peak_date']}, "
            f"mid_mean={item['mid_mean']}, late_mean={item['late_mean']}, end_price={item['end_price']}"
        )


if __name__ == "__main__":
    main()
