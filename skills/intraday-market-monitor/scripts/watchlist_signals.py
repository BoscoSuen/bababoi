"""Hourly-close confirmed signals for a small watchlist.

All signals are evaluated on the **last closed clock-hour bar**, never on the
live/partial bucket, so a 15-minute delayed feed changes nothing about their
meaning: at 11:20 the 10:00-11:00 bar is judged, at 12:20 the 11:00-12:00 bar.
"""

from __future__ import annotations

import glob
import json
from datetime import datetime, timedelta
from pathlib import Path

import _repo_bootstrap  # noqa: F401
import yaml

from scripts.market_data.timeutil import cumulative_vwap, hourly_bars, parse_ts_et

FIRST_HOUR = timedelta(minutes=60)


def _watchlist_entries(path: Path | None) -> list[dict]:
    """Rows of ``state/daily_watchlist.json`` (written by scripts/send_swing_signal.py):
    the screener-derived ``symbols`` list followed by the hand-kept ``manual`` list.
    Each row is normalised to ``{"symbol", "pivot", "stop"}``. YAML input (the old
    ``watchlist.yaml`` shape) still parses because JSON is a YAML subset."""
    if not path or not Path(path).is_file():
        return []
    try:
        data = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    except yaml.YAMLError:
        return []
    if isinstance(data, dict):
        raw = list(data.get("symbols") or []) + list(data.get("manual") or [])
    else:
        raw = data
    out: list[dict] = []
    for item in raw or []:
        if isinstance(item, dict):
            sym, pivot, stop = item.get("symbol"), item.get("pivot"), item.get("stop")
        else:
            sym, pivot, stop = item, None, None
        if sym:
            out.append(
                {
                    "symbol": str(sym).strip().upper(),
                    "pivot": float(pivot) if pivot is not None else None,
                    "stop": float(stop) if stop is not None else None,
                }
            )
    return out


def load_watchlist(
    path: Path | None, *, vcp_json: Path | None = None, vcp_min_rating: str = "B"
) -> list[str]:
    symbols = [e["symbol"] for e in _watchlist_entries(path)]
    if vcp_json:
        symbols.extend(vcp_symbols(vcp_json, min_rating=vcp_min_rating))
    seen: set[str] = set()
    out = []
    for s in symbols:
        if s not in seen:
            seen.add(s)
            out.append(s)
    return out


def load_watchlist_levels(path: Path | None) -> dict[str, dict]:
    """``{symbol: {"pivot", "stop"}}``; the first row naming a symbol wins."""
    levels: dict[str, dict] = {}
    for e in _watchlist_entries(path):
        levels.setdefault(e["symbol"], {"pivot": e["pivot"], "stop": e["stop"]})
    return levels


def latest_vcp_json(reports_dir: Path) -> Path | None:
    files = sorted(glob.glob(str(Path(reports_dir) / "vcp_screener_*.json")))
    return Path(files[-1]) if files else None


def vcp_symbols(path: Path, *, min_rating: str = "B") -> list[str]:
    order = {"A": 0, "B": 1, "C": 2, "D": 3}
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    rows = data.get("results") if isinstance(data, dict) else data
    out = []
    for row in rows or []:
        sym = row.get("symbol")
        rating = str(row.get("rating") or "").upper()[:1]
        if sym and rating in order and order[rating] <= order.get(min_rating.upper(), 1):
            out.append(str(sym).upper())
    return out


def evaluate_symbol(
    symbol: str,
    bars5: list[dict],
    *,
    prev_day: dict | None,
    avg_volume: float | None,
    elapsed: float,
    session_open: datetime,
    session_close: datetime,
    rel_vol_breakout_min: float = 1.2,
    gap_min_pct: float = 2.0,
    pivot: float | None = None,
    stop: float | None = None,
) -> dict:
    if not bars5:
        return {"symbol": symbol, "available": False, "signals": [], "pivot": pivot, "stop": stop}
    hours = hourly_bars(bars5, session_close=session_close)
    closed = [h for h in hours if h["closed"]]
    vwaps = cumulative_vwap(bars5)
    first_hour_end = session_open + FIRST_HOUR
    fh_bars = [b for b in bars5 if parse_ts_et(b["ts_et"]) < first_hour_end]
    fh_complete = (
        bool(fh_bars) and parse_ts_et(fh_bars[-1]["ts_et"]) + timedelta(minutes=5) >= first_hour_end
    )
    fhr_high = max(b["h"] for b in fh_bars) if fh_bars else None
    fhr_low = min(b["l"] for b in fh_bars) if fh_bars else None
    prev_c = (prev_day or {}).get("c")
    prev_h = (prev_day or {}).get("h")
    day_open = bars5[0]["o"]
    gap_pct = round((day_open / prev_c - 1) * 100, 3) if prev_c else None
    day_vol = sum(b["v"] for b in bars5)
    rel_vol = round(day_vol / (avg_volume * elapsed), 3) if avg_volume and elapsed > 0 else None

    signals: list[str] = []
    last_hour = closed[-1] if closed else None
    if last_hour:
        # VWAP through the end of the last closed hour bar.
        idx = max(i for i, b in enumerate(bars5) if b["ts_et"] < last_hour["end_et"])
        vwap_at_close = vwaps[idx]
        hc = last_hour["c"]
        prev_hour = closed[-2] if len(closed) > 1 else None
        if fh_complete and len(closed) >= 2 and fhr_high is not None:
            if hc > fhr_high and (rel_vol or 0) >= rel_vol_breakout_min:
                signals.append("FHR_BREAKOUT")
            elif hc < fhr_low:
                signals.append("FHR_BREAKDOWN")
        if gap_pct is not None and gap_pct >= gap_min_pct:
            if prev_h and hc > prev_h:
                signals.append("GAP_HOLD")
            elif hc < day_open:
                signals.append("GAP_FAIL")
        if prev_hour is not None:
            prev_idx = max(i for i, b in enumerate(bars5) if b["ts_et"] < prev_hour["end_et"])
            prev_vwap = vwaps[prev_idx]
            if prev_hour["c"] < prev_vwap and hc >= vwap_at_close:
                signals.append("VWAP_RECLAIM")
            elif prev_hour["c"] > prev_vwap and hc <= vwap_at_close:
                signals.append("VWAP_LOSS")
    else:
        vwap_at_close = vwaps[-1]
    # Level signals are judged on the latest *confirmed* 5-minute close, not the
    # hourly bar: a pivot break or stop hit is the reason this symbol is on the list,
    # and a half-hourly slot should report it as soon as the feed confirms it.
    last_close = bars5[-1]["c"]
    if pivot is not None and last_close > pivot and (rel_vol or 0) >= rel_vol_breakout_min:
        signals.append("PIVOT_BREAK")
    if stop is not None and last_close < stop:
        signals.append("STOP_HIT")
    return {
        "symbol": symbol,
        "available": True,
        "last_ts_et": bars5[-1]["ts_et"],
        "last": bars5[-1]["c"],
        "hourly_close": last_hour["c"] if last_hour else None,
        "hourly_bar_end_et": last_hour["end_et"] if last_hour else None,
        "vwap": round(vwap_at_close, 4),
        "above_vwap": bars5[-1]["c"] > vwaps[-1],
        "first_hour_complete": fh_complete,
        "fhr_high": fhr_high,
        "fhr_low": fhr_low,
        "gap_pct": gap_pct,
        "rel_vol": rel_vol,
        "pivot": pivot,
        "stop": stop,
        "signals": signals,
    }
