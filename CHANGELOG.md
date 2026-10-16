# Changelog

## v1.1.1 - 2026-10-16

- Made the public dashboard consume a generated snapshot from the reviewed risk output and policy configuration.
- Corrected the public single-name limit from 12.00% to the approved 11.00%.
- Reconciled the investment-committee memo to the current risk, attribution and stress outputs.
- Added CI controls that fail when the dashboard snapshot or committee memo drifts from the model output.
- Published the live dashboard source and updated release links as one tagged repository state.

## v1.1.0 - 2026-10-15

- Replaced square-root-of-time 10-day ES as the limit owner with direct overlapping 10-day ES; retained sqrt-time as a challenge.
- Added excluding-self peer-median volatility floors for short-history proxies.
- Added covariance positive-semidefinite validation.
- Added Christoffersen independence and conditional-coverage diagnostics.
- Added simultaneous liquidity stress and futures initial/stressed margin liquidity.
- Relabelled historical validation as a rolling current-weight diagnostic, not realised fund-P&L backtesting.
- Clarified which workbook outputs are Python snapshots and which controls recalculate live.

## v1.0.0 - 2026-10-15

- Added frozen FUESSV30 holdings and Vietnam market-data snapshot.
- Added historical, parametric and Cornish-Fisher VaR plus Expected Shortfall.
- Added EWMA and rolling regime diagnostics.
- Added Euler component risk, sector attribution and liquidity capacity.
- Added historical, hypothetical, correlation and reverse stress testing.
- Added VaR traffic-light and Kupiec POF validation.
- Added VN30 futures target-beta sensitivity and hedge trade-off analysis.
- Added formula-driven Excel workbook, PDF report, model card and CI checks.
