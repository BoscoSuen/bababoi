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


def load_watchlist(
    path: Path | None, *, vcp_json: Path | None = None, vcp_min_rating: str = "B"
) -> list[str]:
    symbols: list[str] = []
    if path and Path(path).is_file():
        data = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
        raw = data.get("symbols") if isinstance(data, dict) else data
        for item in raw or []:
            sym = item.get("symbol") if isinstance(item, dict) else item
            if sym:
                symbols.append(str(sym).strip().upper())
    if vcp_json:
        symbols.extend(vcp_symbols(vcp_json, min_rating=vcp_min_rating))
    seen: set[str] = set()
    out = []
    for s in symbols:
        if s not in seen:
            seen.add(s)
            out.append(s)
    return out


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
) -> dict:
    if not bars5:
        return {"symbol": symbol, "available": False, "signals": []}
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
        "signals": signals,
    }
