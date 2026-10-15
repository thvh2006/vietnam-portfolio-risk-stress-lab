# Vietnam Portfolio Risk & Stress Lab

![Risk dashboard preview](assets/risk_dashboard_preview.png)

Point-in-time market-risk case built on the publicly disclosed SSIAM VN30 ETF portfolio. The project scales the 30-stock portfolio to a VND100 billion shadow mandate and asks whether its market, concentration and liquidity risks fit an explicit risk budget.

The case uses real holdings and market data. It is an independent portfolio demonstration, not an analysis performed for SSIAM and not a recommendation that the passive ETF should hedge.

## Decision question

At the 30 September 2026 information cutoff:

1. Where does the portfolio's risk come from by stock and sector?
2. How much can the mandate lose under ordinary and stressed conditions?
3. Does the risk model survive out-of-sample backtesting?
4. If a risk limit is breached, what VN30 futures overlay reduces risk with the least tracking disruption?

## Real case

- Reference portfolio: SSIAM VN30 ETF (`FUESSV30`).
- Benchmark: VN30 Index.
- Holdings date: 30 September 2026.
- Disclosure date: 7 October 2026.
- Reported holdings: 30 stocks plus cash.
- Shadow mandate NAV: VND100 billion.
- Hedge instrument: VN30 Index futures, contract multiplier VND100,000 per index point.

## Published outputs

- [`Vietnam_Portfolio_Risk_Stress_Lab.xlsx`](Vietnam_Portfolio_Risk_Stress_Lab.xlsx): formula-driven risk cockpit and hedge simulator.
- [`Vietnam_Portfolio_Risk_Stress_Report.pdf`](output/pdf/Vietnam_Portfolio_Risk_Stress_Report.pdf): eight-page risk committee report.
- `src/portfolio_risk/engine.py`: dependency-light independent Python risk engine.
- `reports/`: coverage, component-risk, liquidity, stress and VaR backtesting outputs.
- [`docs/INVESTMENT_COMMITTEE_MEMO.md`](docs/INVESTMENT_COMMITTEE_MEMO.md): decision memo.
- [`MODEL_CARD.md`](MODEL_CARD.md): intended use, validation, limitations and monitoring policy.

## Key result

The portfolio passes the 3.50% one-day 99% VaR limit at 3.39%, but its square-root-of-time 10-day 97.5% ES is 12.28% and marginally breaches the 12.00% limit. The rolling backtest has 2 exceptions in 250 observations (green zone). The workbook calculates an index-equivalent hedge of 151 short contracts to reduce beta from 0.99 to 0.70; this is a scenario, not an order.

The investment outcome is mandate-dependent:

- **Benchmark tracking:** retain the unhedged portfolio and approve a time-limited ES exception. Hedging would raise tracking error from 2.35% to 6.51%.
- **Absolute risk:** hedge toward beta 0.70 after execution controls. The replayed overlay reduces historical 99% VaR from 3.39% to 2.46%.

The model challenge is intentionally visible. Normal 99% VaR is 2.87%, historical VaR is 3.39% and Cornish-Fisher VaR is 4.16%. Negative skewness and excess kurtosis make a normal-only conclusion unreliable.

## Analytical depth

- 500-day and 250-day historical VaR/ES;
- EWMA volatility and rolling risk regimes;
- Cornish-Fisher non-normality challenge;
- Euler component volatility and component VaR;
- sector risk-to-weight decomposition;
- historical, hypothetical, correlation and reverse stress;
- rolling VaR traffic-light and Kupiec POF validation;
- target-beta sensitivity and before/after hedge economics;
- liquidity capacity and explicit short-history proxy audit.

## Reproduce

```bash
python3 scripts/run_risk.py
python3 scripts/run_checks.py
python3 -m unittest discover -s tests -v
```

The market snapshot is frozen under `data/market/`. Re-fetching changes the evidence set and should be treated as a new model run.
