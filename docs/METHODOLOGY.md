# Risk methodology design

## Return construction

Use daily adjusted close-to-close log returns for constituent risk estimation. Apply the frozen 30 September 2026 analytical weights to historical constituent returns. This produces a current-weight historical replay and must not be described as the realised return history of FUESSV30.

## Coverage hierarchy

1. Use a security's own history when at least 250 observations are available.
2. If history is shorter, show the observation count and proxy flag.
3. Use a documented sector or VN30 proxy only after the own-history result is shown as unavailable.
4. Apply a conservative idiosyncratic-volatility floor to proxied securities.

## Risk measures

- Historical VaR at 95% and 99% over 250-day and 500-day windows.
- Historical Expected Shortfall at 97.5% and 99%.
- Parametric VaR with a covariance matrix that is checked for positive semi-definiteness.
- Cornish-Fisher VaR as a non-normal challenge model using sample skewness and excess kurtosis.
- EWMA volatility with lambda 0.94 as a responsive comparison, not the sole production measure.
- Component VaR and component volatility using Euler allocation.
- Beta, tracking error, maximum drawdown, HHI and top-name/sector concentration.
- Average pairwise correlation, diversification ratio and sector risk-to-weight ratios.
- Liquidity days-to-exit using a configurable participation rate and trailing median value traded.

## Backtesting

Generate one-day 99% VaR using only the rolling observations available before each realised return. Count exceptions over the latest 250 observations. Use Basel-style zones as a model diagnostic: green for 0–4, amber for 5–9 and red for 10 or more exceptions. This is a portfolio-model governance reference, not a claim of regulatory capital compliance.

Apply the Kupiec probability-of-failure likelihood-ratio test to unconditional exception coverage. Do not interpret a high p-value as proof of independence, correct tail shape or correct proxy construction.

## Stress library

- Data-driven worst 1-day, 5-day and 20-day current-weight replay windows.
- 2022 Vietnam equity deleveraging replay, with the exact window selected from the frozen market series.
- September 2026 sector correction using issuer-reported contribution evidence.
- Hypothetical VN30 market shock with sector add-ons for Financials, Real Estate and Materials.
- Correlation-to-one regime and simultaneous liquidity haircut.
- Reverse stress solving for the smallest VN30 shock that causes the approved NAV loss limit to fail.

## Hedge overlay

The VN30 futures contract notional equals futures price multiplied by VND100,000. The preliminary hedge count is:

`contracts = target beta reduction × portfolio NAV ÷ futures contract notional`

The simulator must show rounded contracts, residual beta, estimated basis risk, margin requirement input and stressed margin liquidity. It must not treat margin as the maximum economic loss.

The hedge comparison recomputes the 500-day portfolio return series after subtracting the rounded futures notional times VN30 returns. It reports volatility, VaR, ES, beta and tracking error before and after the overlay. Target-beta sensitivity uses the covariance identity `var(P-hM) = var(P) + h²var(M) - 2h cov(P,M)`; historical tail statistics remain tied to the fully replayed base hedge.
