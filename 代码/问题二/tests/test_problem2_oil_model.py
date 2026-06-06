import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "code"))

from problem2_oil_model import ModelParams, equilibrium_price, resolve_csv_path, simulate_path


class Problem2OilModelTest(unittest.TestCase):
    def test_equilibrium_price_rises_with_larger_supply_gap(self):
        params = ModelParams()
        small_gap = equilibrium_price(params.baseline_price, params.baseline_demand, 94.0, params.long_run_elasticity)
        large_gap = equilibrium_price(params.baseline_price, params.baseline_demand, 88.0, params.long_run_elasticity)

        self.assertGreater(large_gap, small_gap)
        self.assertGreater(small_gap, params.baseline_price)

    def test_low_inventory_adds_risk_premium(self):
        params = ModelParams()
        high_inventory = params.risk_premium(300.0)
        low_inventory = params.risk_premium(40.0)

        self.assertGreater(low_inventory, high_inventory)
        self.assertEqual(high_inventory, 0.0)

    def test_simulation_covers_90_to_180_days(self):
        params = ModelParams()
        rows = simulate_path(params)

        self.assertEqual(len(rows), 91)
        self.assertEqual(rows[0]["day"], 90)
        self.assertEqual(rows[-1]["day"], 180)
        self.assertTrue(all(row["price"] > 0 for row in rows))

    def test_resolves_dataset_from_parent_directories(self):
        resolved = resolve_csv_path(Path("附件1.布伦特原油期货主力合约价格数据.csv"))

        self.assertTrue(resolved.exists())
        self.assertEqual(resolved.name, "附件1.布伦特原油期货主力合约价格数据.csv")


if __name__ == "__main__":
    unittest.main()
