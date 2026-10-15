# Research log

## 2026-10-13 — Real case selected

### Question

Which public Vietnam portfolio provides enough position, benchmark and operational disclosure for a senior-level risk and stress-testing case?

### Evidence

- SSIAM publishes the FUESSV30 benchmark, NAV, daily creation basket and disclosure archive.
- The September 2026 report provides all 30 stock weights, cash, sector allocation, fund performance and benchmark performance at one common cutoff.
- The portfolio is concentrated enough to create meaningful single-name, sector and correlation decisions.
- VN30 futures provide a real hedge instrument with an exchange-published VND100,000 multiplier.

### Decision

Use the SSIAM VN30 ETF portfolio as of 30 September 2026. Scale it to a VND100 billion shadow mandate. Preserve the passive fund's stated strategy as context, but place any hedge decision within the separate shadow mandate.

### Known issues

- Published weights are rounded and sum to 100.02% including cash.
- TCX and VPL have limited trading histories.
- Adjusted historical prices are provider-maintained rather than licensed point-in-time exchange data.
- Current-weight replay contains survivorship and composition bias and is not realised fund performance.

### Next query

Does every holding have enough clean price and liquidity history to support the primary 250-day and secondary 500-day risk windows?

## 2026-10-15 - Model challenge and decision completed

### Coverage result

- TCX requires a Financials proxy in both estimation windows.
- VPL requires a Consumer Discretionary proxy in the 500-day window and uses its own history in the 250-day window.
- All proxy use excludes the issuer itself and is visible in the coverage audit.

### Risk result

- 500-day historical 99% VaR is 3.39% versus a 3.50% limit.
- The initial square-root-of-time 10-day 97.5% ES estimate was 12.28% versus a 12.00% limit; v1.1 supersedes this as the limit owner after a direct multi-day calculation.
- Normal 99% VaR is 2.87%, while Cornish-Fisher VaR is 4.16% because the sample has -0.80 skewness and 7.87 excess kurtosis.
- Rolling backtesting records 2 exceptions in 250 forecasts. The Kupiec POF p-value is 0.742.

### Investment outcome

This preliminary outcome was superseded by the v1.1 direct 10-day method below. The hedge economics remain a contingency analysis rather than an executable recommendation.

## 2026-10-15 - v1.1 model-governance correction

### Research question

Does the marginal 10-day ES breach survive a direct multi-day calculation, and are the methodology claims implemented in code?

### Result

- Direct overlapping 10-day 97.5% ES is 9.30% from 241 windows and passes the 12% limit.
- Square-root-of-time ES is 12.30% and remains a conservative challenge, not the limit owner.
- The 500-day covariance matrix passes the positive-semidefinite check.
- TCX's 500-day proxy is scaled 1.33x to the peer-median volatility floor; VPL's floor does not require an uplift.
- Stressed liquidity uses 10% participation and a 50% volume haircut; the worst days-to-exit rises from 0.40 to 1.61.
- Kupiec, Christoffersen independence and conditional-coverage tests are not rejected at 5%.
- VSDC's notice effective 18 September 2026 supplies a 17% minimum initial-margin input. The illustrated hedge requires VND4.93bn initially and VND7.39bn under a 1.5x buffer.

### Governance decision

Retain the unhedged portfolio under the current budget. Label the historical validation as a rolling current-weight diagnostic because current constituents and weights are replayed through history. Keep the futures overlay as a contingency rather than a recommendation.
