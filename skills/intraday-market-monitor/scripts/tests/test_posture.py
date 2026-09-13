from __future__ import annotations

import json

import posture as p

CFG = {
    "weights": {"breadth": 0.4, "index": 0.3, "sector": 0.3},
    "allow_min_score": 60,
    "cash_max_score": 40,
    "cash_breadth_pct_advancers_max": 30,
    "cash_ud_ratio_max": 0.5,
    "hysteresis_slots": 2,
    "hysteresis_override_delta": 15,
}
SPY_OK = {
    "available": True,
    "above_vwap": True,
    "above_prev_high": False,
    "below_prev_low": False,
    "ret_open_pct": 0.3,
}
SPY_WEAK = {
    "available": True,
    "above_vwap": False,
    "above_prev_high": False,
    "below_prev_low": True,
    "ret_open_pct": -1.2,
}
BREADTH_OK = {"available": True, "pct_advancers": 60.0, "pct_above_vwap": 62.0, "ud_ratio": 2.0}
BREADTH_BAD = {"available": True, "pct_advancers": 20.0, "pct_above_vwap": 15.0, "ud_ratio": 0.3}


def test_component_scores():
    assert p.breadth_score(BREADTH_OK) == round((60 + 62 + 75) / 3, 1)
    assert p.breadth_score({"available": False}) is None
    assert p.index_score([SPY_OK, SPY_OK]) > 50 > p.index_score([SPY_WEAK, SPY_WEAK])
    assert p.index_score([]) is None
    assert p.sector_score({"risk_on_spread_pct": 1.0}) == 75.0
    assert p.sector_score({"risk_on_spread_pct": None}) is None


def test_composite_renormalises_missing_components():
    assert p.composite({"breadth": 80, "index": None, "sector": 40}, CFG["weights"]) == round(
        (80 * 0.4 + 40 * 0.3) / 0.7, 1
    )
    assert p.composite({"breadth": None, "index": None, "sector": None}, CFG["weights"]) is None


def test_recommend_rules():
    assert p.recommend(70, BREADTH_OK, SPY_OK, CFG)[0] == "NEW_ENTRY_ALLOWED"
    assert p.recommend(70, BREADTH_OK, dict(SPY_OK, above_vwap=False), CFG)[0] == "REDUCE_ONLY"
    assert p.recommend(50, BREADTH_OK, SPY_OK, CFG)[0] == "REDUCE_ONLY"
    assert p.recommend(35, BREADTH_OK, SPY_OK, CFG)[0] == "CASH_PRIORITY"
    rec, reasons = p.recommend(70, BREADTH_BAD, SPY_OK, CFG)
    assert rec == "CASH_PRIORITY" and "breadth_washout" in reasons
    rec, reasons = p.recommend(70, BREADTH_OK, SPY_WEAK, CFG)
    assert rec == "CASH_PRIORITY" and "spy_below_prev_low" in reasons
    assert p.recommend(None, {}, {}, CFG) == ("REDUCE_ONLY", ["insufficient_data"])


def test_hysteresis_needs_two_slots_unless_big_move():
    first = p.apply_hysteresis("NEW_ENTRY_ALLOWED", 65, None, CFG)
    assert first["recommendation"] == "NEW_ENTRY_ALLOWED" and first["streak"] == 1
    prev = {"recommendation": "NEW_ENTRY_ALLOWED", "score": 65, "streak": 3}
    step1 = p.apply_hysteresis("REDUCE_ONLY", 58, prev, CFG)
    assert step1["recommendation"] == "NEW_ENTRY_ALLOWED" and step1["pending_flip"] == "REDUCE_ONLY"
    prev2 = dict(prev, pending_flip="REDUCE_ONLY", pending_count=step1["pending_count"], score=58)
    step2 = p.apply_hysteresis("REDUCE_ONLY", 57, prev2, CFG)
    assert step2["recommendation"] == "REDUCE_ONLY" and step2["flipped_from"] == "NEW_ENTRY_ALLOWED"
    crash = p.apply_hysteresis("CASH_PRIORITY", 30, prev, CFG)
    assert (
        crash["recommendation"] == "CASH_PRIORITY" and crash["flipped_from"] == "NEW_ENTRY_ALLOWED"
    )


def test_daily_cap():
    assert p.apply_daily_cap("NEW_ENTRY_ALLOWED", "CASH_PRIORITY") == ("REDUCE_ONLY", True)
    assert p.apply_daily_cap("NEW_ENTRY_ALLOWED", "REDUCE_ONLY") == ("NEW_ENTRY_ALLOWED", False)
    assert p.apply_daily_cap("REDUCE_ONLY", None) == ("REDUCE_ONLY", False)


def test_state_and_baseline(tmp_path):
    store = p.PostureState(tmp_path)
    assert store.load("2026-09-11") is None
    store.save({"session_date": "2026-09-11", "recommendation": "REDUCE_ONLY", "score": 50})
    assert store.load("2026-09-11")["recommendation"] == "REDUCE_ONLY"
    assert store.load("2026-09-12") is None  # new session resets
    (tmp_path / "reports").mkdir()
    (tmp_path / "reports" / "exposure_posture_2026-09-10.json").write_text(
        json.dumps({"recommendation": "CASH_PRIORITY"})
    )
    (tmp_path / "reports" / "exposure_posture_2026-09-11.json").write_text(
        json.dumps({"recommendation": "REDUCE_ONLY"})
    )
    base = p.load_daily_baseline("reports/exposure_posture_*.json", tmp_path)
    assert base["recommendation"] == "REDUCE_ONLY" and base["source_file"].endswith(
        "2026-09-11.json"
    )
    assert p.load_daily_baseline("reports/none_*.json", tmp_path) is None
