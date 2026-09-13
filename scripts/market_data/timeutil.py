"""Time helpers: ET conversion, regular-session filtering, hourly aggregation.

Polygon aggregate timestamps are epoch milliseconds (UTC) at bar *open*.
Polygon's own clock-hour aggregates fold the 09:00-09:30 pre-market into the
09:00 bar, so hourly bars are always rebuilt here from 5-minute RTH bars.
"""

from __future__ import annotations

from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

ET = ZoneInfo("America/New_York")
UTC = ZoneInfo("UTC")
RTH_OPEN = time(9, 30)
RTH_CLOSE = time(16, 0)
BAR_5MIN = timedelta(minutes=5)


def ms_to_et(ms: int) -> datetime:
    return datetime.fromtimestamp(ms / 1000.0, tz=UTC).astimezone(ET)


def ns_to_et(ns: int) -> datetime:
    return datetime.fromtimestamp(ns / 1_000_000_000, tz=UTC).astimezone(ET)


def et_date(ms: int) -> date:
    return ms_to_et(ms).date()


def now_et() -> datetime:
    return datetime.now(tz=ET)


def floor5(dt: datetime) -> datetime:
    """Round *down* to the previous 5-minute boundary (keeps tzinfo)."""
    return dt.replace(minute=dt.minute - dt.minute % 5, second=0, microsecond=0)


def session_bounds(session_date: date) -> tuple[datetime, datetime] | None:
    """(open, close) for the XNYS regular session, or ``None`` on a non-session day.

    Uses the shared exchange calendar when ``pandas-market-calendars`` is
    installed; otherwise assumes weekdays 09:30-16:00 (no holidays / early
    closes) so offline paths keep working.
    """
    try:
        from scripts.market_calendar.market_calendar import (
            CalendarUnavailableError,
            session_for_date,
        )

        try:
            session = session_for_date("XNYS", session_date)
        except CalendarUnavailableError:
            session = None
            raise ImportError
        if session is None:
            return None
        return (
            session.market_open.astimezone(ET),
            session.market_close.astimezone(ET),
        )
    except ImportError:
        if session_date.weekday() >= 5:
            return None
        return (
            datetime.combine(session_date, RTH_OPEN, tzinfo=ET),
            datetime.combine(session_date, RTH_CLOSE, tzinfo=ET),
        )


def parse_ts_et(value: str) -> datetime:
    dt = datetime.fromisoformat(value)
    if dt.tzinfo is None:
        raise ValueError(f"naive timestamp not allowed: {value!r}")
    return dt.astimezone(ET)


def rth_filter(
    bars: list[dict],
    *,
    session_open: datetime,
    session_close: datetime,
    until_et: datetime | None = None,
) -> list[dict]:
    """Keep 5-minute bars inside the regular session whose close is confirmed.

    A bar opening at ``T`` covers ``[T, T+5min)`` and is kept iff
    ``session_open <= T``, ``T + 5min <= session_close`` and (when given)
    ``T + 5min <= until_et``.
    """
    out: list[dict] = []
    for bar in bars:
        ts = parse_ts_et(bar["ts_et"])
        bar_close = ts + BAR_5MIN
        if ts < session_open or bar_close > session_close:
            continue
        if until_et is not None and bar_close > until_et:
            continue
        out.append(bar)
    return out


def hourly_bars(bars_5min: list[dict], *, session_close: datetime | None = None) -> list[dict]:
    """Aggregate RTH 5-minute bars into clock-hour buckets.

    Buckets: ``[09:30,10:00)``, ``[10:00,11:00)``, ..., ``[15:00,16:00)``
    (the last bucket ends at ``session_close`` on early-close days). Each
    output row: ``{"ts_et", "end_et", "o", "h", "l", "c", "v", "closed"}``
    where ``closed`` is True iff the bucket's final 5-minute bar is present.
    """
    if not bars_5min:
        return []
    buckets: dict[datetime, list[dict]] = {}
    for bar in bars_5min:
        ts = parse_ts_et(bar["ts_et"])
        if ts.hour == 9:
            start = ts.replace(minute=30, second=0, microsecond=0)
        else:
            start = ts.replace(minute=0, second=0, microsecond=0)
        buckets.setdefault(start, []).append(bar)
    out: list[dict] = []
    for start in sorted(buckets):
        group = buckets[start]
        end = start.replace(minute=0) + timedelta(hours=1)
        if session_close is not None and end > session_close:
            end = session_close
        last_ts = parse_ts_et(group[-1]["ts_et"])
        out.append(
            {
                "ts_et": start.isoformat(),
                "end_et": end.isoformat(),
                "o": float(group[0]["o"]),
                "h": max(float(b["h"]) for b in group),
                "l": min(float(b["l"]) for b in group),
                "c": float(group[-1]["c"]),
                "v": int(sum(int(b["v"]) for b in group)),
                "closed": last_ts + BAR_5MIN >= end,
            }
        )
    return out


def cumulative_vwap(bars: list[dict]) -> list[float]:
    """Close-based cumulative session VWAP through each bar (same convention as
    ``skills/parabolic-short-trade-planner/scripts/vwap.py``)."""
    out: list[float] = []
    cum_pv = 0.0
    cum_v = 0
    for bar in bars:
        v = int(bar["v"])
        c = float(bar["c"])
        cum_pv += c * v
        cum_v += v
        out.append(c if cum_v == 0 else cum_pv / cum_v)
    return out
