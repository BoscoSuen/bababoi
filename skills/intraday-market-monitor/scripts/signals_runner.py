"""Glue between the live monitor and signal_engine: gather candidates (daily
watchlist + finviz scans), build the SlotData accessors on top of the Polygon
provider, persist per-session engine state, and hand back rendered lines.

Any failure here is reported in the payload and never blocks the posture message.
"""

from __future__ import annotations

import json
from datetime import date, datetime, timedelta
from pathlib import Path

import _repo_bootstrap  # noqa: F401
import finviz_scans
import signal_engine as se

from scripts.market_data.timeutil import ET


def load_watchlist_entries(path: Path | None) -> dict[str, dict]:
    """``state/daily_watchlist.json`` → symbol → entry. ``manual`` rows become
    positions (HOLD/EXIT) when they carry an entry price, else plain watch names."""
    if not path or not Path(path).is_file():
        return {}
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8") or "{}")
    except ValueError:
        return {}
    out: dict[str, dict] = {}
    for item in data.get("symbols") or []:
        if isinstance(item, dict) and item.get("symbol"):
            out[str(item["symbol"]).upper()] = dict(item)
    for item in data.get("manual") or []:
        if isinstance(item, str):
            out.setdefault(item.upper(), {"symbol": item.upper(), "sources": ["manual"]})
            continue
        if not isinstance(item, dict) or not item.get("symbol"):
            continue
        sym = str(item["symbol"]).upper()
        e = dict(item)
        e.setdefault("sources", ["manual"])
        if e.get("entry_price") or e.get("entry"):
            e["position"] = {
                "entry_price": e.get("entry_price") or e.get("entry"),
                "entry_date": e.get("entry_date"),
                "shares": e.get("shares"),
                "stop": e.get("stop"),
            }
        out[sym] = e
    return out


def state_path(state_dir: Path, session_date: str) -> Path:
    return Path(state_dir) / session_date / "signals.json"


def run(
    provider,
    cfg: dict,
    *,
    session_date: date,
    slot: str,
    until_et: datetime,
    watchlist_path: Path | None,
    state_dir: Path,
    previous_sessions: list[date],
) -> dict:
    sig_cfg = {**se.DEFAULT_CFG, **((cfg.get("signals") or {}).get("thresholds") or {})}
    sdate = session_date.isoformat()
    until_hm = until_et.astimezone(ET).strftime("%H:%M")

    watch = load_watchlist_entries(watchlist_path)
    scan_rows, scan_failed = ([], [])
    live = getattr(provider, "name", "polygon") == "polygon"  # fixture/replay runs never touch finviz
    if live and (cfg.get("signals") or {}).get("scans", True):
        scan_rows, scan_failed = finviz_scans.load_or_run(state_dir, sdate, slot)
    candidates: dict[str, dict] = {s: dict(e) for s, e in watch.items()}
    for r in scan_rows:
        sym = r["symbol"]
        if sym in candidates:
            candidates[sym].setdefault("sector", r.get("sector"))
            candidates[sym].setdefault("industry", r.get("industry"))
        else:
            candidates[sym] = {"symbol": sym, "sources": ["scan"], "sector": r.get("sector"), "industry": r.get("industry")}
    need_sector = [s for s, e in candidates.items() if not e.get("sector")]
    sectors = finviz_scans.lookup_sectors(need_sector, Path(state_dir) / "sectors.json") if (need_sector and live) else {}
    for s, info in sectors.items():
        candidates[s].setdefault("sector", info.get("sector"))
        candidates[s].setdefault("industry", info.get("industry"))

    prevs = list(previous_sessions)
    daily_by_date: dict[date, dict] = {}

    def _daily(d: date) -> dict:
        if d not in daily_by_date:
            try:
                daily_by_date[d] = provider.grouped_daily(d)
            except Exception:
                daily_by_date[d] = {}
        return daily_by_date[d]

    bars_cache: dict[tuple[str, date], list[dict]] = {}

    def _bars(sym: str, d: date, until: datetime) -> list[dict]:
        key = (sym, d)
        if key not in bars_cache:
            try:
                bars_cache[key] = provider.bars_5min(sym, session_date=d.isoformat(), until_et=until)
            except Exception:
                bars_cache[key] = []
        return bars_cache[key]

    def _full_day(d: date) -> datetime:
        return datetime(d.year, d.month, d.day, 16, 0, tzinfo=ET)

    def etf_chg(etf: str) -> float | None:
        b = _bars(etf, session_date, until_et)
        pc = (_daily(prevs[0]).get(etf) or {}).get("close") if prevs else None
        return (b[-1]["c"] / pc - 1) * 100 if b and pc else None

    data = se.SlotData(
        bars=lambda sym: _bars(sym, session_date, until_et),
        hist_bars=lambda sym: [_bars(sym, d, _full_day(d)) for d in prevs[: sig_cfg["history_sessions"]]],
        daily=lambda sym: [_daily(d)[sym] for d in prevs if sym in _daily(d)],
        etf_chg=etf_chg,
        sector=lambda sym: candidates.get(sym) or {},
        until_hm=until_hm,
        session_date=sdate,
    )

    spath = state_path(state_dir, sdate)
    state: dict = {}
    if spath.is_file():
        try:
            state = json.loads(spath.read_text(encoding="utf-8")).get("state") or {}
        except ValueError:
            state = {}
    state, signals = se.evaluate_slot(state, slot=slot, candidates=candidates, data=data, cfg=sig_cfg)
    spath.parent.mkdir(parents=True, exist_ok=True)
    spath.write_text(json.dumps({"session_date": sdate, "slot": slot, "state": state}, indent=1), encoding="utf-8")

    return {
        "rows": signals,
        "lines": se.render_lines(signals),
        "candidates": len(candidates),
        "scan": {"n": len(scan_rows), "failed": scan_failed},
        "state_path": str(spath),
    }


def previous_trading_days(session_date: date, n: int, is_session) -> list[date]:
    """Calendar-aware prior sessions (helper for callers without intraday_monitor)."""
    out: list[date] = []
    d = session_date - timedelta(days=1)
    guard = 0
    while len(out) < n and guard < n * 4 + 20:
        if is_session(d):
            out.append(d)
        d -= timedelta(days=1)
        guard += 1
    return out
