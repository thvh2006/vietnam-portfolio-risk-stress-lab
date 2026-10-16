# Risk Committee Memo — FUESSV30 Shadow Mandate

**As of:** 30 September 2026  
**Mandate:** VND100 billion current-weight shadow portfolio  
**Decision:** retain the exposure under the current risk budget; preserve a VN30 futures overlay as a contingency for a tighter absolute-risk mandate.

## Executive decision

The portfolio is inside the proposed risk budget. One-day 99% historical VaR is **3.40% of NAV**, below the 3.50% limit. Direct overlapping 10-day 97.5% Expected Shortfall is **9.30%**, below the 12.00% limit. The square-root-of-time challenge is **12.30%** and remains visible as a conservative comparison. The rolling diagnostic records **2 exceptions in the latest 250 forecasts**, a Basel-style green-zone result.

Largest-name, largest-sector and top-five weights remain within the proposed limits. At the VND100 billion shadow scale, all positions can be liquidated within one trading day at the assumed 20% participation rate; MCH is the slowest at approximately 0.40 day. Under a simultaneous 10% participation rate and 50% volume haircut, the maximum rises to approximately 1.61 days and remains below the five-day limit.

**Recommended action:** retain the unhedged exposure under the current budget. For a tighter absolute-risk mandate, reduce beta toward 0.70 using approximately **152 short VN30 index-equivalent contracts**, subject to execution controls. This is a sizing illustration, not an executable order. At the 17% VSDC minimum initial-margin input, the position requires approximately **VND4.93 billion**, rising to **VND7.39 billion** under the 1.5x liquidity buffer. The exact contract, settlement price, basis and roll policy must still be set before implementation.

## Model challenge

The tail conclusion is estimator-sensitive. Normal 99% VaR is only **2.87%**, historical VaR is **3.40%**, and Cornish-Fisher VaR is **4.17%**. The 500-day return distribution has skewness of **-0.80** and excess kurtosis of **7.87**, so a normal model materially understates downside risk. The committee should therefore use historical ES and stress results for the limit decision, with normal VaR retained only as a diagnostic.

EWMA volatility is **14.23%**, well below the 20.22% 500-day estimate. This indicates a calmer current regime, not evidence that the older tail observations are irrelevant. Average pairwise correlation is 0.37 over 500 days and 0.35 over the latest 60 days. The present regime is not showing a broad correlation spike.

## What drives the result

- **VIC** is the largest constituent at 10.62% and contributes 13.54% of total portfolio volatility.
- Financials are 39.83% of NAV, only 0.17 percentage point below the 40% sector limit.
- HPG, MWG and FPT each contribute roughly 7.9%–8.4% of total volatility after VIC.
- Portfolio beta to VN30 is 0.99 and annualised tracking error is 2.35%, consistent with a passive reference portfolio.
- The 500-day annualised volatility estimate is 20.22%; the recent 250-day estimate is slightly higher at 20.63%.
- Real Estate contributes **21.85% of total volatility** from a 16.88% weight, a risk-to-weight ratio of 1.29. Financials contributes 38.57% of volatility from 39.83% of weight.
- The diversification ratio is 1.64, so diversification is meaningful but does not neutralise left-tail dependence.

## Hedge trade-off

The 152-contract index-equivalent overlay reduces estimated annualised volatility from **20.22% to 14.40%**, historical 99% VaR from **3.40% to 2.46%**, and historical 97.5% ES from **4.16% to 2.97%**. The cost is mandate drift: tracking error rises from **2.35% to 6.52%**. The overlay is therefore appropriate only when absolute loss control has priority over index replication.

The Kupiec unconditional-coverage p-value is **0.742**, the Christoffersen independence p-value is **0.857**, and the combined conditional-coverage p-value is **0.932**. None is rejected at 5%. These are rolling diagnostics on a reconstructed current-weight portfolio, not a production out-of-sample backtest of realised fund P&L.

## Stress outcomes

| Scenario | Portfolio result | VND100bn impact |
|---|---:|---:|
| Worst historical day | -7.24% | -VND7.24bn |
| Worst historical 5-day window | -15.40% | -VND15.40bn |
| 2022 deleveraging replay | -41.62% | -VND41.62bn |
| Hypothetical sector shock | -17.64% | -VND17.64bn |
| Reverse stress: VN30 shock for 15% loss | -15.15% | threshold |

Historical figures are **current-weight replays**, not realised FUESSV30 returns. The 2022 replay therefore answers how today's portfolio would have behaved under that return environment; it does not reconstruct past fund holdings.

## Model governance

The primary model uses 500 daily observations and a 250-day recent comparison. TCX lacks sufficient history in both windows and uses a Financials proxy excluding TCX; its 500-day proxy receives a 1.33x peer-median volatility floor. VPL uses a Consumer Discretionary proxy in the 500-day model and its own history in the 250-day model. The covariance matrix passes a positive-semidefinite check. Proxy use and scaling are disclosed in the audit.

Market prices and traded values come from VNDirect Finfo public endpoints and are provider data, not official exchange records. Holdings and sector weights come from SSIAM's September 2026 factsheet. The futures multiplier comes from HNX. Results must be refreshed before any real capital decision.

## Conditions for approval

1. Select the exact VN30 futures maturity and replace the index proxy with its settlement price.
2. Confirm broker margin, basis and roll-cost inputs before treating the hedge as executable.
3. Review direct and challenge ES, Financials weight and VIC component risk at each risk review.
4. Re-estimate the model after material index rebalancing or constituent corporate action.
5. Escalate if VaR backtesting leaves the green zone, not only when the point estimate breaches.
