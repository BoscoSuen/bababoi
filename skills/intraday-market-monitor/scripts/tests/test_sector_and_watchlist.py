from __future__ import annotations

from datetime import datetime

import sector_rs
import watchlist_signals as ws

from scripts.market_data.timeutil import ET

OPEN = datetime(2026, 9, 11, 9, 30, tzinfo=ET)
CLOSE = datetime(2026, 9, 11, 16, 0, tzinfo=ET)


def _bars(path: list[float], start="09:30", v=100):
    """5-min bars walking through ``path`` closes (o = previous close)."""
    h, m = int(start[:2]), int(start[3:])
    out = []
    prev = path[0]
    for c in path:
        ts = datetime(2026, 9, 11, h, m, tzinfo=ET)
        out.append(
            {
                "ts_et": ts.isoformat(),
                "o": prev,
                "h": max(prev, c) + 0.1,
                "l": min(prev, c) - 0.1,
                "c": c,
                "v": v,
            }
        )
        prev = c
        m += 5
        if m >= 60:
            h, m = h + 1, m - 60
    return out


def test_index_state_flags():
    bars = _bars([100, 101, 102, 103, 104, 105, 106, 107])  # 09:30..10:05 → hour 09:30-10:00 closed
    state = sector_rs.index_state(bars, {"h": 104.0, "l": 98.0, "c": 99.0}, session_close=CLOSE)
    assert state["available"] and state["above_vwap"] and state["above_prev_high"]
    assert not state["below_prev_low"]
    assert state["last_hour"]["end_et"].endswith("10:00:00-04:00")
    assert state["gap_pct"] == round((100 / 99 - 1) * 100, 3)
    assert sector_rs.index_state([], None)["available"] is False


def test_sector_rs_ranks_and_spread():
    spy = _bars([100, 101, 102, 103, 104, 105, 106, 107])
    strong = _bars([100, 102, 104, 106, 108, 110, 112, 114])
    weak = _bars([100, 100, 100, 100, 100, 100, 100, 100])
    out = sector_rs.compute_sector_rs(
        {"SPY": spy, "XLK": strong, "XLU": weak},
        risk_on=["XLK"],
        risk_off=["XLU"],
        session_close=CLOSE,
    )
    assert out["available"]
    assert [r["symbol"] for r in out["sectors"]] == ["XLK", "XLU"]
    assert out["sectors"][0]["rank"] == 1 and out["sectors"][0]["rs_open_pct"] > 0
    assert out["sectors"][1]["rs_open_pct"] < 0
    assert out["risk_on_spread_pct"] == round(
        out["sectors"][0]["rs_open_pct"] - out["sectors"][1]["rs_open_pct"], 3
    )
    assert out["sectors"][0]["rs_last_hour_pct"] is not None


def test_sector_rs_without_benchmark():
    assert (
        sector_rs.compute_sector_rs({"XLK": _bars([1, 2])}, risk_on=[], risk_off=[])["available"]
        is False
    )


def _eval(bars, prev_day=None, avg=None, elapsed=0.3):
    return ws.evaluate_symbol(
        "T",
        bars,
        prev_day=prev_day,
        avg_volume=avg,
        elapsed=elapsed,
        session_open=OPEN,
        session_close=CLOSE,
    )


def test_watchlist_fhr_breakout_requires_two_closed_hours_and_rel_vol():
    # 09:30..11:55: first hour 09:30-10:30 range 100..104; 10:00-11:00 bar closes above.
    path = [
        100,
        101,
        102,
        103,
        104,
        103,
        102,
        103,
        104,
        105,
        106,
        107,
        108,
        109,
        110,
        111,
        112,
        113,
        114,
        115,
        116,
        117,
        118,
        119,
        120,
        121,
        122,
        123,
        124,
        125,
    ]
    bars = _bars(path)  # through 11:55
    hi_vol = _eval(
        bars, prev_day={"c": 99, "h": 100, "l": 98}, avg=1000, elapsed=1.0
    )  # rel_vol = 3000/1000 = 3
    assert hi_vol["first_hour_complete"] and hi_vol["fhr_high"] == 107.1
    assert "FHR_BREAKOUT" in hi_vol["signals"]
    lo_vol = _eval(bars, prev_day={"c": 99, "h": 100, "l": 98}, avg=100000, elapsed=1.0)
    assert "FHR_BREAKOUT" not in lo_vol["signals"]


def test_watchlist_gap_hold_and_vwap_loss():
    # gap +5%, first half hour strong, then the 10:00-11:00 bar fades below VWAP and
    # below the session open; a partial 11:00 bucket must be ignored.
    first = [105, 106, 107, 108, 109, 110]  # 09:30-09:55
    second = [112, 114, 116, 118, 116, 112, 108, 104, 102, 100, 99, 98]  # 10:00-10:55
    partial = [97, 96]  # 11:00-11:05 (bucket not closed)
    bars = _bars(first + second + partial)
    out = _eval(bars, prev_day={"c": 100, "h": 101, "l": 99})
    assert out["gap_pct"] == 5.0
    assert out["hourly_close"] == 98 and out["hourly_bar_end_et"].endswith("11:00:00-04:00")
    assert "VWAP_LOSS" in out["signals"]
    assert "GAP_FAIL" in out["signals"] and "GAP_HOLD" not in out["signals"]
    strong = _eval(
        _bars(first + [111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122]),
        prev_day={"c": 100, "h": 101, "l": 99},
    )
    assert "GAP_HOLD" in strong["signals"]


def test_watchlist_empty_and_loader(tmp_path):
    assert _eval([])["available"] is False
    wl = tmp_path / "watchlist.yaml"
    wl.write_text("symbols:\n  - aapl\n  - symbol: MSFT\n  - AAPL\n", encoding="utf-8")
    vcp = tmp_path / "vcp_screener_x.json"
    vcp.write_text(
        '{"results": [{"symbol": "NVDA", "rating": "A"}, {"symbol": "XYZ", "rating": "C"}]}',
        encoding="utf-8",
    )
    assert ws.load_watchlist(wl, vcp_json=vcp) == ["AAPL", "MSFT", "NVDA"]
    assert ws.load_watchlist(tmp_path / "missing.yaml") == []
