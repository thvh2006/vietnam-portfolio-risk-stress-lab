"""Fail-fast reproducibility and accounting checks for published risk results."""

import csv
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"


def close(left: float, right: float, tolerance: float = 1e-9) -> None:
    assert math.isclose(left, right, rel_tol=tolerance, abs_tol=tolerance), (left, right)


result = json.loads((REPORTS / "risk_summary.json").read_text(encoding="utf-8"))
close(result["case"]["analytical_weight_total"], 1.0)
close(sum(result["concentration"]["sector_weights"].values()), 1.0)
close(sum(row["share_of_total_volatility"] for row in result["component_risk"]), 1.0, 1e-7)
close(sum(row["component_parametric_var_99"] for row in result["component_risk"]), result["risk"]["primary_500d"]["parametric_var_99"], 1e-7)
close(sum(row["share_of_total_volatility"] for row in result["sector_risk"]), 1.0, 1e-7)
assert result["risk"]["primary_500d"]["observations"] == 500
assert result["risk"]["recent_250d"]["observations"] == 250
assert result["backtest"]["evaluation_observations"] == 250
assert result["backtest"]["zone"] in {"green", "amber", "red"}
assert result["hedge"]["rounded_short_contracts"] >= 0
close(result["hedge"]["comparison"]["hedged_beta"], result["hedge"]["residual_beta"], 1e-7)
assert result["hedge"]["comparison"]["hedged_annualised_volatility"] < result["hedge"]["comparison"]["unhedged_annualised_volatility"]
assert result["hedge"]["comparison"]["hedged_tracking_error"] > result["hedge"]["comparison"]["unhedged_tracking_error"]
assert 0 <= result["backtest"]["kupiec_pof"]["p_value"] <= 1
assert all(row["last_date"] == "2026-09-30" for row in result["coverage_audit"])
assert {row["ticker"] for row in result["coverage_audit"]} == {
    row["ticker"] for row in csv.DictReader((ROOT / "data/sample/holdings_2026-09-30.csv").open()) if row["ticker"] != "CASH"
}
assert result["model_methods"]["primary_500d"]["TCX"].startswith("sector_proxy")
assert result["model_methods"]["primary_500d"]["VPL"].startswith("sector_proxy")
assert result["model_methods"]["recent_250d"]["TCX"].startswith("sector_proxy")
assert result["model_methods"]["recent_250d"]["VPL"] == "own"
print("All reproducibility, coverage and risk-allocation checks passed.")
