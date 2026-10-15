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
- 10-day 97.5% ES is 12.28% versus a 12.00% limit.
- Normal 99% VaR is 2.87%, while Cornish-Fisher VaR is 4.16% because the sample has -0.80 skewness and 7.87 excess kurtosis.
- Rolling backtesting records 2 exceptions in 250 forecasts. The Kupiec POF p-value is 0.742.

### Investment outcome

For a benchmark-tracking mandate, retain the unhedged exposure and approve a temporary ES exception. For an absolute-risk mandate, a 151-contract index-equivalent overlay reduces beta toward 0.70 and historical VaR to 2.46%, but raises tracking error to 6.51%. Execution still requires an actual contract, settlement price, margin, basis and roll policy.
