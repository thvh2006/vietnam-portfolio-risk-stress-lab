# Model Card — Vietnam Portfolio Risk & Stress Lab

| Governance item | Status |
|---|---|
| Model version | v1.1.1 |
| Information cutoff | 30 September 2026 |
| Owner | Repository maintainer |
| Use status | Independent portfolio demonstration |
| Independent validation | Not performed; execution use is prohibited without independent validation |
| Published surfaces | Python outputs, Excel workbook, committee report and public dashboard |

## Intended use

Independent market-risk demonstration for a VND100 billion shadow mandate based on the publicly disclosed 30 September 2026 FUESSV30 portfolio. It supports risk-committee discussion of tail loss, concentration, liquidity and a VN30 futures overlay. It is not investment advice, a regulatory capital model or an executable hedge instruction.

## Model specification

| Item | Specification |
|---|---|
| Portfolio | Current reported FUESSV30 holdings, analytically normalised from 100.02% to 100.00% |
| Returns | Daily adjusted close log returns; benchmark-calendar carry-forward for missing quote days |
| Primary / recent windows | 500 / 250 trading days |
| Tail risk | Historical VaR 95%/99%, daily ES 97.5%/99%, direct overlapping 10-day ES; square-root-of-time challenge |
| Distribution diagnostics | Cornish-Fisher VaR, skewness, excess kurtosis, downside deviation |
| Dynamic risk | EWMA volatility with lambda 0.94 and rolling 60-day volatility |
| Risk attribution | Sample covariance matrix and Euler component volatility |
| Benchmark analytics | Beta to VN30 and annualised tracking error |
| Liquidity | Base: 20% participation; stress: 10% participation after a 50% volume haircut |
| Rolling diagnostic | 250-day 99% historical VaR, prior returns only, applied to reconstructed current weights |
| Validation | Basel-style traffic light, Kupiec POF, Christoffersen independence/conditional coverage, covariance PSD |
| Hedge | Beta reduction × NAV ÷ VN30 futures index-equivalent notional; margin-liquidity input and buffer |

## Data lineage and proxy policy

- Holdings, company names, reported weights and sector allocation: SSIAM September 2026 ETF factsheet.
- Adjusted prices, VN30 levels and normal traded values: VNDirect Finfo public APIs.
- VN30 futures multiplier: HNX contract specification.
- Backtesting zones: BIS Basel Framework MAR99, used as governance guidance only.
- TCX: Financials proxy excluding TCX in 500-day and 250-day windows; 500-day proxy receives a 1.33x peer-median volatility floor.
- VPL: Consumer Discretionary proxy excluding VPL in the 500-day window; own history in the 250-day window.

## Validation controls

- Analytical weights reconcile to 100%.
- Sector weights reconcile to 100%.
- Euler component-risk shares reconcile to 100%.
- Primary and recent samples contain exactly 500 and 250 observations.
- Latest VaR evaluation contains exactly 250 forecasts and uses no future return.
- Direct 10-day ES contains 241 overlapping windows from the recent 250-day sample.
- The covariance matrix is symmetric and positive semi-definite within a published tolerance.
- Proxy volatility scales are at least 1.00x and are published by security and window.
- Stressed days-to-exit cannot be lower than base days-to-exit.
- Component parametric VaR and sector risk shares each reconcile to 100% of the owning result.
- Hedge beta reconciles to rounded contract notional and the 500-day return replay.
- All 30 holdings have data coverage entries and the common cutoff is 30 September 2026.
- Reproducibility checks run through `scripts/run_checks.py`.
- The browser snapshot is generated from `risk_summary.json` and `project.yaml`; CI fails when published limits or memo results drift from those sources.

## Known limitations

1. Frozen current weights create survivorship and composition bias in historical replays.
2. Sector proxies cannot reproduce issuer-specific jumps; the peer-median volatility floor reduces but does not eliminate this limitation.
3. Carry-forward converts non-trading days into zero return and places the accumulated move on the next quoted day.
4. Direct 10-day ES uses overlapping windows, so the 241 observations are dependent; square-root-of-time ES is only a challenge estimate.
5. Public provider data may differ from official exchange-adjusted series.
6. Liquidity includes a simultaneous participation/volume stress but excludes nonlinear impact, price-limit queues and auction constraints.
7. The hedge includes an initial-margin input and buffer but ignores actual basis, maturity, variation-margin paths, roll, transaction costs and tax.
8. A green backtest zone does not prove the model is correctly specified.
9. Cornish-Fisher expansion can be unstable with extreme higher moments; it is a challenge model, not the sole limit model.
10. Kupiec and Christoffersen tests have limited power with 250 evaluation observations.
11. The rolling diagnostic is not realised fund P&L because 2026 constituents and weights are applied historically.

## Change and monitoring policy

Refresh holdings after index rebalances, rerun prices at each reporting cutoff, compare 250-day and 500-day estimates, and log every proxy change. A model change requires regenerated reports, workbook, checks and memo. Execution use requires independent validation and current official market data.
