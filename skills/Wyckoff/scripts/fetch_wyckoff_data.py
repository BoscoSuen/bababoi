#!/usr/bin/env python3
"""Fetch auditable US equity daily OHLCV through the shared market-data layer.

Only dates strictly before the New York cutoff date are eligible, even after
the close. This intentionally conservative boundary avoids partial daily bars
without pretending that a fixed 16:00 clock is an exchange calendar.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from uuid import uuid4
from zoneinfo import ZoneInfo

ET = ZoneInfo("America/New_York")


def parse_as_of(value: str) -> datetime:
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if dt.tzinfo is None or dt.utcoffset() is None:
        raise ValueError("--as-of requires a timestamp with an explicit UTC offset")
    return dt.astimezone(ET)


def request_end(as_of: datetime) -> date:
    return as_of.astimezone(ET).date() - timedelta(days=1)


def prepare_bars(rows: list[dict], start: date, as_of: datetime) -> tuple[list[dict], list[str]]:
    """Filter before evaluating OHLCV; reject malformed in-range observations."""
    if not isinstance(rows, list):
        raise ValueError("Provider bars must be a list")
    end = request_end(as_of)
    seen = set()
    bars = []
    warnings = []
    for row in rows:
        if not isinstance(row, dict) or not isinstance(row.get("date"), str):
            raise ValueError("Each provider bar needs an ISO date")
        day = date.fromisoformat(row["date"])
        if not start <= day <= end:
            continue
        if day in seen:
            raise ValueError(f"duplicate daily bar: {day}")
        seen.add(day)
        clean = {"date": day.isoformat()}
        for field in ("open", "high", "low", "close", "volume"):
            value = row.get(field)
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise ValueError(f"Invalid {field} on {day}: expected a finite number")
            if not math.isfinite(value):
                raise ValueError(f"Non-finite {field} on {day}")
            clean[field] = value
        if not (
            0 < clean["low"] <= clean["open"] <= clean["high"]
            and clean["low"] <= clean["close"] <= clean["high"]
        ):
            raise ValueError(f"Invalid equity OHLC geometry on {day}")
        if clean["volume"] < 0:
            raise ValueError(f"Negative volume on {day}")
        if clean["volume"] == 0:
            warnings.append(f"Zero volume on {day}; verify source before any volume interpretation")
        # Keep split-adjusted O/H/L/C on the same basis; do not substitute adjClose.
        bars.append(clean)
    if not bars:
        raise ValueError("No completed daily bars in the requested interval")
    bars.sort(key=lambda b: b["date"])
    return bars, warnings


def _load_shared_layer():
    override = os.environ.get("TRADING_SKILLS_REPO_ROOT")
    root = Path(override).expanduser().resolve() if override else Path(__file__).resolve().parents[3]
    if not (root / "scripts/market_data/__init__.py").is_file():
        raise RuntimeError(
            "Shared market-data layer not found. Run from this repository or set "
            "TRADING_SKILLS_REPO_ROOT to its checkout; the standalone skill package "
            "does not bundle scripts/market_data."
        )
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    from scripts.market_data import get_provider
    from scripts.market_data.http import redact
    from scripts.market_data.symbols import to_polygon

    return get_provider, redact, to_polygon


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--symbol", required=True, help="US stock/ETF ticker; no implicit index proxy")
    parser.add_argument("--start", required=True, help="Inclusive first date, YYYY-MM-DD")
    parser.add_argument("--as-of", required=True, help="Timezone-aware timestamp; its ET date is excluded")
    parser.add_argument("--provider", choices=("polygon", "fixture"), default="polygon")
    parser.add_argument("--fixture-dir", type=Path, help="Shared DiskCache-format replay directory")
    parser.add_argument("--output-dir", type=Path, default=Path("reports"))
    args = parser.parse_args(argv)
    symbol = args.symbol.strip().upper()
    if not re.fullmatch(r"[A-Z][A-Z0-9.-]{0,14}", symbol):
        parser.error("Use a US stock/ETF ticker (for example AAPL or SPY); index proxies are not automatic")
    try:
        start = date.fromisoformat(args.start)
        as_of = parse_as_of(args.as_of)
    except ValueError as exc:
        parser.error(str(exc))
    if as_of > datetime.now(timezone.utc):
        parser.error("--as-of cannot be in the future")
    if start > request_end(as_of):
        parser.error("--start must precede the New York --as-of date")
    if (args.provider == "fixture") != (args.fixture_dir is not None):
        parser.error("--fixture-dir is required for fixture and only valid with --provider fixture")
    key = os.environ.get("POLYGON_API_KEY")
    if args.provider == "polygon" and not key:
        print("Set POLYGON_API_KEY for Polygon, or use --provider fixture --fixture-dir DIR.", file=sys.stderr)
        return 2
    try:
        get_provider, redact, to_polygon = _load_shared_layer()
    except (ImportError, RuntimeError) as exc:
        print(f"Setup error: {exc}. See skills/Wyckoff/requirements.txt.", file=sys.stderr)
        return 2
    try:
        provider = get_provider(args.provider, api_key=key, fixture_dir=args.fixture_dir)
        rows = provider.daily_bars(symbol, start, request_end(as_of))
        bars, warnings = prepare_bars(rows, start, as_of)
        fetched_symbol, _ = to_polygon(symbol)
        warnings.extend([
            "Cutoff-date daily bar excluded, including after close; no intraday or weekly bars generated.",
            "Exchange-calendar coverage is not validated; inspect gaps and last_completed_bar for staleness.",
            "Historical split adjustments and provider revisions are not point-in-time snapshots.",
            "Shared provider rounds volume and maps absent raw volume to zero; verify zero-volume rows.",
        ])
        now = datetime.now(timezone.utc)
        bundle = {
            "schema_version": "1.0",
            "kind": "wyckoff_ohlcv_input",
            "generated_at": now.isoformat(),
            "as_of": as_of.isoformat(),
            "symbol": symbol,
            "fetched_symbol": fetched_symbol,
            "asset_scope": "US_equity_or_ETF",
            "timeframe": "1d",
            "timezone": "America/New_York",
            "currency": "USD",
            "source": {"provider": provider.name, "method": "scripts.market_data.daily_bars"},
            "requested_start": start.isoformat(),
            "requested_end": request_end(as_of).isoformat(),
            "history_start": bars[0]["date"],
            "last_completed_bar": bars[-1]["date"],
            "bar_count": len(bars),
            "adjustment": "split_adjusted_ohlc_not_dividend_adjusted",
            "volume_type": "provider_reported_share_volume",
            "point_in_time_snapshot": False,
            "warnings": warnings,
            "bars": bars,
        }
        content = json.dumps(bundle, indent=2, allow_nan=False) + "\n"
        args.output_dir.mkdir(parents=True, exist_ok=True)
        stamp = as_of.strftime("%Y%m%dT%H%M%S%z")
        path = args.output_dir / f"Wyckoff_ohlcv_{symbol}_{stamp}_{uuid4().hex[:12]}.json"
        with path.open("x", encoding="utf-8") as stream:
            stream.write(content)
        print(path)
        return 0
    except ImportError:
        print("Missing runtime dependency; install skills/Wyckoff/requirements.txt.", file=sys.stderr)
        return 2
    except Exception as exc:
        # Provider payloads/errors may contain credentials; never print an unredacted traceback.
        print(f"Data preparation failed: {redact(str(exc), key)}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
