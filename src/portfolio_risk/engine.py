"""Dependency-light market-risk engine for the FUESSV30 shadow mandate.

The module deliberately uses only Python's standard library so every published
number can be reproduced without a hidden analytics stack.
"""

from __future__ import annotations

import csv
import json
import math
import statistics
from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Iterable


TRADING_DAYS = 252
Z_99 = 2.326347874


@dataclass(frozen=True)
class Holding:
    ticker: str
    company: str
    sector: str
    reported_weight: float
    analytical_weight: float


def quantile(values: Iterable[float], probability: float) -> float:
    ordered = sorted(values)
    if not ordered:
        raise ValueError("quantile requires observations")
    position = (len(ordered) - 1) * probability
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    return ordered[lower] + (ordered[upper] - ordered[lower]) * (position - lower)


def compound(returns: Iterable[float]) -> float:
    return math.exp(sum(returns)) - 1.0


def load_holdings(path: Path) -> list[Holding]:
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    total = sum(float(row["reported_weight_pct"]) for row in rows) / 100.0
    return [
        Holding(
            ticker=row["ticker"],
            company=row["company"],
            sector=row["sector"],
            reported_weight=float(row["reported_weight_pct"]) / 100.0,
            analytical_weight=(float(row["reported_weight_pct"]) / 100.0) / total,
        )
        for row in rows
    ]


def load_benchmark(path: Path) -> tuple[list[str], dict[str, float]]:
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    closes = {row["date"]: float(row["close"]) for row in rows}
    dates = sorted(closes)
    return dates, closes


def load_stock_data(path: Path) -> tuple[dict[str, dict[str, float]], dict[str, list[float]]]:
    prices: dict[str, dict[str, float]] = defaultdict(dict)
    traded_values: dict[str, list[tuple[str, float]]] = defaultdict(list)
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            ticker = row["ticker"]
            prices[ticker][row["date"]] = float(row["adjusted_close_vnd"])
            if row["normal_value_vnd"]:
                traded_values[ticker].append((row["date"], float(row["normal_value_vnd"])))
    trailing: dict[str, list[float]] = {}
    for ticker, observations in traded_values.items():
        eligible = [value for day, value in observations if day <= "2026-09-30"]
        trailing[ticker] = eligible[-60:]
    return dict(prices), trailing


def aligned_log_returns(
    dates: list[str], raw_prices: dict[str, float]
) -> tuple[dict[str, float | None], int, str | None, str | None]:
    """Align prices to the benchmark calendar using last-observation carry-forward."""
    returns: dict[str, float | None] = {}
    last_price: float | None = None
    missing_quote_days = 0
    observed_dates = sorted(raw_prices)
    first = observed_dates[0] if observed_dates else None
    last = observed_dates[-1] if observed_dates else None
    for day in dates:
        observed = raw_prices.get(day)
        if observed is None:
            if last_price is not None:
                returns[day] = 0.0
                missing_quote_days += 1
            else:
                returns[day] = None
            continue
        if last_price is None:
            returns[day] = None
        else:
            returns[day] = math.log(observed / last_price)
        last_price = observed
    return returns, missing_quote_days, first, last


def weighted_series(
    dates: list[str], members: list[tuple[float, dict[str, float | None]]]
) -> dict[str, float | None]:
    result: dict[str, float | None] = {}
    for day in dates:
        available = [(weight, series[day]) for weight, series in members if series[day] is not None]
        denominator = sum(weight for weight, _ in available)
        result[day] = (
            sum(weight * float(value) for weight, value in available) / denominator
            if denominator
            else None
        )
    return result


def covariance(left: list[float], right: list[float]) -> float:
    if len(left) != len(right) or len(left) < 2:
        raise ValueError("covariance requires equal series with at least two observations")
    mean_left = statistics.fmean(left)
    mean_right = statistics.fmean(right)
    return sum((x - mean_left) * (y - mean_right) for x, y in zip(left, right)) / (len(left) - 1)


