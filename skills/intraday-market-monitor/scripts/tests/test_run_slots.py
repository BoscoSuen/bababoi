from __future__ import annotations

from datetime import date, datetime

from run_slots import DEFAULT_SLOTS, SlotLedger, due_slots, resolve_auto_slot, slot_time, until_for

from scripts.market_data.timeutil import ET


def test_until_for_is_five_minute_floor_of_now_minus_delay():
    now = datetime(2026, 9, 11, 10, 20, tzinfo=ET)
    assert until_for(now).isoformat() == "2026-09-11T10:05:00-04:00"
    late = datetime(2026, 9, 11, 10, 23, 40, tzinfo=ET)
    assert until_for(late).isoformat() == "2026-09-11T10:05:00-04:00"


def test_slot_time_and_due_slots():
    d = date(2026, 9, 11)
    assert slot_time(d, "1520").hour == 15 and slot_time(d, "1520").minute == 20
    now = datetime(2026, 9, 11, 12, 30, tzinfo=ET)
    assert due_slots(now) == ["0950", "1020", "1050", "1120", "1150", "1220"]


def test_default_slots_are_half_hourly():
    assert len(DEFAULT_SLOTS) == 14
    assert DEFAULT_SLOTS[:3] == ("0950", "1020", "1050")
    assert DEFAULT_SLOTS[-3:] == ("1520", "1550", "1620")
    assert all(s.endswith(("20", "50")) for s in DEFAULT_SLOTS)


def test_resolve_auto_slot_catches_up_to_latest_pending():
    now = datetime(2026, 9, 11, 13, 45, tzinfo=ET)
    assert resolve_auto_slot(now, {"0950", "1020"}) == "1320"
    assert resolve_auto_slot(now, set(DEFAULT_SLOTS)) is None
    early = datetime(2026, 9, 11, 9, 0, tzinfo=ET)
    assert resolve_auto_slot(early, set()) is None


def test_ledger_roundtrip(tmp_path):
    ledger = SlotLedger(tmp_path, date(2026, 9, 11))
    assert ledger.load() == set()
    ledger.mark("1020")
    ledger.mark("0950")
    assert ledger.load() == {"0950", "1020"}
    assert (tmp_path / "2026-09-11" / "slots_done.json").is_file()
