# Model Card — Vietnam Portfolio Risk & Stress Lab

## Intended use

Independent market-risk demonstration for a VND100 billion shadow mandate based on the publicly disclosed 30 September 2026 FUESSV30 portfolio. It supports risk-committee discussion of tail loss, concentration, liquidity and a VN30 futures overlay. It is not investment advice, a regulatory capital model or an executable hedge instruction.

## Model specification

| Item | Specification |
|---|---|
| Portfolio | Current reported FUESSV30 holdings, analytically normalised from 100.02% to 100.00% |
| Returns | Daily adjusted close log returns; benchmark-calendar carry-forward for missing quote days |
| Primary / recent windows | 500 / 250 trading days |
| Tail risk | Historical VaR 95%/99%, ES 97.5%/99%; parametric 99% VaR comparison |
| Distribution diagnostics | Cornish-Fisher VaR, skewness, excess kurtosis, downside deviation |
| Dynamic risk | EWMA volatility with lambda 0.94 and rolling 60-day volatility |
| Risk attribution | Sample covariance matrix and Euler component volatility |
| Benchmark analytics | Beta to VN30 and annualised tracking error |
| Liquidity | Position value divided by 20% of trailing 60-observation median traded value |
| Backtest | Rolling 250-day 99% historical VaR, prior observations only |
| Validation | Basel-style traffic light and Kupiec unconditional-coverage test |
| Hedge | Beta reduction × NAV ÷ VN30 futures index-equivalent notional |

## Data lineage and proxy policy

- Holdings, company names, reported weights and sector allocation: SSIAM September 2026 ETF factsheet.
- Adjusted prices, VN30 levels and normal traded values: VNDirect Finfo public APIs.
- VN30 futures multiplier: HNX contract specification.
- Backtesting zones: BIS Basel Framework MAR99, used as governance guidance only.
- TCX: Financials proxy excluding TCX in 500-day and 250-day windows.
- VPL: Consumer Discretionary proxy excluding VPL in the 500-day window; own history in the 250-day window.

## Validation controls

- Analytical weights reconcile to 100%.
- Sector weights reconcile to 100%.
- Euler component-risk shares reconcile to 100%.
- Primary and recent samples contain exactly 500 and 250 observations.
- Latest VaR evaluation contains exactly 250 forecasts and uses no future return.
- Component parametric VaR and sector risk shares each reconcile to 100% of the owning result.
- Hedge beta reconciles to rounded contract notional and the 500-day return replay.
- All 30 holdings have data coverage entries and the common cutoff is 30 September 2026.
- Reproducibility checks run through `scripts/run_checks.py`.

## Known limitations

1. Frozen current weights create survivorship and composition bias in historical replays.
2. Sector proxies suppress issuer-specific risk and may understate IPO or newly listed security risk.
3. Carry-forward converts non-trading days into zero return and places the accumulated move on the next quoted day.
4. Square-root-of-time ES scaling assumes stable, independent daily risk and is only a limit-comparison approximation.
5. Public provider data may differ from official exchange-adjusted series.
6. Liquidity excludes market impact, price-limit queues, auction constraints and stressed volume decay.
7. The hedge ignores actual futures basis, maturity, roll, margin calls, transaction costs and tax.
8. A green backtest zone does not prove the model is correctly specified.
9. Cornish-Fisher expansion can be unstable with extreme higher moments; it is a challenge model, not the sole limit model.
10. Kupiec POF tests unconditional coverage only and has limited power with 250 observations.

## Change and monitoring policy

Refresh holdings after index rebalances, rerun prices at each reporting cutoff, compare 250-day and 500-day estimates, and log every proxy change. A model change requires regenerated reports, workbook, checks and memo. Execution use requires independent validation and current official market data.