def risk_stats(returns: list[float]) -> dict[str, float]:
    mean = statistics.fmean(returns)
    daily_vol = statistics.stdev(returns)
    q95 = quantile(returns, 0.05)
    q99 = quantile(returns, 0.01)
    q975 = quantile(returns, 0.025)
    centered = [value - mean for value in returns]
    skewness = statistics.fmean(value ** 3 for value in centered) / daily_vol ** 3
    excess_kurtosis = statistics.fmean(value ** 4 for value in centered) / daily_vol ** 4 - 3.0
    cornish_fisher_z = (
        Z_99
        + (Z_99 ** 2 - 1) * skewness / 6
        + (Z_99 ** 3 - 3 * Z_99) * excess_kurtosis / 24
        - (2 * Z_99 ** 3 - 5 * Z_99) * skewness ** 2 / 36
    )
    downside = [min(0.0, value) ** 2 for value in returns]
    return {
        "observations": len(returns),
        "annualised_volatility": daily_vol * math.sqrt(TRADING_DAYS),
        "historical_var_95": max(0.0, -q95),
        "historical_var_99": max(0.0, -q99),
        "historical_es_975": max(0.0, -statistics.fmean(x for x in returns if x <= q975)),
        "historical_es_99": max(0.0, -statistics.fmean(x for x in returns if x <= q99)),
        "parametric_var_99": max(0.0, Z_99 * daily_vol - mean),
        "cornish_fisher_var_99": max(0.0, cornish_fisher_z * daily_vol - mean),
        "skewness": skewness,
        "excess_kurtosis": excess_kurtosis,
        "annualised_downside_deviation": math.sqrt(statistics.fmean(downside)) * math.sqrt(TRADING_DAYS),
        "daily_mean": mean,
    }


def ewma_volatility(returns: list[float], decay: float = 0.94) -> float:
    variance = statistics.variance(returns)
    for value in returns:
        variance = decay * variance + (1.0 - decay) * value ** 2
    return math.sqrt(variance) * math.sqrt(TRADING_DAYS)


def average_pairwise_correlation(matrix: dict[str, list[float]], start: int = 0) -> float:
    tickers = list(matrix)
    correlations = []
    for i, left in enumerate(tickers):
        left_values = matrix[left][start:]
        left_vol = statistics.stdev(left_values)
        for right in tickers[i + 1 :]:
            right_values = matrix[right][start:]
            right_vol = statistics.stdev(right_values)
            if left_vol and right_vol:
                correlations.append(covariance(left_values, right_values) / (left_vol * right_vol))
    return statistics.fmean(correlations)


def kupiec_test(exception_count: int, observations: int, expected_rate: float = 0.01) -> dict[str, float]:
    observed_rate = exception_count / observations
    bounded_rate = min(max(observed_rate, 1e-12), 1 - 1e-12)
    log_null = (observations - exception_count) * math.log(1 - expected_rate) + exception_count * math.log(expected_rate)
    log_alt = (observations - exception_count) * math.log(1 - bounded_rate) + exception_count * math.log(bounded_rate)
    statistic = max(0.0, -2.0 * (log_null - log_alt))
    return {"likelihood_ratio": statistic, "p_value": math.erfc(math.sqrt(statistic / 2.0)), "observed_rate": observed_rate}


def max_drawdown(returns: list[float]) -> float:
    wealth = peak = 1.0
    worst = 0.0
    for value in returns:
        wealth *= math.exp(value)
        peak = max(peak, wealth)
        worst = min(worst, wealth / peak - 1.0)
    return worst


def worst_window(dates: list[str], returns: list[float], width: int) -> dict[str, float | str]:
    candidates = []
    for end in range(width - 1, len(returns)):
        loss = compound(returns[end - width + 1 : end + 1])
        candidates.append((loss, end))
    loss, end = min(candidates)
    return {"start": dates[end - width + 1], "end": dates[end], "return": loss}


def period_return(dates: list[str], returns: list[float], start: str, end: str) -> dict[str, float | str | int]:
    selected = [value for day, value in zip(dates, returns) if start <= day <= end]
    return {"start": start, "end": end, "observations": len(selected), "return": compound(selected)}


