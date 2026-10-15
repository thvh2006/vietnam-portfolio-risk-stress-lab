# Sample data

## `holdings_2026-09-30.csv`

Frozen SSIAM VN30 ETF portfolio weights transcribed from the issuer's September 2026 performance report. The 30 reported stock weights sum to 99.85%; reported cash is 0.17%. The 100.02% combined total is a disclosure-rounding effect.

The raw reported percentages must remain unchanged. The analytical layer may normalise them to 100%, but it must retain both fields and disclose the 0.02 percentage-point reconciliation difference.

## Market-price snapshots

Run `scripts/fetch_market_data.py` to create long-form constituent and VN30 index histories. Stock prices are stored in VND; the provider endpoint expresses quoted stock prices in VND thousands, so the script applies an explicit 1,000 conversion. The VN30 index level is not scaled.

Adjusted prices can change when providers apply later corporate actions. Every refresh therefore records its retrieval timestamp, query window and row counts. A production risk process would use licensed point-in-time data.
