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
BETA = 0.09

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


def commercial_release(t: int, inventory: float) -> float:
    target = 350.0 * math.exp(-0.02 * t)
    return min(target, inventory)


def bypass_recovery(t: int) -> float:
    if t < 15:
        return 0.0
    return min(25.0 * (t - 15), 300.0)


def panic_factor(t: int) -> float:
    if t < 10:
        return 0.15
    return 0.15 * math.exp(-0.10 * (t - 10))


def load_actual_prices(path: Path) -> dict[str, float]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    return {row["date"]: float(row["close"]) for row in rows}


def simulate() -> list[dict[str, float | int | str | None]]:
    rows: list[dict[str, float | int | str | None]] = []
    price = P0
    inventory = I0

    for t in range(NUM_DAYS + 1):
        current_date = START_DATE + timedelta(days=t)
        lt = supply_disruption(t)
        rt = reserve_release(t)
        ct = commercial_release(t, inventory)
        bt = bypass_recovery(t)
        ft = panic_factor(t)

        supply = S0 - lt + rt + ct + bt
        demand = D0 * (1.0 + ft) * ((price / P0) ** EPSILON)
        gap = (demand - supply) / S0

        rows.append(
            {
                "t": t,
                "date": current_date.isoformat(),
                "price": round(price, 4),
                "inventory": round(inventory, 4),
                "L_t": round(lt, 4),
                "R_t": round(rt, 4),
                "C_t": round(ct, 4),
                "B_t": round(bt, 4),
                "F_t": round(ft, 6),
                "S_t": round(supply, 4),
                "D_t": round(demand, 4),
                "g_t": round(gap, 6),
            }
        )

        next_price = price * (1.0 + BETA * gap)
        next_inventory = max(inventory - ct, 0.0)
        price = next_price
        inventory = next_inventory

    return rows


def write_output(
    rows: list[dict[str, float | int | str | None]],
    actual_prices: dict[str, float],
    path: Path,
) -> None:
    fieldnames = [
        "t",
        "date",
        "price",
        "actual_close",
        "inventory",
        "L_t",
        "R_t",
        "C_t",
        "B_t",
        "F_t",
        "S_t",
        "D_t",
        "g_t",
    ]
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            out = dict(row)
            out["actual_close"] = actual_prices.get(str(row["date"]))
            writer.writerow(out)


def main() -> None:
    actual_path = Path("brent_event_window.csv")
    output_path = Path("baseline_simulation.csv")
    actual_prices = load_actual_prices(actual_path)
    rows = simulate()

    base_row = {
        "t": -1,
        "date": "2026-02-27",
        "price": round(P0, 4),
        "inventory": round(I0, 4),
        "L_t": "",
        "R_t": "",
        "C_t": "",
        "B_t": "",
        "F_t": "",
        "S_t": "",
        "D_t": "",
        "g_t": "",
    }
    write_output([base_row, *rows], actual_prices | {"2026-02-27": P0}, output_path)


if __name__ == "__main__":
    main()
