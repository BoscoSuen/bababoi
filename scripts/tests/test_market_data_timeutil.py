"""ET conversion, RTH filtering and hourly aggregation (scripts/market_data/timeutil.py)."""

from __future__ import annotations

import sys
from datetime import date, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import pytest  # noqa: E402

from scripts.market_data import timeutil
from scripts.market_data.timeutil import (
    ET,
    cumulative_vwap,
    floor5,
    hourly_bars,
    ms_to_et,
    rth_filter,
    session_bounds,
)


def _bar(hhmm: str, o=1.0, h=1.0, l=1.0, c=1.0, v=10, day="2026-09-11"):  # noqa: E741
    return {"ts_et": f"{day}T{hhmm}:00-04:00", "o": o, "h": h, "l": l, "c": c, "v": v}


def test_ms_to_et_is_dst_aware():
    # 2026-09-11 13:30:00 UTC == 09:30 EDT
    assert ms_to_et(1789133400000).isoformat() == "2026-09-11T09:30:00-04:00"
    # 2026-01-15 14:30:00 UTC == 09:30 EST
    assert ms_to_et(1768487400000).isoformat() == "2026-01-15T09:30:00-05:00"


def test_floor5():
    dt = datetime(2026, 9, 11, 10, 23, 45, tzinfo=ET)
    assert floor5(dt).isoformat() == "2026-09-11T10:20:00-04:00"


def test_session_bounds_weekend_is_none_and_weekday_is_rth():
    assert session_bounds(date(2026, 9, 12)) is None  # Saturday
    bounds = session_bounds(date(2026, 9, 11))
    assert bounds is not None
    o, c = bounds
    assert (o.hour, o.minute) == (9, 30) and (c.hour, c.minute) == (16, 0)


def test_rth_filter_drops_premarket_afterhours_and_unconfirmed():
    o = datetime(2026, 9, 11, 9, 30, tzinfo=ET)
    c = datetime(2026, 9, 11, 16, 0, tzinfo=ET)
    bars = [
        _bar("09:25"),
        _bar("09:30"),
        _bar("09:55"),
        _bar("10:00"),
        _bar("15:55"),
        _bar("16:00"),
    ]
    kept = rth_filter(bars, session_open=o, session_close=c)
    assert [b["ts_et"][11:16] for b in kept] == ["09:30", "09:55", "10:00", "15:55"]
    until = datetime(2026, 9, 11, 10, 3, tzinfo=ET)  # 10:00 bar closes 10:05 > until → dropped
    kept = rth_filter(bars, session_open=o, session_close=c, until_et=until)
    assert [b["ts_et"][11:16] for b in kept] == ["09:30", "09:55"]


def test_rth_filter_rejects_naive_timestamps():
    with pytest.raises(ValueError):
        rth_filter(
            [{"ts_et": "2026-09-11T09:30:00"}],
            session_open=datetime.now(ET),
            session_close=datetime.now(ET),
        )


def test_hourly_bars_first_bucket_is_half_hour_and_closed_flag():
    bars = [
        _bar("09:30", o=10, h=12, l=9, c=11, v=5),
        _bar("09:55", o=11, h=13, l=10, c=12, v=5),
        _bar("10:00", o=12, h=12, l=11, c=11.5, v=7),
        _bar("10:05", o=11.5, h=14, l=11, c=13, v=7),
    ]
    out = hourly_bars(bars)
    assert [b["ts_et"][11:16] for b in out] == ["09:30", "10:00"]
    first, second = out
    assert first["o"] == 10 and first["h"] == 13 and first["l"] == 9 and first["c"] == 12
    assert first["v"] == 10 and first["closed"] is True  # 09:55 bar closes at 10:00
    assert second["end_et"][11:16] == "11:00" and second["closed"] is False


def test_hourly_bars_respects_early_close():
    close = datetime(2026, 11, 27, 13, 0, tzinfo=ET)
    bars = [_bar("12:00", day="2026-11-27").copy(), _bar("12:55", day="2026-11-27")]
    for b in bars:
        b["ts_et"] = b["ts_et"].replace("-04:00", "-05:00")
    out = hourly_bars(bars, session_close=close)
    assert out[-1]["end_et"][11:16] == "13:00" and out[-1]["closed"] is True


def test_cumulative_vwap_matches_manual():
    bars = [_bar("09:30", c=10, v=10), _bar("09:35", c=20, v=10), _bar("09:40", c=30, v=0)]
    assert cumulative_vwap(bars) == [10.0, 15.0, 15.0]


def test_now_et_is_aware():
    assert timeutil.now_et().tzinfo is not None
