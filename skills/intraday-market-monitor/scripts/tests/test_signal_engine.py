"""Core paths of signal_engine: armed → 🟢 → 🟢🟢🟢, shakeout vs real VWAP loss, kill."""

from __future__ import annotations

import signal_engine as se

OPEN = "2026-09-17T09:30:00-04:00"


def _bars(closes, *, vols=None, start_h=9, start_m=30):
    """5-min bars walking through ``closes``; o = previous close."""
    out, prev, h, m = [], closes[0], start_h, start_m
    for i, c in enumerate(closes):
        v = vols[i] if vols else 1000
        out.append({"ts_et": f"2026-09-17T{h:02d}:{m:02d}:00-04:00", "o": prev, "h": max(prev, c) + 0.05, "l": min(prev, c) - 0.05, "c": c, "v": v})
        prev = c
        m += 5
        if m >= 60:
            h, m = h + 1, m - 60
    return out


def _daily(prev_close=100.0, n=25, prev_low=98.0):
    # flat history: SMA20 = prev_close, ATR ≈ 2
    return [{"close": prev_close, "high": prev_close + 1, "low": prev_low, "volume": 1_000_000} for _ in range(n)]


def _hist(today_vol_per_bar=1000, n_days=20, quiet_ratio=0.4):
    # prior sessions carry ~40% of today's per-bar volume → today is p100
    return [_bars([100 + i * 0.01 for i in range(78)], vols=[int(today_vol_per_bar * quiet_ratio)] * 78) for _ in range(n_days)]


def _data(today, *, hist=None, etf=0.0, daily=None, until="10:05"):
    return se.SlotData(
        bars=lambda sym: today,
        hist_bars=lambda sym: hist if hist is not None else _hist(),
        daily=lambda sym: daily or _daily(),
        etf_chg=lambda e: etf,
        sector=lambda sym: {"sector": "Technology", "industry": "Semiconductors"},
        until_hm=until,
    )


PIVOT = {"symbol": "AMD", "pivot": 100.0, "stop": 90.0, "sources": ["vcp_near_pivot"], "sector": "Technology", "industry": "Semiconductors"}
# 10:05: eight bars, last close 1.8% over the pivot (inside the 2% chase limit), above VWAP.
UP = [99.5, 100.2, 100.8, 101.2, 101.5, 101.6, 101.7, 101.8]
# Six more bars that close under the cumulative VWAP (~101) but stay above the pivot.
DIP = [100.9, 100.8, 100.7, 100.6, 100.5, 100.4]


def test_pivot_break_first_slot_is_one_green_then_climbs():
    # sector ETF also up 4% → RS ≈ −2 → only the trigger: 🟢
    state, sig = se.evaluate_slot({}, slot="1020", candidates={"AMD": PIVOT}, data=_data(_bars(UP), etf=4.0))
    row = next(r for r in sig if r["symbol"] == "AMD")
    assert row["level"] == "BUY" and row["tier"] == 1 and row["new"] is True
    assert row["stop"] == 100.0 * 0.95  # pivot −5% (contraction low 90 is wider)
    # 11:05: held, closes at the high, RS vs XLK +5%, volume p100, not extended → 🟢🟢🟢
    up2 = UP + [102.0, 102.3, 102.6, 103.0, 103.4, 103.8, 104.0, 104.3, 104.5, 104.8, 105.0, 105.2]
    state, sig = se.evaluate_slot(state, slot="1120", candidates={"AMD": PIVOT}, data=_data(_bars(up2), etf=0.0, until="11:05"))
    row = next(r for r in sig if r["symbol"] == "AMD")
    assert row["tier"] == 3 and row["held"] == 2 and row["new"] is False


def test_pivot_over_but_thin_volume_is_armed():
    busy_hist = _hist(quiet_ratio=1.5)  # history busier than today → low percentile
    _, sig = se.evaluate_slot({}, slot="1020", candidates={"AMD": PIVOT}, data=_data(_bars(UP), hist=busy_hist))
    assert sig[0]["level"] == "ARMED" and sig[0]["tier"] == 0


def test_chasing_more_than_two_percent_above_pivot_is_not_a_buy():
    up = [100, 101, 102, 103, 103.5, 104, 104.2, 104.3]  # +4.3% over pivot
    _, sig = se.evaluate_slot({}, slot="1020", candidates={"AMD": PIVOT}, data=_data(_bars(up)))
    assert sig[0]["level"] == "ARMED"


def test_shakeout_below_vwap_on_thin_volume_does_not_demote():
    state, _ = se.evaluate_slot({}, slot="1020", candidates={"AMD": PIVOT}, data=_data(_bars(UP), etf=4.0))
    vols = [1000] * len(UP) + [100] * 6  # dip on ~10% of the session's per-bar volume
    state, sig = se.evaluate_slot(state, slot="1050", candidates={"AMD": PIVOT}, data=_data(_bars(UP + DIP, vols=vols), until="10:35"))
    row = sig[0]
    assert row["level"] == "BUY" and row["tier"] == 1 and "shakeout" in (row.get("note") or "")
    assert state["AMD"]["below"] == 0


