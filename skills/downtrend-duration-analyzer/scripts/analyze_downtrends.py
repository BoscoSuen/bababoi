#!/usr/bin/env python3
"""
Downtrend Duration Analyzer

Analyzes historical price data to identify downtrend periods (peak-to-trough)
and computes duration statistics segmented by sector and market cap.

Data sources:
- Stock universe: finvizfinance (sector screening)
- Price history: Polygon via PolygonCompatClient
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.market_data.legacy import PolygonCompatClient

MARKET_CAP_TIERS = {
    "Mega": 200_000_000_000,
    "Large": 10_000_000_000,
    "Mid": 2_000_000_000,
    "Small": 0,
}

DEFAULT_SECTORS = [
    "Technology",
    "Healthcare",
    "Financial",
    "Consumer Cyclical",
    "Consumer Defensive",
    "Industrials",
    "Energy",
    "Basic Materials",
    "Utilities",
    "Real Estate",
    "Communication Services",
]

FINVIZ_SECTOR_MAP = {
    "Financial Services": "Financial",
}


def get_market_cap_tier(market_cap: float | None) -> str:
    if market_cap is None:
        return "Unknown"
    if market_cap >= MARKET_CAP_TIERS["Mega"]:
        return "Mega"
    elif market_cap >= MARKET_CAP_TIERS["Large"]:
        return "Large"
    elif market_cap >= MARKET_CAP_TIERS["Mid"]:
        return "Mid"
    else:
        return "Small"


def fetch_stock_list_finviz(sector: str | None = None) -> list[dict]:
    """Fetch liquid stocks from finviz, optionally filtered by sector."""
    from finvizfinance.screener.overview import Overview

    foverview = Overview()
    filters: dict[str, str] = {
        "Price": "Over $20",
        "Average Volume": "Over 2M",
        "Industry": "Stocks only (ex-Funds)",
    }
    if sector:
        finviz_sector = FINVIZ_SECTOR_MAP.get(sector, sector)
        filters["Sector"] = finviz_sector

    foverview.set_filter(filters_dict=filters)
    df = foverview.screener_view()

    stocks = []
    if df is not None and not df.empty:
        for _, row in df.iterrows():
            market_cap_raw = row.get("Market Cap")
            market_cap = None
            if market_cap_raw is not None:
                try:
                    market_cap = float(market_cap_raw)
                except (TypeError, ValueError):
                    pass
            stocks.append(
                {
                    "symbol": str(row.get("Ticker", "")),
                    "sector": str(row.get("Sector", sector or "Unknown")),
                    "marketCap": market_cap,
                }
            )
    return stocks


def fetch_historical_prices(
    client: PolygonCompatClient, symbol: str, days: int
) -> pd.DataFrame:
    """Fetch historical daily prices for a symbol via Polygon."""
    data = client.get_historical_prices(symbol, days=days)
    if not data or not data.get("historical"):
        return pd.DataFrame()

    historical = data["historical"]
    df = pd.DataFrame(historical)
    if df.empty:
        return df

    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").reset_index(drop=True)
    return df[["date", "open", "high", "low", "close", "volume"]]


def detect_peaks_troughs(
    prices: pd.DataFrame, peak_window: int = 20, trough_window: int = 20
) -> tuple[list[int], list[int]]:
    closes = prices["close"].values
    n = len(closes)
    peaks = []
    troughs = []

    for i in range(peak_window, n - peak_window):
        window_start = i - peak_window
        window_end = i + peak_window + 1
        window = closes[window_start:window_end]

        if closes[i] == np.max(window):
            peaks.append(i)

        if closes[i] == np.min(window):
            troughs.append(i)

    return peaks, troughs


def find_downtrends(
    prices: pd.DataFrame,
    peaks: list[int],
    troughs: list[int],
    min_depth_pct: float = 5.0,
    min_duration_days: int = 3,
) -> list[dict]:
    downtrends = []
    closes = prices["close"].values
    dates = prices["date"].values

    for peak_idx in peaks:
        peak_price = closes[peak_idx]
        peak_date = dates[peak_idx]

        subsequent_troughs = [t for t in troughs if t > peak_idx]
        if not subsequent_troughs:
            continue

        next_peaks = [p for p in peaks if p > peak_idx]
        end_idx = next_peaks[0] if next_peaks else len(closes)

        valid_troughs = [t for t in subsequent_troughs if t < end_idx]
        if not valid_troughs:
            continue

        trough_idx = min(valid_troughs, key=lambda t: closes[t])
        trough_price = closes[trough_idx]
        trough_date = dates[trough_idx]

        depth_pct = ((trough_price - peak_price) / peak_price) * 100
        duration_days = int(trough_idx - peak_idx)

        if abs(depth_pct) < min_depth_pct:
            continue
        if duration_days < min_duration_days:
            continue

        downtrends.append(
            {
                "peak_idx": peak_idx,
                "trough_idx": trough_idx,
                "peak_date": pd.Timestamp(peak_date).strftime("%Y-%m-%d"),
                "trough_date": pd.Timestamp(trough_date).strftime("%Y-%m-%d"),
                "peak_price": float(peak_price),
                "trough_price": float(trough_price),
                "duration_days": duration_days,
                "depth_pct": round(depth_pct, 2),
            }
        )

    return downtrends


def analyze_symbol(
    client: PolygonCompatClient,
    symbol: str,
    sector: str,
    market_cap: float | None,
    days: int,
    peak_window: int,
    trough_window: int,
    min_depth_pct: float,
) -> list[dict]:
    prices = fetch_historical_prices(client, symbol, days)

    if prices.empty or len(prices) < peak_window * 2 + 1:
        return []

    peaks, troughs = detect_peaks_troughs(prices, peak_window, trough_window)

    if not peaks or not troughs:
        return []

    downtrends = find_downtrends(prices, peaks, troughs, min_depth_pct)

    market_cap_tier = get_market_cap_tier(market_cap)

    for dt in downtrends:
        dt["symbol"] = symbol
        dt["sector"] = sector
        dt["market_cap_tier"] = market_cap_tier

    return downtrends


def compute_statistics(downtrends: list[dict]) -> dict[str, Any]:
    if not downtrends:
        return {
            "total_downtrends": 0,
            "median_duration_days": 0,
            "mean_duration_days": 0,
            "p25_duration_days": 0,
            "p75_duration_days": 0,
            "p90_duration_days": 0,
        }

    durations = [dt["duration_days"] for dt in downtrends]
    return {
        "total_downtrends": len(downtrends),
        "median_duration_days": int(np.median(durations)),
        "mean_duration_days": round(np.mean(durations), 1),
        "p25_duration_days": int(np.percentile(durations, 25)),
        "p75_duration_days": int(np.percentile(durations, 75)),
        "p90_duration_days": int(np.percentile(durations, 90)),
    }


def group_statistics(downtrends: list[dict], group_key: str) -> dict[str, dict[str, Any]]:
    groups: dict[str, list[dict]] = {}

    for dt in downtrends:
        key = dt.get(group_key, "Unknown")
        if key not in groups:
            groups[key] = []
        groups[key].append(dt)

    result = {}
    for key, group_downtrends in groups.items():
        durations = [dt["duration_days"] for dt in group_downtrends]
        result[key] = {
            "count": len(group_downtrends),
            "median_days": int(np.median(durations)),
            "mean_days": round(np.mean(durations), 1),
        }

    return result


def generate_markdown_report(analysis_result: dict[str, Any], output_path: Path) -> None:
    params = analysis_result["parameters"]
    summary = analysis_result["summary"]
    by_sector = analysis_result.get("by_sector", {})
    by_market_cap = analysis_result.get("by_market_cap", {})

    lines = [
        "# Downtrend Duration Analysis",
        "",
        f"**Date**: {analysis_result['analysis_date'][:10]}",
        f"**Lookback**: {params['lookback_years']} years",
    ]

    if params.get("sector_filter"):
        lines.append(f"**Sector**: {params['sector_filter']}")

    lines.extend(
        [
            "",
            "## Summary Statistics",
            "",
            "| Metric | Value |",
            "|--------|-------|",
            f"| Total Downtrends | {summary['total_downtrends']:,} |",
            f"| Median Duration | {summary['median_duration_days']} days |",
            f"| Mean Duration | {summary['mean_duration_days']} days |",
            f"| 25th Percentile | {summary['p25_duration_days']} days |",
            f"| 75th Percentile | {summary['p75_duration_days']} days |",
            f"| 90th Percentile | {summary['p90_duration_days']} days |",
            "",
        ]
    )

    if by_market_cap:
        lines.extend(
            [
                "## By Market Cap Tier",
                "",
                "| Tier | Count | Median | Mean |",
                "|------|-------|--------|------|",
            ]
        )
        tier_order = ["Mega", "Large", "Mid", "Small"]
        for tier in tier_order:
            if tier in by_market_cap:
                stats = by_market_cap[tier]
                lines.append(
                    f"| {tier} | {stats['count']} | {stats['median_days']} days | {stats['mean_days']} days |"
                )
        lines.append("")

    if by_sector:
        lines.extend(
            [
                "## By Sector",
                "",
                "| Sector | Count | Median | Mean |",
                "|--------|-------|--------|------|",
            ]
        )
        for sector, stats in sorted(by_sector.items(), key=lambda x: x[1]["median_days"]):
            lines.append(
                f"| {sector} | {stats['count']} | {stats['median_days']} days | {stats['mean_days']} days |"
            )
        lines.append("")

    lines.extend(
        [
            "## Key Insights",
            "",
            "1. **Percentile Guidance**: Use P50 (median) for typical expectations; P75-P90 for conservative planning",
            "2. **Market Cap Effect**: Larger companies typically recover faster from corrections",
            "3. **Sector Variation**: Defensive sectors show shorter corrections than cyclical sectors",
            "",
        ]
    )

    output_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Analyze historical downtrend durations by sector and market cap"
    )
    parser.add_argument(
        "--sector",
        help="Filter to specific sector (e.g., 'Technology')",
    )
    parser.add_argument(
        "--lookback-years",
        type=int,
        default=5,
        help="Years of historical data to analyze (default: 5)",
    )
    parser.add_argument(
        "--peak-window",
        type=int,
        default=20,
        help="Rolling window size for peak detection (default: 20)",
    )
    parser.add_argument(
        "--trough-window",
        type=int,
        default=20,
        help="Rolling window size for trough detection (default: 20)",
    )
    parser.add_argument(
        "--min-depth",
        type=float,
        default=5.0,
        help="Minimum depth percentage for a downtrend (default: 5.0)",
    )
    parser.add_argument(
        "--max-stocks",
        type=int,
        default=100,
        help="Maximum stocks to analyze (default: 100)",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="reports",
        help="Output directory for reports (default: reports)",
    )

    args = parser.parse_args()

    days = 365 * args.lookback_years + 60
    print(f"Analyzing downtrends over {args.lookback_years} years")

    print("Fetching stock universe from finviz...")
    stocks = fetch_stock_list_finviz(args.sector)
    if not stocks:
        print("No stocks found matching criteria", file=sys.stderr)
        sys.exit(1)

    stocks = stocks[: args.max_stocks]
    print(f"Analyzing {len(stocks)} stocks...")

    client = PolygonCompatClient()

    all_downtrends: list[dict] = []
    for i, stock in enumerate(stocks):
        symbol = stock.get("symbol", "")
        sector = stock.get("sector", "Unknown")
        market_cap = stock.get("marketCap")

        if i % 10 == 0:
            print(f"  Progress: {i}/{len(stocks)} stocks processed")

        downtrends = analyze_symbol(
            client,
            symbol,
            sector,
            market_cap,
            days,
            args.peak_window,
            args.trough_window,
            args.min_depth,
        )
        all_downtrends.extend(downtrends)

    print(f"Found {len(all_downtrends)} downtrend periods")

    summary = compute_statistics(all_downtrends)
    by_sector = group_statistics(all_downtrends, "sector")
    by_market_cap = group_statistics(all_downtrends, "market_cap_tier")

    result = {
        "schema_version": "1.0",
        "analysis_date": datetime.now().isoformat() + "Z",
        "parameters": {
            "lookback_years": args.lookback_years,
            "sector_filter": args.sector,
            "peak_window": args.peak_window,
            "trough_window": args.trough_window,
            "min_depth_pct": args.min_depth,
        },
        "summary": summary,
        "by_sector": by_sector,
        "by_market_cap": by_market_cap,
        "downtrends": all_downtrends,
    }

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")

    json_path = output_dir / f"downtrend_analysis_{timestamp}.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    print(f"JSON report saved to: {json_path}")

    md_path = output_dir / f"downtrend_analysis_{timestamp}.md"
    generate_markdown_report(result, md_path)
    print(f"Markdown report saved to: {md_path}")


if __name__ == "__main__":
    main()
