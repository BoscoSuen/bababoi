"""Hourly exposure posture: score → recommendation with hysteresis and a daily cap.

Recommendation tokens match exposure-coach / pre-trade-discipline-gate:
``NEW_ENTRY_ALLOWED`` > ``REDUCE_ONLY`` > ``CASH_PRIORITY``.
"""

from __future__ import annotations

import glob
import json
from pathlib import Path

ORDER = ["CASH_PRIORITY", "REDUCE_ONLY", "NEW_ENTRY_ALLOWED"]


def _clip(x: float, lo: float = 0.0, hi: float = 100.0) -> float:
    return max(lo, min(hi, x))


def breadth_score(b: dict) -> float | None:
    if not b or not b.get("available"):
        return None
    parts = [b["pct_advancers"], b["pct_above_vwap"]]
    ud = b.get("ud_ratio")
    if ud is not None:
        # 0.5 → 25, 1.0 → 50, 2.0 → 75, 4.0 → 100 (log2 scale around parity)
        import math

        parts.append(_clip(50 + 25 * math.log2(max(ud, 1e-6))))
    return round(sum(parts) / len(parts), 1)


def index_score(states: list[dict]) -> float | None:
    usable = [s for s in states if s and s.get("available")]
    if not usable:
        return None
    score = 50.0
    per = 50.0 / len(usable)
    for s in usable:
        score += per * 0.5 if s["above_vwap"] else -per * 0.5
        if s["above_prev_high"]:
            score += per * 0.3
        if s["below_prev_low"]:
            score -= per * 0.5
        ret = s.get("ret_open_pct") or 0.0
        score += _clip(ret * per * 0.2, -per * 0.2, per * 0.2)
    return round(_clip(score), 1)


def sector_score(sectors: dict) -> float | None:
    spread = (sectors or {}).get("risk_on_spread_pct")
    if spread is None:
        return None
    return round(_clip(50 + spread * 25), 1)


def composite(parts: dict[str, float | None], weights: dict[str, float]) -> float | None:
    usable = {k: v for k, v in parts.items() if v is not None}
    if not usable:
        return None
    total_w = sum(weights[k] for k in usable)
    return round(sum(v * weights[k] for k, v in usable.items()) / total_w, 1)


def recommend(score: float | None, breadth: dict, spy: dict, cfg: dict) -> tuple[str, list[str]]:
    reasons: list[str] = []
    if score is None:
        return "REDUCE_ONLY", ["insufficient_data"]
    spy_ok = spy.get("available", False)
    if score < cfg["cash_max_score"]:
        reasons.append(f"score<{cfg['cash_max_score']}")
    if (
        breadth.get("available")
        and breadth["pct_advancers"] < cfg["cash_breadth_pct_advancers_max"]
        and (breadth.get("ud_ratio") or 0) < cfg["cash_ud_ratio_max"]
    ):
        reasons.append("breadth_washout")
    if spy_ok and spy["below_prev_low"]:
        reasons.append("spy_below_prev_low")
    if reasons:
        return "CASH_PRIORITY", reasons
    if score >= cfg["allow_min_score"] and spy_ok and spy["above_vwap"]:
        return "NEW_ENTRY_ALLOWED", [f"score>={cfg['allow_min_score']}", "spy_above_vwap"]
    if score >= cfg["allow_min_score"]:
        return "REDUCE_ONLY", ["spy_below_vwap"]
    return "REDUCE_ONLY", ["score_middle_band"]


def apply_hysteresis(candidate: str, score: float | None, prev: dict | None, cfg: dict) -> dict:
    """Require ``hysteresis_slots`` consecutive candidates before flipping, unless
    the score moved by ``hysteresis_override_delta`` or more."""
    if not prev or prev.get("recommendation") not in ORDER:
        return {
            "recommendation": candidate,
            "flipped_from": None,
            "pending_flip": None,
            "streak": 1,
        }
    current = prev["recommendation"]
    if candidate == current:
        return {
            "recommendation": current,
            "flipped_from": None,
            "pending_flip": None,
            "streak": prev.get("streak", 1) + 1,
        }
    pending = prev.get("pending_flip")
    pending_count = prev.get("pending_count", 0) if pending == candidate else 0
    pending_count += 1
    delta = abs((score or 0) - (prev.get("score") or 0))
    if pending_count >= cfg["hysteresis_slots"] or delta >= cfg["hysteresis_override_delta"]:
        return {
            "recommendation": candidate,
            "flipped_from": current,
            "pending_flip": None,
            "streak": 1,
        }
    return {
        "recommendation": current,
        "flipped_from": None,
        "pending_flip": candidate,
        "pending_count": pending_count,
        "streak": prev.get("streak", 1) + 1,
    }


def apply_daily_cap(recommendation: str, baseline: str | None, steps: int = 1) -> tuple[str, bool]:
    """Never sit more than ``steps`` above the daily exposure-coach posture."""
    if baseline not in ORDER:
        return recommendation, False
    cap = min(ORDER.index(baseline) + steps, len(ORDER) - 1)
    if ORDER.index(recommendation) > cap:
        return ORDER[cap], True
    return recommendation, False


def load_daily_baseline(pattern: str, root: Path) -> dict | None:
    files = sorted(glob.glob(str(root / pattern)))
    if not files:
        return None
    path = files[-1]
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    rec = data.get("recommendation")
    return {
        "recommendation": rec if rec in ORDER else None,
        "source_file": path,
        "generated_at": data.get("generated_at"),
    }


class PostureState:
    """``state/intraday/last_posture.json``."""

    def __init__(self, state_dir: Path) -> None:
        self.path = Path(state_dir) / "last_posture.json"

    def load(self, session_date: str) -> dict | None:
        if not self.path.is_file():
            return None
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return None
        # A new session starts fresh; yesterday's posture must not gate today.
        return data if data.get("session_date") == session_date else None

    def save(self, data: dict) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(data, indent=1, sort_keys=True) + "\n", encoding="utf-8")
