"""Build the browser snapshot from reviewed model outputs and policy limits."""

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUMMARY_PATH = ROOT / "reports" / "risk_summary.json"
CONFIG_PATH = ROOT / "configs" / "project.yaml"
OUTPUT_PATH = ROOT / "dashboard" / "snapshot.js"


def yaml_section_numbers(path: Path, section: str) -> dict[str, float]:
    values: dict[str, float] = {}
    active = False
    for line in path.read_text(encoding="utf-8").splitlines():
        if re.fullmatch(rf"{re.escape(section)}:", line):
            active = True
            continue
        if active and line and not line.startswith(" "):
            break
        if not active:
            continue
        match = re.fullmatch(r"  ([a-z0-9_]+):\s*([0-9.]+)", line)
        if match:
            values[match.group(1)] = float(match.group(2))
    return values


def build_snapshot() -> dict:
    result = json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))
    limits = yaml_section_numbers(CONFIG_PATH, "limits")
    risk = result["risk"]
    concentration = result["concentration"]
    backtest = result["backtest"]
    hedge = result["hedge"]
    liquidity = result["liquidity_stress"]

    limit_rows = [
        {"key": "single_name", "label": "Single-name weight", "actual": concentration["largest_name_weight"], "limit": limits["single_name_weight"], "format": "percent"},
        {"key": "sector", "label": "Sector weight", "actual": concentration["largest_sector_weight"], "limit": limits["sector_weight"], "format": "percent"},
        {"key": "top_five", "label": "Top-five weight", "actual": concentration["top_five_weight"], "limit": limits["top_five_weight"], "format": "percent"},
        {"key": "one_day_var_99", "label": "1-day VaR 99%", "actual": risk["primary_500d"]["historical_var_99"], "limit": limits["one_day_var_99_nav"], "format": "percent"},
        {"key": "ten_day_es_975", "label": "Direct 10-day ES 97.5%", "actual": risk["ten_day_es_975_direct"], "limit": limits["ten_day_es_975_nav"], "format": "percent"},
        {"key": "liquidity_days_to_exit", "label": "Liquidity exit time", "actual": liquidity["maximum_base_days_to_exit"], "limit": limits["maximum_days_to_exit"], "format": "days"},
        {"key": "backtest_green_zone", "label": "Backtest exceptions", "actual": backtest["exceptions"], "limit": limits["maximum_var_exceptions_250d_green"], "format": "count"},
    ]
    for row in limit_rows:
        row["status"] = "PASS" if row["actual"] <= row["limit"] else "BREACH"

    return {
        "version": "v1.1.1",
        "asOf": result["case"]["as_of"],
        "shadowNavVnd": result["case"]["shadow_nav_vnd"],
        "risk": {
            "historicalVar99": risk["primary_500d"]["historical_var_99"],
            "directTenDayEs975": risk["ten_day_es_975_direct"],
            "sqrtTimeTenDayEs975": risk["ten_day_es_975_sqrt_time"],
            "annualisedVolatility": risk["primary_500d"]["annualised_volatility"],
            "beta": risk["beta_to_vn30"],
            "benchmarkVolatility": risk["benchmark_annualised_volatility"],
            "portfolioBenchmarkCovariance": risk["portfolio_benchmark_annualised_covariance"],
            "worstTwentyDay": abs(result["stress"]["worst_20d"]["return"]),
        },
        "backtest": {
            "exceptions": backtest["exceptions"],
            "observations": backtest["evaluation_observations"],
            "zone": backtest["zone"],
            "kupiecPValue": backtest["kupiec_pof"]["p_value"],
            "independencePValue": backtest["christoffersen"]["independence_p_value"],
            "conditionalCoveragePValue": backtest["christoffersen"]["conditional_coverage_p_value"],
            "covariancePsd": risk["covariance_validation"]["is_positive_semidefinite"],
        },
        "hedge": {
            "indexLevel": hedge["index_level_proxy"],
            "contractMultiplier": hedge["contract_multiplier"],
            "targetBeta": hedge["target_beta"],
            "contracts": hedge["rounded_short_contracts"],
            "residualBeta": hedge["residual_beta"],
            "initialMarginRate": hedge["initial_margin_rate"],
            "stressMarginMultiplier": hedge["stress_margin_multiplier"],
            "initialMarginVnd": hedge["initial_margin_vnd"],
            "stressedMarginVnd": hedge["stressed_margin_vnd"],
            "hedgedHistoricalVar99": hedge["comparison"]["hedged_var_99"],
            "hedgedTrackingError": hedge["comparison"]["hedged_tracking_error"],
        },
        "liquidity": {
            "baseParticipation": 0.20,
            "maximumBaseDaysToExit": liquidity["maximum_base_days_to_exit"],
        },
        "limits": limit_rows,
        "drivers": [
            {"ticker": row["ticker"], "share": row["share_of_total_volatility"]}
            for row in result["component_risk"][:8]
        ],
    }


def render(snapshot: dict) -> str:
    payload = json.dumps(snapshot, indent=2, sort_keys=True)
    return f"window.RISK_SNAPSHOT = {payload};\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="fail when the committed snapshot is stale")
    args = parser.parse_args()
    expected = render(build_snapshot())
    if args.check:
        assert OUTPUT_PATH.exists(), f"missing generated snapshot: {OUTPUT_PATH}"
        assert OUTPUT_PATH.read_text(encoding="utf-8") == expected, "dashboard/snapshot.js is stale; rebuild it"
        print("Dashboard snapshot matches reviewed model outputs and policy limits.")
        return
    OUTPUT_PATH.write_text(expected, encoding="utf-8")
    print(f"Wrote {OUTPUT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
