"""Tests for scripts/send_swing_signal.py — daily watchlist hand-off to the intraday monitor."""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import send_swing_signal as sss  # noqa: E402


def _reports(tmp_path: Path) -> dict[str, Path]:
    vcp = tmp_path / "vcp_screener_2026-09-21_140541.json"
    vcp.write_text(
        json.dumps(
            {
                "results": [
                    {
                        "symbol": "ANET",
                        "price": 205.42,
                        "composite_score": 60.8,
                        "rating": "Developing VCP",
                        "execution_state": "Pre-breakout",
                        "distance_from_pivot_pct": -0.34,
                        "pivot_proximity": {"pivot_price": 206.13, "stop_loss_price": 179.46},
                    },
                    {
                        "symbol": "FTNT",
                        "price": 175.23,
                        "composite_score": 55.8,
                        "rating": "Weak VCP",
                        "execution_state": "Overextended",
                        "distance_from_pivot_pct": 1.82,
                        "pivot_proximity": {"pivot_price": 172.09, "stop_loss_price": 146.77},
                    },
                    {
                        "symbol": "FAR",
                        "price": 100.0,
                        "composite_score": 50.0,
                        "rating": "Weak VCP",
                        "execution_state": "Pre-breakout",
                        "distance_from_pivot_pct": -9.0,
                        "pivot_proximity": {"pivot_price": 110.0, "stop_loss_price": 90.0},
                    },
                ]
            }
        )
    )
    mb = tmp_path / "stockbee_momentum_burst_2026-09-21_140735.json"
    mb.write_text(
        json.dumps(
            {
                "candidates": [
                    {
                        "symbol": "AMGN",
                        "state": "ACTIONABLE_BUY",
                        "setup_score": 88,
                        "rating": "A-",
                        "primary_trigger": "range_expansion",
                        "day_gain_pct": 1.6,
                        "volume_ratio_20d": 3.2,
                        "entry_reference": 300.0,
                        "stop_reference": 290.0,
                    },
                    {
                        "symbol": "ANET",
                        "state": "WATCH_ONLY",
                        "setup_score": 62,
                        "rating": "Watch",
                        "primary_trigger": "dollar_breakout",
                        "day_gain_pct": 3.0,
                        "volume_ratio_20d": 0.94,
                        "entry_reference": 205.42,
                        "stop_reference": 200.74,
                    },
                    {
                        "symbol": "FTNT",
                        "state": "WATCH_ONLY",
                        "setup_score": 56,
                        "rating": "Watch",
                        "primary_trigger": "dollar_breakout",
                        "day_gain_pct": 3.2,
                        "volume_ratio_20d": 0.67,
                        "entry_reference": 175.23,
                        "stop_reference": 167.4,
                    },
                    {"symbol": "REJ", "state": "REJECTED", "setup_score": 0},
                ]
            }
        )
    )
    eh = tmp_path / "stockbee_exhaustion_hammer_2026-09-21_140852.json"
    eh.write_text(
        json.dumps(
            {
                "candidates": [
                    {
                        "symbol": "ADBE",
                        "state": "ACTIONABLE_CLOSE_BUY",
                        "setup_score": 83,
                        "rating": "A-",
                        "primary_trigger": "confirmed_exhaustion_hammer",
                        "day_gain_pct": 0.24,
                        "entry_reference": 249.52,
                        "stop_reference": 243.99,
                    },
                    {"symbol": "REJ", "state": "REJECTED", "setup_score": 0},
                ]
            }
        )
    )
    return {"vcp": vcp, "mb": mb, "eh": eh, "theme": None}


def test_build_watchlist_mirrors_signal_sections(tmp_path: Path) -> None:
    wl = sss.build_watchlist(_reports(tmp_path))
    by = {e["symbol"]: e for e in wl}
    # Every symbol the Discord message shows is on the watchlist, nothing else.
    assert set(by) == {"AMGN", "ADBE", "ANET", "FTNT"}
    assert by["AMGN"]["sources"] == ["momentum_burst"]
    assert by["AMGN"]["stop"] == 290.0 and by["AMGN"]["entry"] == 300.0
    assert by["ADBE"]["sources"] == ["exhaustion_hammer"]
    # ANET: near-pivot VCP + cross-signal; pivot/stop come from the VCP row.
    assert by["ANET"]["sources"] == ["vcp_near_pivot", "cross"]
    assert by["ANET"]["pivot"] == 206.13 and by["ANET"]["stop"] == 179.46
    assert "VCP 61 Pre-breakout" in by["ANET"]["note"] and "MB 62 WATCH_ONLY" in by["ANET"]["note"]
    # FTNT is Overextended: cross-signal only, no pivot (stop kept for reference).
    assert by["FTNT"]["sources"] == ["cross"] and "pivot" not in by["FTNT"]  # Overextended: no buy level
    # Symbols deduplicate: one entry per ticker, ordered by first appearance.
    assert [e["symbol"] for e in wl] == ["AMGN", "ADBE", "ANET", "FTNT"]


def test_build_watchlist_handles_missing_reports() -> None:
    assert sss.build_watchlist({"vcp": None, "mb": None, "eh": None}) == []


def test_write_daily_watchlist_overwrites_but_keeps_manual(tmp_path: Path) -> None:
    path = tmp_path / "daily_watchlist.json"
    path.write_text(
        json.dumps(
            {
                "date": "2026-09-18",
                "symbols": [{"symbol": "OLD", "sources": ["cross"]}],
                "manual": [{"symbol": "AMD", "stop": 582.27, "note": "position"}],
            }
        )
    )
    out = sss.write_daily_watchlist(
        path, "2026-09-21", [{"symbol": "ANET", "sources": ["cross"], "pivot": 206.13}]
    )
    data = json.loads(path.read_text())
    assert out == path
    assert data["date"] == "2026-09-21"
    assert [e["symbol"] for e in data["symbols"]] == ["ANET"]
    assert data["manual"] == [{"symbol": "AMD", "stop": 582.27, "note": "position"}]
    assert data["generated_at"]


def test_write_daily_watchlist_tolerates_empty_or_corrupt_file(tmp_path: Path) -> None:
    path = tmp_path / "daily_watchlist.json"
    path.write_text("")
    sss.write_daily_watchlist(path, "2026-09-21", [])
    data = json.loads(path.read_text())
    assert data["symbols"] == [] and data["manual"] == []
