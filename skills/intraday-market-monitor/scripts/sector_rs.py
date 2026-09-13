"""Index state and sector relative strength from 5-minute RTH bars."""

from __future__ import annotations

from datetime import datetime

import _repo_bootstrap  # noqa: F401

from scripts.market_data.timeutil import cumulative_vwap, hourly_bars


def _pct(a: float, b: float) -> float | None:
    if not b:
        return None
    return round((a / b - 1) * 100, 3)


def index_state(
    bars5: list[dict], prev_day: dict | None, *, session_close: datetime | None = None
) -> dict:
    """SPY/QQQ-style state on the latest *confirmed* 5-minute bar."""
    if not bars5:
        return {"available": False}
    vwap = cumulative_vwap(bars5)[-1]
    last = bars5[-1]
    open_ = bars5[0]["o"]
    prev_h = (prev_day or {}).get("h")
    prev_l = (prev_day or {}).get("l")
    prev_c = (prev_day or {}).get("c")
    hours = hourly_bars(bars5, session_close=session_close)
    closed = [h for h in hours if h["closed"]]
    last_hour = closed[-1] if closed else None
    return {
        "available": True,
        "last_ts_et": last["ts_et"],
        "last": last["c"],
        "open": open_,
        "vwap": round(vwap, 4),
        "above_vwap": last["c"] > vwap,
        "ret_open_pct": _pct(last["c"], open_),
        "ret_prev_close_pct": _pct(last["c"], prev_c) if prev_c else None,
        "gap_pct": _pct(open_, prev_c) if prev_c else None,
        "above_prev_high": bool(prev_h and last["c"] > prev_h),
        "below_prev_low": bool(prev_l and last["c"] < prev_l),
        "session_high": max(b["h"] for b in bars5),
        "session_low": min(b["l"] for b in bars5),
        "last_hour": (
            {
                "ts_et": last_hour["ts_et"],
                "end_et": last_hour["end_et"],
                "ret_pct": _pct(last_hour["c"], last_hour["o"]),
                "close": last_hour["c"],
            }
            if last_hour
            else None
        ),
    }


def compute_sector_rs(
    bars_by_symbol: dict[str, list[dict]],
    *,
    benchmark: str = "SPY",
    risk_on: list[str],
    risk_off: list[str],
    session_close: datetime | None = None,
) -> dict:
    """Relative strength vs the benchmark since the open and over the last closed hour."""
    bench = bars_by_symbol.get(benchmark) or []
    if not bench:
        return {"available": False, "benchmark": benchmark, "sectors": []}
    bench_ret = _pct(bench[-1]["c"], bench[0]["o"]) or 0.0
    bench_hours = [h for h in hourly_bars(bench, session_close=session_close) if h["closed"]]
    bench_hour_ret = _pct(bench_hours[-1]["c"], bench_hours[-1]["o"]) if bench_hours else None
    rows = []
    for sym, bars in bars_by_symbol.items():
        if sym == benchmark or not bars:
            continue
        ret = _pct(bars[-1]["c"], bars[0]["o"])
        hours = [h for h in hourly_bars(bars, session_close=session_close) if h["closed"]]
        hour_ret = _pct(hours[-1]["c"], hours[-1]["o"]) if hours else None
        rows.append(
            {
                "symbol": sym,
                "ret_open_pct": ret,
                "rs_open_pct": round(ret - bench_ret, 3) if ret is not None else None,
                "rs_last_hour_pct": (
                    round(hour_ret - bench_hour_ret, 3)
                    if hour_ret is not None and bench_hour_ret is not None
                    else None
                ),
                "above_vwap": bars[-1]["c"] > cumulative_vwap(bars)[-1],
            }
        )
    rows.sort(key=lambda r: (r["rs_open_pct"] is None, -(r["rs_open_pct"] or 0)))
    for i, r in enumerate(rows, 1):
        r["rank"] = i
    by = {r["symbol"]: r for r in rows}

    def _mean(symbols: list[str]) -> float | None:
        vals = [
            by[s]["rs_open_pct"] for s in symbols if s in by and by[s]["rs_open_pct"] is not None
        ]
        return round(sum(vals) / len(vals), 3) if vals else None

    on, off = _mean(risk_on), _mean(risk_off)
    return {
        "available": True,
        "benchmark": benchmark,
        "benchmark_ret_open_pct": bench_ret,
        "benchmark_last_hour_ret_pct": bench_hour_ret,
        "sectors": rows,
        "risk_on_rs_pct": on,
        "risk_off_rs_pct": off,
        "risk_on_spread_pct": round(on - off, 3) if on is not None and off is not None else None,
    }
