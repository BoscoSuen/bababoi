"""Run-slot arithmetic and the per-session ledger.

A slot ``HHMM`` is the ET wall-clock time the job is *meant* to run. With a
15-minute delayed feed the data horizon is ``until_et = floor5(slot - 15min)``,
so the 10:20 slot sees confirmed bars through 10:05 and the clock-hour bar
that closed at 10:00 is complete.
"""

from __future__ import annotations

import json
from datetime import date, datetime, timedelta
from pathlib import Path

import _repo_bootstrap  # noqa: F401

from scripts.market_data.timeutil import ET, floor5

# Half-hourly: HH:20 confirms the clock-hour bar that closed at HH:00, HH:50 the
# half-hour through HH:30 (posture inputs are hourly, so HH:50 mostly re-checks
# watchlist levels). 09:50 = opening read, 16:20 = full-session wrap-up.
DEFAULT_SLOTS = (
    "0950", "1020", "1050", "1120", "1150", "1220", "1250",
    "1320", "1350", "1420", "1450", "1520", "1550", "1620",
)  # fmt: skip


def slot_time(session_date: date, slot: str) -> datetime:
    return datetime(
        session_date.year,
        session_date.month,
        session_date.day,
        int(slot[:2]),
        int(slot[2:]),
        tzinfo=ET,
    )


def until_for(now_et: datetime, *, delay_minutes: int = 15) -> datetime:
    """Data horizon for a run at ``now_et`` (5-minute floor of now minus the feed delay)."""
    return floor5(now_et.astimezone(ET) - timedelta(minutes=delay_minutes))


def due_slots(now_et: datetime, slots=DEFAULT_SLOTS) -> list[str]:
    session_date = now_et.astimezone(ET).date()
    return [s for s in slots if slot_time(session_date, s) <= now_et]


def resolve_auto_slot(now_et: datetime, done: set[str], slots=DEFAULT_SLOTS) -> str | None:
    """Latest due slot that has not run yet (catch-up after sleep), else ``None``."""
    pending = [s for s in due_slots(now_et, slots) if s not in done]
    return pending[-1] if pending else None


class SlotLedger:
    """``state/intraday/<date>/slots_done.json`` → {"done": ["0950", ...]}."""

    def __init__(self, state_dir: Path, session_date: date) -> None:
        self.path = Path(state_dir) / session_date.isoformat() / "slots_done.json"

    def load(self) -> set[str]:
        if not self.path.is_file():
            return set()
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return set()
        return set(data.get("done") or [])

    def mark(self, slot: str) -> None:
        self.mark_many([slot])

    def mark_many(self, slots) -> None:
        done = self.load()
        done.update(slots)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps({"done": sorted(done)}, indent=1) + "\n", encoding="utf-8")
