from __future__ import annotations

from datetime import datetime

import breadth_metrics as bm

from scripts.market_data.timeutil import ET

CURVE = [[0, 0.0], [30, 0.15], [60, 0.24], [390, 1.0]]
OPEN = datetime(2026, 9, 11, 9, 30, tzinfo=ET)
CLOSE = datetime(2026, 9, 11, 16, 0, tzinfo=ET)


def _row(sym, c, prev_c, vw=None, v=1_000_000, prev_v=1_000_000, prev_h=None, prev_l=None):
    return {
        "symbol": sym,
        "day": {
            "o": prev_c,
            "h": max(c, prev_c),
            "l": min(c, prev_c),
            "c": c,
            "v": v,
            "vw": vw or prev_c,
        },
        "prev_day": {
            "o": prev_c,
            "h": prev_h or prev_c * 1.01,
            "l": prev_l or prev_c * 0.99,
            "c": prev_c,
            "v": prev_v,
            "vw": prev_c,
        },
        "change_pct": (c / prev_c - 1) * 100,
    }


def test_filter_universe_applies_symbol_price_and_volume_floors():
    rows = [
        _row("AAPL", 10, 9),
        _row("BRK.B", 10, 9),  # dot class excluded by regex
        _row("PENNY", 1.0, 0.9),  # prev close < 5
        _row("THIN", 10, 9, prev_v=10),  # prev volume < 100k
        {"symbol": "NOPREV", "day": {"c": 1}, "prev_day": None},
    ]
    assert [r["symbol"] for r in bm.filter_universe(rows)] == ["AAPL"]


def test_elapsed_fraction_interpolates_and_rescales_for_early_close():
    assert bm.elapsed_fraction(OPEN, OPEN, CLOSE, CURVE) == 0.0
    assert (
        round(bm.elapsed_fraction(datetime(2026, 9, 11, 10, 15, tzinfo=ET), OPEN, CLOSE, CURVE), 3)
        == 0.195
    )
    assert bm.elapsed_fraction(CLOSE, OPEN, CLOSE, CURVE) == 1.0
    early_close = datetime(2026, 9, 11, 13, 0, tzinfo=ET)
    assert bm.elapsed_fraction(early_close, OPEN, early_close, CURVE) == 1.0


def test_compute_breadth_counts_and_ratios():
    rows = [
        _row("A", 11, 10, vw=10.5, v=200),  # up, above vwap, above prev high (10.1)
        _row("B", 9, 10, vw=9.5, v=100),  # down, below vwap, below prev low (9.9)
        _row("C", 10.05, 10, vw=10.1, v=100),  # up, below vwap
    ]
    out = bm.compute_breadth(rows, avg_volume={"A": 1000, "B": 1000, "C": 1000}, elapsed=0.2)
    assert out["universe_size"] == 3
    assert out["pct_advancers"] == 66.7 and out["pct_decliners"] == 33.3
    assert out["pct_above_vwap"] == 33.3
    assert out["pct_above_prev_high"] == 33.3 and out["pct_below_prev_low"] == 33.3
    assert out["up_volume"] == 300 and out["down_volume"] == 100 and out["ud_ratio"] == 3.0
    # 400 traded vs 3000 avg * 0.2 elapsed = 600 expected
    assert out["volume_pace"] == round(400 / 600, 3)
    assert out["avg_volume_coverage"] == 1.0


def test_compute_breadth_handles_empty_and_missing_avg():
    assert bm.compute_breadth([], avg_volume=None, elapsed=0.5)["available"] is False
    out = bm.compute_breadth([_row("A", 11, 10)], avg_volume=None, elapsed=0.5)
    assert out["volume_pace"] is None and out["ud_ratio"] is None


def test_avg_volume_by_symbol():
    days = [{"A": {"volume": 100}, "B": {"volume": 10}}, {"A": {"volume": 300}}]
    assert bm.avg_volume_by_symbol(days) == {"A": 200.0, "B": 10.0}
