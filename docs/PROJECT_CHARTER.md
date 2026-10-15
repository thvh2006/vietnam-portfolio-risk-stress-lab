# Project charter

## Objective

Build an auditable market-risk and stress-testing process around a real Vietnam equity portfolio. The portfolio is the SSIAM VN30 ETF composition reported at 30 September 2026, scaled to a VND100 billion shadow mandate.

## Decision owner

The primary user is a portfolio risk manager presenting to an investment committee. The project must end with a risk-limit and hedge decision, not a catalogue of statistics.

## Decision boundary

FUESSV30 is a passive fund whose stated objective is to replicate VN30 and which does not take defensive action in falling markets. The shadow mandate is separate from the fund. It uses the disclosed portfolio to demonstrate what a controlled hedge overlay would look like under a different risk mandate.

## Core decision

If the portfolio breaches the approved market-risk budget, determine the number of VN30 futures contracts required to bring beta-adjusted exposure back within limits while preserving the constituent portfolio.

## Analytical sequence

1. Freeze reported positions and reconcile weights.
2. Snapshot adjusted daily prices and audit coverage.
3. Calculate daily portfolio and benchmark returns without hindsight reweighting.
4. Measure volatility, beta, drawdown, VaR, Expected Shortfall and risk contribution.
5. Backtest one-day 99% VaR over the latest 250 observations.
6. Replay observed stress windows and apply hypothetical sector and liquidity shocks.
7. Find the minimum market shock or correlation regime that breaches the loss limit.
8. Compare no action, constituent rebalance and VN30 futures hedge after transaction and basis-risk assumptions.

## Senior-level controls

- Reported weights remain immutable; normalisation occurs only in the calculation layer.
- New listings and short histories are flagged. Any proxy is explicit and conservative.
- Historical replay is labelled as current-weight replay, not reconstructed fund performance.
- VaR never replaces Expected Shortfall, stress testing or concentration limits.
- Backtesting uses information available before each forecasted day.
- Hedge recommendations include contract rounding, residual beta, basis risk and margin liquidity.

## Deliverables

- Excel risk cockpit with transparent formulas and scenario controls.
- Python engine as an independent calculation path.
- Risk and stress report for the investment committee.
- Model card, source register, backtest log and data-quality report.
- GitHub repository with automated tests and a scheduled freshness monitor.
