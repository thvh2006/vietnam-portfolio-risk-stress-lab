"""Run the independent risk engine and publish auditable result tables."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from portfolio_risk.engine import run_analysis, write_outputs  # noqa: E402


if __name__ == "__main__":
    result = run_analysis(ROOT)
    write_outputs(ROOT, result)
    risk = result["risk"]
    print(f"500d 99% historical VaR: {risk['primary_500d']['historical_var_99']:.2%}")
    print(f"500d annualised volatility: {risk['primary_500d']['annualised_volatility']:.2%}")
    print(f"Backtest: {result['backtest']['exceptions']} exceptions ({result['backtest']['zone']})")
    print(f"Limit breaches: {result['limits']['breach_count']}")

