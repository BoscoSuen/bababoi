"""Dividend adjustment properties (scripts/market_data/adjust.py)."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.market_data.adjust import apply_dividend_adjustment


def _bars(closes: list[float], start_day: int = 1) -> list[dict]:
    return [
        {
            "date": f"2026-08-{start_day + i:02d}",
            "open": c,
            "high": c,
            "low": c,
            "close": c,
            "adjClose": c,
            "volume": 100,
        }
        for i, c in enumerate(closes)
    ]


def test_no_dividends_leaves_adjclose_equal_to_close():
    bars = _bars([10.0, 11.0, 12.0])
    out = apply_dividend_adjustment(bars, [])
    assert [b["adjClose"] for b in out] == [10.0, 11.0, 12.0]
    assert bars[0]["adjClose"] == 10.0  # input untouched (copy semantics)


def test_single_dividend_scales_only_bars_before_ex_date():
    bars = _bars([100.0, 100.0, 100.0, 100.0])  # 08-01 .. 08-04
    divs = [{"ex_date": "2026-08-03", "cash_amount": 1.0, "type": "CD"}]
    out = apply_dividend_adjustment(bars, divs)
    ratios = [round(b["adjClose"] / b["close"], 6) for b in out]
    assert ratios[2] == 1.0 and ratios[3] == 1.0  # on/after ex-date unchanged
    assert ratios[0] == ratios[1] == round(1 - 1.0 / 100.0, 6)  # constant before


def test_two_dividends_compound_backwards():
    bars = _bars([50.0] * 6)  # 08-01 .. 08-06
    divs = [
        {"ex_date": "2026-08-03", "cash_amount": 0.5, "type": "CD"},
        {"ex_date": "2026-08-05", "cash_amount": 0.5, "type": "CD"},
    ]
    out = apply_dividend_adjustment(bars, divs)
    f = 1 - 0.5 / 50.0
    assert round(out[5]["adjClose"], 4) == 50.0
    assert round(out[4]["adjClose"], 4) == 50.0
    assert round(out[3]["adjClose"], 4) == round(50.0 * f, 4)
    assert round(out[2]["adjClose"], 4) == round(50.0 * f, 4)
    assert round(out[1]["adjClose"], 4) == round(50.0 * f * f, 4)


def test_dividend_before_window_and_non_cash_types_are_ignored():
    bars = _bars([20.0, 20.0])
    divs = [
        {"ex_date": "2026-07-15", "cash_amount": 5.0, "type": "CD"},  # before first bar
        {"ex_date": "2026-08-02", "cash_amount": 5.0, "type": "ST"},  # stock dividend
        {"ex_date": "2026-08-02", "cash_amount": 0.0, "type": "CD"},  # zero
    ]
    out = apply_dividend_adjustment(bars, divs)
    assert [b["adjClose"] for b in out] == [20.0, 20.0]


def test_empty_input():
    assert apply_dividend_adjustment([], [{"ex_date": "2026-08-02", "cash_amount": 1}]) == []
