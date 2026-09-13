"""Intraday breadth from one all-tickers snapshot.

Inputs are normalized SnapshotRows (``scripts/market_data/provider.py``):
``{"symbol", "day": {o,h,l,c,v,vw}, "prev_day": {...}, "change_pct", ...}``.
"""

from __future__ import annotations

import re
from datetime import datetime


def filter_universe(
    rows: list[dict],
    *,
    symbol_regex: str = r"^[A-Z]{1,5}$",
    min_prev_close: float = 5.0,
    min_prev_volume: int = 100_000,
) -> list[dict]:
    pattern = re.compile(symbol_regex)
    out = []
    for r in rows:
        sym = r.get("symbol") or ""
        day, prev = r.get("day"), r.get("prev_day")
        if not pattern.match(sym) or not day or not prev:
            continue
        if not day.get("c") or not prev.get("c"):
            continue
        if prev["c"] < min_prev_close or prev["v"] < min_prev_volume:
            continue
        out.append(r)
    return out


def elapsed_fraction(
    until_et: datetime,
    session_open: datetime,
    session_close: datetime,
    curve: list[list[float]],
) -> float:
    """Share of a normal session's volume expected by ``until_et`` (piecewise-linear
    on ``curve`` = [[minutes_since_open, cumulative_fraction], ...])."""
    total = (session_close - session_open).total_seconds() / 60.0
    minutes = max(0.0, min((until_et - session_open).total_seconds() / 60.0, total))
    # Rescale the curve's x-axis to this session's length (early closes).
    scale = total / curve[-1][0] if curve and curve[-1][0] else 1.0
    pts = [(x * scale, y) for x, y in curve]
    if minutes <= pts[0][0]:
        return max(pts[0][1], 0.0)
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        if minutes <= x1:
            if x1 == x0:
                return y1
            return y0 + (y1 - y0) * (minutes - x0) / (x1 - x0)
    return pts[-1][1]


def avg_volume_by_symbol(grouped_days: list[dict[str, dict]]) -> dict[str, float]:
    """Mean daily volume per symbol across ``grouped_daily`` results."""
    sums: dict[str, float] = {}
    counts: dict[str, int] = {}
    for day in grouped_days:
        for sym, bar in day.items():
            sums[sym] = sums.get(sym, 0.0) + float(bar.get("volume") or 0)
            counts[sym] = counts.get(sym, 0) + 1
    return {sym: sums[sym] / counts[sym] for sym in sums if counts[sym]}


def compute_breadth(
    rows: list[dict],
    *,
    avg_volume: dict[str, float] | None,
    elapsed: float,
) -> dict:
    """Breadth statistics over an already-filtered universe."""
    n = len(rows)
    if n == 0:
        return {"universe_size": 0, "available": False}
    adv = dec = above_vwap = above_prev_high = below_prev_low = 0
    up_vol = down_vol = 0.0
    day_vol_total = 0.0
    avg_total = 0.0
    with_avg = 0
    for r in rows:
        day, prev = r["day"], r["prev_day"]
        chg = r.get("change_pct")
        if chg is None:
            chg = (day["c"] / prev["c"] - 1) * 100 if prev["c"] else 0.0
        if chg > 0:
            adv += 1
            up_vol += day["v"]
        elif chg < 0:
            dec += 1
            down_vol += day["v"]
        if day.get("vw") and day["c"] > day["vw"]:
            above_vwap += 1
        if day["c"] > prev["h"]:
            above_prev_high += 1
        if day["c"] < prev["l"]:
            below_prev_low += 1
        day_vol_total += day["v"]
        if avg_volume and r["symbol"] in avg_volume and avg_volume[r["symbol"]] > 0:
            avg_total += avg_volume[r["symbol"]]
            with_avg += 1
    pace = None
    if avg_total > 0 and elapsed > 0:
        pace = round(day_vol_total / (avg_total * elapsed), 3)
    return {
        "available": True,
        "universe_size": n,
        "advancers": adv,
        "decliners": dec,
        "pct_advancers": round(adv / n * 100, 1),
        "pct_decliners": round(dec / n * 100, 1),
        "pct_above_vwap": round(above_vwap / n * 100, 1),
        "pct_above_prev_high": round(above_prev_high / n * 100, 1),
        "pct_below_prev_low": round(below_prev_low / n * 100, 1),
        "up_volume": int(up_vol),
        "down_volume": int(down_vol),
        "ud_ratio": round(up_vol / down_vol, 3) if down_vol > 0 else None,
        "volume_pace": pace,
        "elapsed_fraction": round(elapsed, 3),
        "avg_volume_coverage": round(with_avg / n, 3),
    }
