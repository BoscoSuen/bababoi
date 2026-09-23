"""Intraday finviz scans (public screener via finvizfinance, no key) used as the
momentum-burst candidate source for signal_engine.

Two scans, mirroring calpico's market-scan daemon:
  bullish_flow    stocks only, avg vol > 2M, ATR > 1.5, day +1%, from open +2%,
                  month up, week up, above SMA50
  close_stronger  stocks only, avg vol > 2M, price > $20, from open +2%,
                  month up, above SMA20/50/200

Rows carry Sector / Industry, which the engine needs for relative strength and
theme counts. Results are cached per slot under ``state/intraday/<date>/`` so a
finviz hiccup falls back to the latest scan of the day instead of an empty list.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

SCANS: dict[str, dict] = {
    "bullish_flow": {
        "Industry": "Stocks only (ex-Funds)",
        "Average Volume": "Over 2M",
        "Average True Range": "Over 1.5",
        "Change": "Up 1%",
        "Change from Open": "Up 2%",
        "Performance": "Month Up",
        "Performance 2": "Week Up",
        "50-Day Simple Moving Average": "Price above SMA50",
    },
    "close_stronger": {
        "Industry": "Stocks only (ex-Funds)",
        "Average Volume": "Over 2M",
        "Price": "Over $20",
        "Change from Open": "Up 2%",
        "Performance": "Month Up",
        "20-Day Simple Moving Average": "Price above SMA20",
        "50-Day Simple Moving Average": "Price above SMA50",
        "200-Day Simple Moving Average": "Price above SMA200",
    },
}


def _rows(df) -> list[dict]:
    out = []
    for _, r in df.iterrows():
        sym = str(r.get("Ticker") or "").strip().upper()
        if not sym:
            continue
        chg = r.get("Change %", r.get("Change"))
        try:
            chg = float(str(chg).rstrip("%")) if chg is not None else None
        except ValueError:
            chg = None
        out.append(
            {
                "symbol": sym,
                "sector": r.get("Sector"),
                "industry": r.get("Industry"),
                "price": float(r["Price"]) if r.get("Price") is not None else None,
                "change_pct": chg,
                "volume": float(r["Volume"]) if r.get("Volume") is not None else None,
            }
        )
    return out


def run_scans(*, pause: float = 1.5, verbose: int = 0) -> tuple[list[dict], list[str]]:
    """Union of both scans (first occurrence wins) plus a list of scan names that failed."""
    from finvizfinance.screener.overview import Overview

    rows: dict[str, dict] = {}
    failed: list[str] = []
    for name, filters in SCANS.items():
        try:
            o = Overview()
            o.set_filter(filters_dict=filters)
            df = o.screener_view(order="Change", ascend=False, verbose=verbose)
            for r in _rows(df):
                r.setdefault("scans", [])
                rows.setdefault(r["symbol"], r)["scans"].append(name) if "scans" in rows.get(r["symbol"], {}) else rows.setdefault(r["symbol"], {**r, "scans": [name]})
        except Exception as exc:  # network / layout change — never abort the slot
            failed.append(f"{name}: {exc}")
        time.sleep(pause)
    return list(rows.values()), failed


def scan_path(state_dir: Path, session_date: str, slot: str) -> Path:
    return Path(state_dir) / session_date / f"scan_{slot}.json"


def load_or_run(state_dir: Path, session_date: str, slot: str) -> tuple[list[dict], list[str]]:
    """Run the scans for this slot and cache them; on total failure reuse the newest
    scan cached earlier today."""
    rows, failed = run_scans()
    path = scan_path(state_dir, session_date, slot)
    if rows:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({"slot": slot, "rows": rows, "failed": failed}, indent=1), encoding="utf-8")
        return rows, failed
    older = sorted(path.parent.glob("scan_*.json")) if path.parent.is_dir() else []
    if older:
        data = json.loads(older[-1].read_text(encoding="utf-8"))
        return data.get("rows") or [], failed + [f"reused {older[-1].name}"]
    return [], failed


def lookup_sectors(symbols: list[str], cache_file: Path, *, pause: float = 1.5) -> dict[str, dict]:
    """Sector / industry for arbitrary symbols (watchlist names) via finviz's ticker
    filter, cached on disk across sessions."""
    cache: dict[str, dict] = {}
    if cache_file.is_file():
        try:
            cache = json.loads(cache_file.read_text(encoding="utf-8"))
        except ValueError:
            cache = {}
    missing = [s for s in symbols if s not in cache]
    if missing:
        try:
            from finvizfinance.screener.overview import Overview

            for i in range(0, len(missing), 100):
                batch = missing[i : i + 100]
                o = Overview()
                o.set_filter(ticker=",".join(batch))
                for r in _rows(o.screener_view(verbose=0)):
                    cache[r["symbol"]] = {"sector": r["sector"], "industry": r["industry"]}
                for s in batch:
                    cache.setdefault(s, {"sector": None, "industry": None})
                time.sleep(pause)
            cache_file.parent.mkdir(parents=True, exist_ok=True)
            cache_file.write_text(json.dumps(cache, indent=0), encoding="utf-8")
        except Exception:
            pass
    return {s: cache.get(s, {"sector": None, "industry": None}) for s in symbols}
