import math
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from portfolio_risk.engine import (
    christoffersen_test,
    compound,
    covariance,
    historical_expected_shortfall,
    kupiec_test,
    overlapping_returns,
    quantile,
    run_analysis,
    symmetric_eigenvalues,
)


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

    def test_direct_ten_day_returns(self):
        daily = [math.log(1.01)] * 12
        ten_day = overlapping_returns(daily, 10)
        self.assertEqual(len(ten_day), 3)
        self.assertAlmostEqual(ten_day[0], 1.01 ** 10 - 1.0)
        self.assertAlmostEqual(historical_expected_shortfall([-0.1, -0.02, 0.01], 0.975), 0.1)

    def test_symmetric_eigenvalue_check(self):
        self.assertGreaterEqual(min(symmetric_eigenvalues([[2.0, 1.0], [1.0, 2.0]])), 0.0)
        self.assertLess(min(symmetric_eigenvalues([[1.0, 2.0], [2.0, 1.0]])), 0.0)

    def test_christoffersen_probability_bounds(self):
        result = christoffersen_test([0, 0, 1, 0, 0, 1, 0], 0.2)
        self.assertGreaterEqual(result["independence_p_value"], 0)
        self.assertLessEqual(result["conditional_coverage_p_value"], 1)


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

    def test_rolling_diagnostic_window_and_scope(self):
        self.assertEqual(self.result["backtest"]["lookback"], 250)
        self.assertEqual(self.result["backtest"]["evaluation_observations"], 250)
        self.assertIn("current-weight", self.result["backtest"]["scope"])

    def test_direct_ten_day_es_and_covariance_validation(self):
        self.assertEqual(self.result["risk"]["ten_day_es_975_direct_observations"], 241)
        self.assertTrue(self.result["risk"]["covariance_validation"]["is_positive_semidefinite"])
        self.assertGreater(self.result["risk"]["ten_day_es_975_sqrt_time"], self.result["risk"]["ten_day_es_975_direct"])

    def test_proxy_floor_and_liquidity_stress(self):
        controls = self.result["model_methods"]["proxy_controls_primary_500d"]
        self.assertGreaterEqual(controls["TCX"]["applied_scale"], 1.0)
        self.assertGreaterEqual(controls["VPL"]["applied_scale"], 1.0)
        self.assertGreater(
            self.result["liquidity_stress"]["maximum_stressed_days_to_exit"],
            self.result["liquidity_stress"]["maximum_base_days_to_exit"],
        )


if __name__ == "__main__":
    unittest.main()
