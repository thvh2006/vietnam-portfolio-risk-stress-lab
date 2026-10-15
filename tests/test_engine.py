import math
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from portfolio_risk.engine import compound, covariance, kupiec_test, quantile, run_analysis


class TestRiskMath(unittest.TestCase):
    def test_quantile_interpolates(self):
        self.assertAlmostEqual(quantile([0, 1, 2, 3, 4], 0.25), 1.0)

    def test_log_return_compounding(self):
        self.assertAlmostEqual(compound([math.log(1.1), math.log(0.9)]), -0.01)

    def test_covariance_symmetry(self):
        x = [0.01, -0.02, 0.03, 0.00]
        y = [-0.01, 0.04, 0.02, -0.01]
        self.assertAlmostEqual(covariance(x, y), covariance(y, x))

    def test_kupiec_probability_bounds(self):
        result = kupiec_test(2, 250)
        self.assertGreaterEqual(result["p_value"], 0)
        self.assertLessEqual(result["p_value"], 1)


class TestPublishedCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = run_analysis(ROOT)

    def test_accounting_reconciliations(self):
        self.assertAlmostEqual(self.result["case"]["analytical_weight_total"], 1.0)
        self.assertAlmostEqual(sum(x["share_of_total_volatility"] for x in self.result["component_risk"]), 1.0)
        self.assertAlmostEqual(sum(x["share_of_total_volatility"] for x in self.result["sector_risk"]), 1.0)

    def test_hedge_tradeoff_is_explicit(self):
        comparison = self.result["hedge"]["comparison"]
        self.assertLess(comparison["hedged_annualised_volatility"], comparison["unhedged_annualised_volatility"])
        self.assertGreater(comparison["hedged_tracking_error"], comparison["unhedged_tracking_error"])

    def test_no_lookahead_backtest_window(self):
        self.assertEqual(self.result["backtest"]["lookback"], 250)
        self.assertEqual(self.result["backtest"]["evaluation_observations"], 250)


if __name__ == "__main__":
    unittest.main()