def backtest(dates: list[str], returns: list[float], lookback: int = 250) -> dict:
    forecasts = []
    for index in range(lookback, len(returns)):
        var = max(0.0, -quantile(returns[index - lookback : index], 0.01))
        forecasts.append({
            "date": dates[index],
            "var_99": var,
            "realised_loss": max(0.0, -returns[index]),
            "exception": int(returns[index] < -var),
        })
    latest = forecasts[-250:]
    exceptions = sum(row["exception"] for row in latest)
    zone = "green" if exceptions <= 4 else "amber" if exceptions <= 9 else "red"
    return {"lookback": lookback, "evaluation_observations": len(latest), "exceptions": exceptions, "zone": zone, "series": latest}


def run_analysis(root: Path) -> dict:
    holdings = load_holdings(root / "data/sample/holdings_2026-09-30.csv")
    dates, benchmark_prices = load_benchmark(root / "data/market/vn30_index.csv")
    raw_prices, trailing_values = load_stock_data(root / "data/market/constituent_prices.csv")
    as_of = "2026-09-30"
    dates = [day for day in dates if day <= as_of]

    own: dict[str, dict[str, float | None]] = {}
    audit = []
    by_ticker = {holding.ticker: holding for holding in holdings}
    for ticker, prices in raw_prices.items():
        series, missing, first, last = aligned_log_returns(dates, prices)
        own[ticker] = series
        usable = sum(series[day] is not None for day in dates[-500:])
        audit.append({
            "ticker": ticker,
            "sector": by_ticker[ticker].sector,
            "first_date": first,
            "last_date": last,
            "raw_price_rows": len(prices),
            "usable_returns_last_500": usable,
            "missing_quote_days_after_listing": missing,
            "primary_500d_method": "own" if usable >= 500 else "sector_proxy",
            "recent_250d_method": "own" if sum(series[day] is not None for day in dates[-250:]) >= 250 else "sector_proxy",
        })

    stock_holdings = [holding for holding in holdings if holding.ticker != "CASH"]
    sector_members: dict[str, list[Holding]] = defaultdict(list)
    for holding in stock_holdings:
        sector_members[holding.sector].append(holding)
    sector_proxy: dict[str, dict[str, float | None]] = {}
    for sector, members in sector_members.items():
        sector_proxy[sector] = weighted_series(
            dates, [(member.analytical_weight, own[member.ticker]) for member in members]
        )

    def build_matrix(window: int) -> tuple[list[str], dict[str, list[float]], dict[str, str]]:
        selected_dates = dates[-window:]
        matrix: dict[str, list[float]] = {}
        methods: dict[str, str] = {}
        for holding in stock_holdings:
            candidate = own[holding.ticker]
            own_values = [candidate[day] for day in selected_dates]
            if all(value is not None for value in own_values):
                chosen = candidate
                methods[holding.ticker] = "own"
            else:
                peers = [member for member in sector_members[holding.sector] if member.ticker != holding.ticker]
                chosen = weighted_series(dates, [(m.analytical_weight, own[m.ticker]) for m in peers]) if peers else sector_proxy[holding.sector]
                methods[holding.ticker] = "sector_proxy_excluding_self"
            matrix[holding.ticker] = [float(chosen[day] or 0.0) for day in selected_dates]
        return selected_dates, matrix, methods

    primary_dates, primary_matrix, primary_methods = build_matrix(500)
    recent_dates, recent_matrix, recent_methods = build_matrix(250)
    weights = {holding.ticker: holding.analytical_weight for holding in stock_holdings}
    cash_weight = by_ticker["CASH"].analytical_weight

    def portfolio_from_matrix(matrix: dict[str, list[float]], count: int) -> list[float]:
        return [sum(weights[ticker] * matrix[ticker][i] for ticker in matrix) for i in range(count)]

    primary_portfolio = portfolio_from_matrix(primary_matrix, len(primary_dates))
    recent_portfolio = portfolio_from_matrix(recent_matrix, len(recent_dates))

    benchmark_returns: dict[str, float | None] = {}
    previous = None
    for day in dates:
        price = benchmark_prices[day]
        benchmark_returns[day] = None if previous is None else math.log(price / previous)
        previous = price
    primary_benchmark = [float(benchmark_returns[day]) for day in primary_dates]
    portfolio_market_covariance = covariance(primary_portfolio, primary_benchmark)
    benchmark_variance = covariance(primary_benchmark, primary_benchmark)
    beta = portfolio_market_covariance / benchmark_variance
    tracking = [portfolio - market for portfolio, market in zip(primary_portfolio, primary_benchmark)]

    # Full current-weight replay: explicit sector proxy before an issuer has history.
    full_dates = [day for day in dates if benchmark_returns[day] is not None]
    full_matrix: dict[str, list[float]] = {}
    for holding in stock_holdings:
        proxy = sector_proxy[holding.sector]
        full_matrix[holding.ticker] = [
            float(own[holding.ticker][day] if own[holding.ticker][day] is not None else proxy[day] or 0.0)
            for day in full_dates
        ]
    full_portfolio = portfolio_from_matrix(full_matrix, len(full_dates))

    covariance_matrix: dict[tuple[str, str], float] = {}
    for left in weights:
        for right in weights:
            covariance_matrix[(left, right)] = covariance(primary_matrix[left], primary_matrix[right])
    daily_portfolio_vol = math.sqrt(sum(weights[i] * weights[j] * covariance_matrix[(i, j)] for i in weights for j in weights))
    contributions = []
    for holding in stock_holdings:
        marginal = sum(covariance_matrix[(holding.ticker, other)] * weights[other] for other in weights) / daily_portfolio_vol
        component = holding.analytical_weight * marginal
        contributions.append({
            "ticker": holding.ticker,
            "sector": holding.sector,
            "analytical_weight": holding.analytical_weight,
            "component_annualised_volatility": component * math.sqrt(TRADING_DAYS),
            "share_of_total_volatility": component / daily_portfolio_vol,
            "marginal_annualised_volatility": marginal * math.sqrt(TRADING_DAYS),
            "model_method_500d": primary_methods[holding.ticker],
        })
    contributions.sort(key=lambda row: row["component_annualised_volatility"], reverse=True)

    sector_weights = defaultdict(float)
    for holding in holdings:
        sector_weights[holding.sector] += holding.analytical_weight
    top_five = sum(sorted((h.analytical_weight for h in stock_holdings), reverse=True)[:5])
    hhi = sum(holding.analytical_weight ** 2 for holding in holdings)

    liquidity = []
    nav = 100_000_000_000
    for holding in stock_holdings:
        values = trailing_values.get(holding.ticker, [])
        median_value = statistics.median(values) if values else 0.0
        position = holding.analytical_weight * nav
        days_to_exit = position / (0.20 * median_value) if median_value else None
        liquidity.append({
            "ticker": holding.ticker,
            "position_vnd": position,
            "median_60d_traded_value_vnd": median_value,
            "participation_rate": 0.20,
            "days_to_exit": days_to_exit,
        })
    liquidity.sort(key=lambda row: row["days_to_exit"] or math.inf, reverse=True)

    hypothetical_shocks = {
        "Financials": -0.18, "Real Estate": -0.25, "Materials": -0.20,
        "Information Technology": -0.15, "Consumer Discretionary": -0.17,
        "Consumer Staples": -0.10, "Industrials": -0.14, "Energy": -0.08,
        "Utilities": -0.07, "Cash": 0.0,
    }
    hypothetical_loss = sum(weight * hypothetical_shocks[sector] for sector, weight in sector_weights.items())
    individual_vols = {ticker: statistics.stdev(series) for ticker, series in primary_matrix.items()}
    correlation_one_var = Z_99 * sum(weights[ticker] * individual_vols[ticker] for ticker in weights)

    primary = risk_stats(primary_portfolio)
    recent = risk_stats(recent_portfolio)
    primary["ewma_94_annualised_volatility"] = ewma_volatility(primary_portfolio)
    recent["ewma_94_annualised_volatility"] = ewma_volatility(recent_portfolio)
    for row in contributions:
        row["component_parametric_var_99"] = row["share_of_total_volatility"] * primary["parametric_var_99"]
    ten_day_es_975 = recent["historical_es_975"] * math.sqrt(10)
    backtest_result = backtest(full_dates, full_portfolio)
    coverage_test = kupiec_test(backtest_result["exceptions"], backtest_result["evaluation_observations"])

    weighted_standalone_vol = sum(weights[ticker] * individual_vols[ticker] for ticker in weights) * math.sqrt(TRADING_DAYS)
    diversification_ratio = weighted_standalone_vol / primary["annualised_volatility"]
    long_correlation = average_pairwise_correlation(primary_matrix)
    recent_60d_correlation = average_pairwise_correlation(primary_matrix, -60)

    sector_risk = defaultdict(lambda: {"weight": 0.0, "share_of_total_volatility": 0.0})
    for row in contributions:
        sector_risk[row["sector"]]["weight"] += row["analytical_weight"]
        sector_risk[row["sector"]]["share_of_total_volatility"] += row["share_of_total_volatility"]
    sector_risk_rows = [
        {
            "sector": sector,
            "weight": values["weight"],
            "share_of_total_volatility": values["share_of_total_volatility"],
            "risk_to_weight_ratio": values["share_of_total_volatility"] / values["weight"] if values["weight"] else None,
        }
        for sector, values in sector_risk.items()
    ]
    sector_risk_rows.sort(key=lambda row: row["share_of_total_volatility"], reverse=True)

    index_level = 1906.81
    contract_notional = index_level * 100_000
    target_beta = 0.70
    raw_contracts = max(0.0, (beta - target_beta) * nav / contract_notional)
    contracts = round(raw_contracts)
    residual_beta = beta - contracts * contract_notional / nav
    hedge_ratio = contracts * contract_notional / nav
    hedged_returns = [portfolio - hedge_ratio * market for portfolio, market in zip(primary_portfolio, primary_benchmark)]
    hedged_tracking = [value - market for value, market in zip(hedged_returns, primary_benchmark)]
    hedged = risk_stats(hedged_returns)
    hedged_beta = covariance(hedged_returns, primary_benchmark) / covariance(primary_benchmark, primary_benchmark)
    hedge_comparison = {
        "unhedged_annualised_volatility": primary["annualised_volatility"],
        "hedged_annualised_volatility": hedged["annualised_volatility"],
        "unhedged_var_99": primary["historical_var_99"],
        "hedged_var_99": hedged["historical_var_99"],
        "unhedged_es_975": primary["historical_es_975"],
        "hedged_es_975": hedged["historical_es_975"],
        "unhedged_tracking_error": statistics.stdev(tracking) * math.sqrt(TRADING_DAYS),
        "hedged_tracking_error": statistics.stdev(hedged_tracking) * math.sqrt(TRADING_DAYS),
        "hedged_beta": hedged_beta,
        "var_reduction": 1.0 - hedged["historical_var_99"] / primary["historical_var_99"],
        "volatility_reduction": 1.0 - hedged["annualised_volatility"] / primary["annualised_volatility"],
    }

    rolling_risk = []
    for index in range(249, len(full_portfolio)):
        window = full_portfolio[index - 249 : index + 1]
        if index % 5 == 0 or index == len(full_portfolio) - 1:
            rolling_risk.append({
                "date": full_dates[index],
                "annualised_volatility_60d": statistics.stdev(full_portfolio[max(0, index - 59) : index + 1]) * math.sqrt(TRADING_DAYS),
                "historical_var_99_250d": max(0.0, -quantile(window, 0.01)),
                "drawdown": None,
            })
    wealth = peak = 1.0
    drawdown_by_date = {}
    for day, value in zip(full_dates, full_portfolio):
        wealth *= math.exp(value)
        peak = max(peak, wealth)
        drawdown_by_date[day] = wealth / peak - 1.0
    for row in rolling_risk:
        row["drawdown"] = drawdown_by_date[row["date"]]

    largest = max(stock_holdings, key=lambda item: item.analytical_weight)
    largest_sector, largest_sector_weight = max(sector_weights.items(), key=lambda item: item[1])
    maximum_dte = max(row["days_to_exit"] or math.inf for row in liquidity)
    breaches = {
        "single_name": largest.analytical_weight > 0.11,
        "sector": largest_sector_weight > 0.40,
        "top_five": top_five > 0.45,
        "one_day_var_99": primary["historical_var_99"] > 0.035,
        "ten_day_es_975": ten_day_es_975 > 0.12,
        "liquidity_days_to_exit": maximum_dte > 5,
        "backtest_green_zone": backtest_result["exceptions"] > 4,
    }

    return {
        "case": {
            "as_of": as_of, "portfolio": "FUESSV30 current-weight shadow mandate",
            "shadow_nav_vnd": nav, "benchmark": "VN30", "reported_weight_total": sum(h.reported_weight for h in holdings),
            "analytical_weight_total": sum(h.analytical_weight for h in holdings), "cash_weight": cash_weight,
        },
        "risk": {
            "primary_500d": primary, "recent_250d": recent, "ten_day_es_975_sqrt_time": ten_day_es_975,
            "beta_to_vn30": beta, "tracking_error_annualised": statistics.stdev(tracking) * math.sqrt(TRADING_DAYS),
            "maximum_drawdown_full_replay": max_drawdown(full_portfolio),
            "diversification_ratio": diversification_ratio,
            "weighted_standalone_volatility": weighted_standalone_vol,
            "average_pairwise_correlation_500d": long_correlation,
            "average_pairwise_correlation_recent_60d": recent_60d_correlation,
            "benchmark_annualised_volatility": statistics.stdev(primary_benchmark) * math.sqrt(TRADING_DAYS),
            "portfolio_benchmark_annualised_covariance": portfolio_market_covariance * TRADING_DAYS,
        },
        "concentration": {
            "largest_name": largest.ticker, "largest_name_weight": largest.analytical_weight,
            "largest_sector": largest_sector, "largest_sector_weight": largest_sector_weight,
            "top_five_weight": top_five, "hhi": hhi, "sector_weights": dict(sorted(sector_weights.items())),
        },
        "stress": {
            "worst_1d": worst_window(full_dates, full_portfolio, 1),
            "worst_5d": worst_window(full_dates, full_portfolio, 5),
            "worst_20d": worst_window(full_dates, full_portfolio, 20),
            "vietnam_2022_replay": period_return(full_dates, full_portfolio, "2022-04-04", "2022-11-15"),
            "september_2026_replay": period_return(full_dates, full_portfolio, "2026-08-31", "2026-09-30"),
            "hypothetical_sector_shock": hypothetical_loss,
            "hypothetical_sector_vector": hypothetical_shocks,
            "correlation_one_parametric_var_99": correlation_one_var,
            "reverse_stress_vn30_shock_for_15pct_loss": -0.15 / beta,
        },
        "backtest": {**{key: value for key, value in backtest_result.items() if key != "series"}, "kupiec_pof": coverage_test},
        "hedge": {
            "index_level_proxy": index_level, "contract_multiplier": 100_000,
            "contract_notional_vnd": contract_notional, "current_beta": beta, "target_beta": target_beta,
            "raw_short_contracts": raw_contracts, "rounded_short_contracts": contracts,
            "residual_beta": residual_beta,
            "comparison": hedge_comparison,
            "disclaimer": "Index-equivalent only; replace the index level with the selected VN30 futures settlement price before execution.",
        },
        "limits": {"breaches": breaches, "breach_count": sum(breaches.values())},
        "coverage_audit": sorted(audit, key=lambda row: row["ticker"]),
        "component_risk": contributions,
        "sector_risk": sector_risk_rows,
        "liquidity": liquidity,
        "backtest_series": backtest_result["series"],
        "rolling_risk": rolling_risk,
        "model_methods": {"primary_500d": primary_methods, "recent_250d": recent_methods},
    }


def write_outputs(root: Path, result: dict) -> None:
    reports = root / "reports"
    reports.mkdir(exist_ok=True)
    (reports / "risk_summary.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    tables = {
        "coverage_audit.csv": result["coverage_audit"],
        "risk_contributions.csv": result["component_risk"],
        "sector_risk.csv": result["sector_risk"],
        "liquidity.csv": result["liquidity"],
        "var_backtest.csv": result["backtest_series"],
        "rolling_risk.csv": result["rolling_risk"],
    }
    for filename, rows in tables.items():
        with (reports / filename).open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
