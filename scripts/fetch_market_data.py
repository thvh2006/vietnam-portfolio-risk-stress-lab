"""Fetch a versioned public-market snapshot for the FUESSV30 risk case."""

from __future__ import annotations

import argparse
import csv
import json
import time
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path


STOCK_ENDPOINT = "https://api-finfo.vndirect.com.vn/v4/stock_prices"
INDEX_ENDPOINT = "https://api-finfo.vndirect.com.vn/v4/vnmarket_prices"
USER_AGENT = "Mozilla/5.0 portfolio-risk-research/1.0"


def read_tickers(path: Path) -> list[str]:
    with path.open(newline="", encoding="utf-8") as handle:
        tickers = [row["ticker"] for row in csv.DictReader(handle)]
    return [ticker for ticker in tickers if ticker != "CASH"]


def fetch_json(endpoint: str, query: dict[str, str | int], attempts: int = 4) -> dict:
    url = endpoint + "?" + urllib.parse.urlencode(query)
    request = urllib.request.Request(
        url,
        headers={"Accept": "application/json", "User-Agent": USER_AGENT},
    )
    error: Exception | None = None
    for attempt in range(attempts):
        try:
            with urllib.request.urlopen(request, timeout=45) as response:
                return json.load(response)
        except Exception as exc:
            error = exc
            time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"Unable to fetch {url}: {error}")


def fetch_stock(ticker: str, start: str, end: str) -> tuple[str, list[dict]]:
    payload = fetch_json(
        STOCK_ENDPOINT,
        {
            "sort": "date",
            "q": f"code:{ticker}~date:gte:{start}~date:lte:{end}",
            "size": 5000,
            "page": 1,
        },
    )
    return ticker, payload.get("data", [])


def write_stock_history(path: Path, rows: list[dict]) -> None:
    fields = [
        "date",
        "ticker",
        "close_vnd",
        "adjusted_close_vnd",
        "normal_volume",
        "normal_value_vnd",
        "provider_price_unit",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in sorted(rows, key=lambda item: (item["date"], item["code"])):
            writer.writerow(
                {
                    "date": row["date"],
                    "ticker": row["code"],
                    "close_vnd": round(float(row["close"]) * 1000, 4),
                    "adjusted_close_vnd": round(float(row["adClose"]) * 1000, 4),
                    "normal_volume": row.get("nmVolume", ""),
                    "normal_value_vnd": row.get("nmValue", ""),
                    "provider_price_unit": "VND_thousand_converted_to_VND",
                }
            )


def write_index_history(path: Path, rows: list[dict]) -> None:
    fields = ["date", "index_code", "close", "normal_volume", "normal_value_vnd"]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in sorted(rows, key=lambda item: item["date"]):
            writer.writerow(
                {
                    "date": row["date"],
                    "index_code": row["code"],
                    "close": row["close"],
                    "normal_volume": row.get("nmVolume", ""),
                    "normal_value_vnd": row.get("nmValue", ""),
                }
            )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", default="2019-01-02")
    parser.add_argument("--end", default="2026-09-30")
    parser.add_argument(
        "--holdings", default="data/sample/holdings_2026-09-30.csv"
    )
    parser.add_argument("--output-dir", default="data/market")
    args = parser.parse_args()

    output = Path(args.output_dir)
    output.mkdir(parents=True, exist_ok=True)
    tickers = read_tickers(Path(args.holdings))

    stock_rows: list[dict] = []
    coverage: dict[str, dict[str, str | int | None]] = {}
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {
            executor.submit(fetch_stock, ticker, args.start, args.end): ticker
            for ticker in tickers
        }
        for future in as_completed(futures):
            ticker, rows = future.result()
            stock_rows.extend(rows)
            dates = sorted(row["date"] for row in rows)
            coverage[ticker] = {
                "rows": len(rows),
                "first_date": dates[0] if dates else None,
                "last_date": dates[-1] if dates else None,
            }

    benchmark = fetch_json(
        INDEX_ENDPOINT,
        {
            "sort": "date",
            "q": f"code:VN30~date:gte:{args.start}~date:lte:{args.end}",
            "size": 5000,
            "page": 1,
        },
    ).get("data", [])

    write_stock_history(output / "constituent_prices.csv", stock_rows)
    write_index_history(output / "vn30_index.csv", benchmark)
    metadata = {
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "start_date": args.start,
        "end_date": args.end,
        "stock_endpoint": STOCK_ENDPOINT,
        "index_endpoint": INDEX_ENDPOINT,
        "stock_rows": len(stock_rows),
        "benchmark_rows": len(benchmark),
        "coverage": dict(sorted(coverage.items())),
    }
    (output / "snapshot_metadata.json").write_text(
        json.dumps(metadata, indent=2), encoding="utf-8"
    )
    print(json.dumps(metadata, indent=2))


if __name__ == "__main__":
    main()
