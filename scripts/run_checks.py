"""Fail-fast reproducibility and accounting checks for published risk results."""

import csv
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
EXPECTED_HASHES = {
    "data/sample/holdings_2026-09-30.csv": "c979a8f346b892a9508ed6de85bec3164244b4ebf76fceb0d84f2353226f261c",
    "data/market/vn30_index.csv": "c79147093ceedd8f8e008346347e5dc3bbab782dfc362a6024188b7bfccb6da9",
    "data/market/constituent_prices.csv": "786f3e830fb3976b04392d41a4a0d157066460aa1a27e096271242ea9399bdef",
}


def close(left: float, right: float, tolerance: float = 1e-9) -> None:
    assert math.isclose(left, right, rel_tol=tolerance, abs_tol=tolerance), (left, right)


result = json.loads((REPORTS / "risk_summary.json").read_text(encoding="utf-8"))
for relative_path, expected_hash in EXPECTED_HASHES.items():
    assert hashlib.sha256((ROOT / relative_path).read_bytes()).hexdigest() == expected_hash
close(result["case"]["analytical_weight_total"], 1.0)
close(sum(result["concentration"]["sector_weights"].values()), 1.0)
close(sum(row["share_of_total_volatility"] for row in result["component_risk"]), 1.0, 1e-7)
close(sum(row["component_parametric_var_99"] for row in result["component_risk"]), result["risk"]["primary_500d"]["parametric_var_99"], 1e-7)
close(sum(row["share_of_total_volatility"] for row in result["sector_risk"]), 1.0, 1e-7)
assert result["risk"]["primary_500d"]["observations"] == 500
assert result["risk"]["recent_250d"]["observations"] == 250
assert result["risk"]["ten_day_es_975_direct_observations"] == 241
assert result["risk"]["covariance_validation"]["is_positive_semidefinite"]
assert result["risk"]["covariance_validation"]["minimum_eigenvalue"] >= -result["risk"]["covariance_validation"]["tolerance"]
assert result["backtest"]["evaluation_observations"] == 250
assert result["backtest"]["zone"] in {"green", "amber", "red"}
assert result["hedge"]["rounded_short_contracts"] >= 0
close(result["hedge"]["comparison"]["hedged_beta"], result["hedge"]["residual_beta"], 1e-7)
assert result["hedge"]["comparison"]["hedged_annualised_volatility"] < result["hedge"]["comparison"]["unhedged_annualised_volatility"]
assert result["hedge"]["comparison"]["hedged_tracking_error"] > result["hedge"]["comparison"]["unhedged_tracking_error"]
assert 0 <= result["backtest"]["kupiec_pof"]["p_value"] <= 1
assert 0 <= result["backtest"]["christoffersen"]["independence_p_value"] <= 1
assert 0 <= result["backtest"]["christoffersen"]["conditional_coverage_p_value"] <= 1
assert "current-weight" in result["backtest"]["scope"]
assert all(row["last_date"] == "2026-09-30" for row in result["coverage_audit"])
assert {row["ticker"] for row in result["coverage_audit"]} == {
    row["ticker"] for row in csv.DictReader((ROOT / "data/sample/holdings_2026-09-30.csv").open()) if row["ticker"] != "CASH"
}
assert result["model_methods"]["primary_500d"]["TCX"].startswith("sector_proxy")
assert result["model_methods"]["primary_500d"]["VPL"].startswith("sector_proxy")
assert result["model_methods"]["recent_250d"]["TCX"].startswith("sector_proxy")
assert result["model_methods"]["recent_250d"]["VPL"] == "own"
assert all(control["applied_scale"] >= 1.0 for control in result["model_methods"]["proxy_controls_primary_500d"].values())
assert result["liquidity_stress"]["maximum_stressed_days_to_exit"] >= result["liquidity_stress"]["maximum_base_days_to_exit"]
close(result["hedge"]["initial_margin_vnd"], result["hedge"]["rounded_short_contracts"] * result["hedge"]["contract_notional_vnd"] * result["hedge"]["initial_margin_rate"])

# Published-surface controls: prevent the dashboard and committee memo from
# drifting away from the reviewed engine output.
snapshot_source = (ROOT / "dashboard/snapshot.js").read_text(encoding="utf-8")
snapshot = json.loads(snapshot_source.removeprefix("window.RISK_SNAPSHOT = ").removesuffix(";\n"))
single_name_limit = next(row for row in snapshot["limits"] if row["key"] == "single_name")
close(single_name_limit["actual"], result["concentration"]["largest_name_weight"])
close(single_name_limit["limit"], 0.11)
assert snapshot["version"] == "v1.1.1"
assert snapshot["hedge"]["contracts"] == result["hedge"]["rounded_short_contracts"]
close(snapshot["risk"]["directTenDayEs975"], result["risk"]["ten_day_es_975_direct"])
assert all(row["status"] == "PASS" for row in snapshot["limits"])

memo = (ROOT / "docs/INVESTMENT_COMMITTEE_MEMO.md").read_text(encoding="utf-8")
assert "13.54% of total portfolio volatility" in memo
assert "21.85% of total volatility" in memo
assert "38.57% of volatility" in memo
assert "| Worst historical day | -7.24% | -VND7.24bn |" in memo
assert "| Worst historical 5-day window | -15.40% | -VND15.40bn |" in memo
assert "| 2022 deleveraging replay | -41.62% | -VND41.62bn |" in memo
assert "| Reverse stress: VN30 shock for 15% loss | -15.15% | threshold |" in memo
print("All reproducibility, coverage and risk-allocation checks passed.")