def test_two_slots_below_vwap_on_volume_demotes_and_stop_kills():
    state, _ = se.evaluate_slot({}, slot="1020", candidates={"AMD": PIVOT}, data=_data(_bars(UP), etf=4.0))
    state["AMD"]["tier"] = 2  # pretend it had climbed
    vols = [1000] * len(UP) + [3000] * 6  # heavy selling under VWAP
    state, sig = se.evaluate_slot(state, slot="1050", candidates={"AMD": PIVOT}, data=_data(_bars(UP + DIP, vols=vols), until="10:35"))
    assert sig[0]["level"] == "BUY" and state["AMD"]["below"] == 1  # first slot: only counted
    dip2 = UP + DIP + [100.4, 100.3, 100.35, 100.3, 100.25, 100.3]
    vols2 = vols + [3000] * 6
    state, sig = se.evaluate_slot(state, slot="1120", candidates={"AMD": PIVOT}, data=_data(_bars(dip2, vols=vols2), until="11:05"))
    assert sig[0]["level"] == "DOWN" and sig[0]["tier"] == 1
    crash = dip2 + [99, 97, 95.5, 94.8, 94.5, 94.4]  # below the pivot −5% stop
    state, sig = se.evaluate_slot(state, slot="1150", candidates={"AMD": PIVOT}, data=_data(_bars(crash, vols=vols2 + [3000] * 6), until="11:35"))
    assert sig[0]["level"] == "DEAD" and state["AMD"]["dead"] is True


def test_momentum_burst_needs_quiet_prior_days_and_position_rows_hold_or_exit():
    burst = [100, 101, 102, 103, 104, 104.3, 104.5, 104.6]  # +4.6%, day low within 5%
    cand = {"NEW": {"symbol": "NEW", "sources": ["scan"], "sector": "Technology", "industry": "Software"}}
    _, sig = se.evaluate_slot({}, slot="1020", candidates=cand, data=_data(_bars(burst)))
    assert sig and sig[0]["kind"] == "MB" and sig[0]["level"] == "BUY" and sig[0]["stop"] == burst[0] - 0.05
    # a +6% day two sessions ago disqualifies day-1 status
    ran = _daily()
    ran[1]["close"] = 106.0  # rows newest-first: prev session close 100, the one before 106 → chg3[1] = -5.7, chg3[2]...
    ran[2]["close"] = 100.0
    ran[0]["close"] = 100.0
    ran[1]["close"] = 95.0
    ran[2]["close"] = 89.0  # 95/89 = +6.7% on chg3[1]
    _, sig = se.evaluate_slot({}, slot="1020", candidates=cand, data=_data(_bars(burst), daily=ran))
    assert not sig
    # positions: HOLD while above stop, EXIT below stop
    pos = {"ARM": {"symbol": "ARM", "position": {"entry_price": 90.0, "stop": 99.0}, "sources": ["manual"]}}
    _, sig = se.evaluate_slot({}, slot="1020", candidates=pos, data=_data(_bars([100, 101, 102, 103])))
    assert sig[0]["level"] == "HOLD" and round(sig[0]["pnl_pct"], 1) == 14.4
    _, sig = se.evaluate_slot({}, slot="1050", candidates=pos, data=_data(_bars([100, 99.5, 98.9, 98.5])))
    assert sig[0]["level"] == "EXIT" and sig[0]["reason"] == "< stop"


def test_render_lines_orders_strongest_first():
    rows = [
        {"symbol": "B", "kind": "MB", "level": "BUY", "tier": 1, "new": True, "price": 50.0, "chg": 5.0, "from_open": 3.0, "vol_pct": 95, "rs": 2.0, "etf": "XLK", "close_loc": 0.9, "stop": 48.0, "stop_pct": -4.0, "held": 1, "theme_n": 1},
        {"symbol": "A", "kind": "PIVOT", "level": "BUY", "tier": 3, "new": False, "price": 105.0, "pivot": 104.0, "chg": 5.0, "from_open": 4.0, "vol_pct": 100, "rs": 4.5, "etf": "XLK", "close_loc": 0.95, "stop": 98.8, "stop_pct": -5.9, "held": 3, "theme_n": 3, "industry": "Semiconductors"},
        {"symbol": "C", "kind": "PIVOT", "level": "ARMED", "tier": 0, "price": 101.0, "pivot": 100.0, "vol_pct": 70, "reason": "volume light"},
        {"symbol": "P", "kind": "POS", "level": "HOLD", "pnl_pct": 12.0, "above_vwap": True, "stop": 90.0, "stop_pct": -8.0},
    ]
    lines = se.render_lines(rows)
    assert lines[0].startswith("🟢🟢🟢") and "A    " in lines[0] and "Semiconductors×3" in lines[0]
    assert lines[1].startswith("🟢★") and "B" in lines[1]
    assert lines[2].startswith("HOLD") and lines[3].startswith("⚪")
