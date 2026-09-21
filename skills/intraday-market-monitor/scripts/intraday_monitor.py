#!/usr/bin/env python3
"""Intraday Market Monitor — hourly, deterministic posture + signals on delayed data.

Usage::

    intraday_monitor.py run --auto-slot                 # launchd entry point
    intraday_monitor.py run --slot 1020 [--now-et ISO]  # explicit slot (replayable)
    intraday_monitor.py run --slot 1020 --provider fixture --fixture-dir DIR --no-discord
    intraday_monitor.py discord-test                    # one-line webhook ping
    intraday_monitor.py replay --date 2026-09-11        # re-run every slot from cache

Exit codes: 0 success / nothing to do (non-session day, slot already done),
1 hard failure (provider unusable), 2 missing runtime dependency.
"""

from __future__ import annotations

import argparse
import copy
import json
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

import _repo_bootstrap  # noqa: F401
from _repo_bootstrap import REPO_ROOT

try:
    import yaml
except ImportError:  # pragma: no cover
    print(
        "ERROR: pyyaml is required (see skills/intraday-market-monitor/requirements.txt)",
        file=sys.stderr,
    )
    sys.exit(2)

import breadth_metrics
import discord_notify
import narrative
import posture as posture_mod
import report_writer
import sector_rs
import watchlist_signals
from run_slots import SlotLedger, due_slots, resolve_auto_slot, slot_time, until_for

from scripts.market_calendar.market_calendar import CalendarUnavailableError, session_for_date
from scripts.market_data import get_provider
from scripts.market_data.provider import NotAvailable, ProviderError
from scripts.market_data.timeutil import ET, now_et, parse_ts_et

SKILL_DIR = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = SKILL_DIR / "config" / "default.yaml"
SKILL_ID = "intraday-market-monitor"


# ----------------------------------------------------------------- config
def _deep_merge(base: dict, override: dict) -> dict:
    out = copy.deepcopy(base)
    for k, v in (override or {}).items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _deep_merge(out[k], v)
        else:
            out[k] = v
    return out


def load_config(path: Path | None = None) -> dict:
    cfg = yaml.safe_load(DEFAULT_CONFIG.read_text(encoding="utf-8")) or {}
    if path:
        cfg = _deep_merge(cfg, yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {})
    return cfg


# --------------------------------------------------------------- sessions
def session_bounds_or_none(session_date: date) -> tuple[datetime, datetime] | None:
    try:
        session = session_for_date("XNYS", session_date)
    except CalendarUnavailableError as exc:
        print(f"ERROR: exchange calendar unavailable: {exc}", file=sys.stderr)
        sys.exit(2)
    if session is None:
        return None
    return session.market_open.astimezone(ET), session.market_close.astimezone(ET)


def previous_sessions(session_date: date, n: int) -> list[date]:
    out: list[date] = []
    d = session_date - timedelta(days=1)
    guard = 0
    while len(out) < n and guard < n * 4 + 20:
        if session_bounds_or_none(d) is not None:
            out.append(d)
        d -= timedelta(days=1)
        guard += 1
    return out


# --------------------------------------------------------------- provider
def build_provider(args: argparse.Namespace, cfg: dict):
    name = args.provider or cfg["provider"]["name"]
    if name == "fixture":
        return get_provider("fixture", fixture_dir=args.fixture_dir)
    return get_provider("polygon", api_key=args.api_key, use_cache=not args.no_cache)


# ----------------------------------------------------------------- collect
def collect(
    provider,
    cfg: dict,
    *,
    session_date: date,
    slot: str,
    until_et: datetime,
    session_open: datetime,
    session_close: datetime,
    watchlist: list[str],
    watchlist_levels: dict[str, dict] | None = None,
) -> dict:
    """Pull everything for one slot and compute all metrics (pure given the provider)."""
    watchlist_levels = watchlist_levels or {}
    sec_cfg = cfg["sectors"]
    etfs = list(dict.fromkeys(sec_cfg["core"] + sec_cfg["spdr"] + sec_cfg["risk_gauges"]))
    warnings: list[str] = []

    # 1. Breadth from one all-tickers snapshot.
    breadth: dict = {"available": False}
    snap_by: dict[str, dict] = {}
    try:
        rows = provider.snapshot(replay_key=f"{session_date.isoformat()}:{slot}")
        snap_by = {r["symbol"]: r for r in rows if r.get("symbol")}
        universe = breadth_metrics.filter_universe(
            rows,
            symbol_regex=cfg["universe"]["symbol_regex"],
            min_prev_close=cfg["universe"]["min_prev_close"],
            min_prev_volume=cfg["universe"]["min_prev_volume"],
        )
        elapsed = breadth_metrics.elapsed_fraction(
            until_et, session_open, session_close, cfg["volume_curve"]
        )
        avg_vol: dict[str, float] | None = None
        try:
            days = previous_sessions(session_date, int(cfg["universe"]["avg_volume_sessions"]))
            grouped = [provider.grouped_daily(d) for d in days]
            avg_vol = breadth_metrics.avg_volume_by_symbol(grouped) if grouped else None
        except ProviderError as exc:
            warnings.append(f"avg volume unavailable: {exc}")
        breadth = breadth_metrics.compute_breadth(universe, avg_volume=avg_vol, elapsed=elapsed)
    except ProviderError as exc:
        warnings.append(f"snapshot unavailable: {exc}")
        elapsed = breadth_metrics.elapsed_fraction(
            until_et, session_open, session_close, cfg["volume_curve"]
        )
        avg_vol = None
        try:  # degrade: snapshot only the symbols we need for prev-day levels
            rows = provider.snapshot(
                etfs + watchlist, replay_key=f"{session_date.isoformat()}:{slot}"
            )
            snap_by = {r["symbol"]: r for r in rows if r.get("symbol")}
        except ProviderError as exc2:
            warnings.append(f"filtered snapshot unavailable: {exc2}")

    # 2. 5-minute bars for ETFs and watchlist.
    def _bars(sym: str) -> list[dict]:
        try:
            return provider.bars_5min(sym, session_date=session_date.isoformat(), until_et=until_et)
        except NotAvailable:
            warnings.append(f"{sym}: not available on this plan")
        except ProviderError as exc:
            warnings.append(f"{sym}: bars failed: {exc}")
        return []

    etf_bars = {sym: _bars(sym) for sym in etfs}
    from scripts.market_data.symbols import to_polygon

    def _prev(sym: str) -> dict | None:
        try:
            key = to_polygon(sym)[0]
        except (NotAvailable, ValueError):
            key = sym
        return (snap_by.get(key) or {}).get("prev_day")

    index = {
        sym: sector_rs.index_state(etf_bars.get(sym) or [], _prev(sym), session_close=session_close)
        for sym in sec_cfg["core"]
    }
    sectors = sector_rs.compute_sector_rs(
        {
            s: b
            for s, b in etf_bars.items()
            if s in sec_cfg["spdr"]
            or s in sec_cfg["risk_gauges"]
            or s == sec_cfg["benchmark"]
            or s in sec_cfg["core"]
        },
        benchmark=sec_cfg["benchmark"],
        risk_on=sec_cfg["risk_on"],
        risk_off=sec_cfg["risk_off"],
        session_close=session_close,
    )
    wl = []
    for sym in watchlist:
        bars = _bars(sym)
        poly = to_polygon(sym)[0] if sym.upper() not in ("^VIX",) else sym
        wl.append(
            watchlist_signals.evaluate_symbol(
                sym,
                bars,
                prev_day=_prev(sym),
                avg_volume=(avg_vol or {}).get(poly) if avg_vol else None,
                elapsed=elapsed,
                session_open=session_open,
                session_close=session_close,
                rel_vol_breakout_min=cfg["watchlist"]["rel_vol_breakout_min"],
                gap_min_pct=cfg["watchlist"]["gap_min_pct"],
                pivot=(watchlist_levels.get(sym) or {}).get("pivot"),
                stop=(watchlist_levels.get(sym) or {}).get("stop"),
            )
        )
    return {
        "breadth": breadth,
        "index": index,
        "sectors": sectors,
        "watchlist": wl,
        "warnings": warnings,
    }


# --------------------------------------------------------------------- run
def run_slot(
    args: argparse.Namespace, cfg: dict, *, slot: str, now: datetime, provider=None
) -> int:
    session_date = now.date()
    bounds = session_bounds_or_none(session_date)
    if bounds is None:
        print(f"{session_date}: not an XNYS session; nothing to do")
        return 0
    session_open, session_close = bounds
    state_dir = Path(args.state_dir)
    out_dir = Path(args.output_dir)
    ledger = SlotLedger(state_dir, session_date)
    if slot in ledger.load() and not args.force:
        print(f"{session_date} {slot}: already ran (use --force to repeat)")
        return 0

    nominal = slot_time(session_date, slot)
    until_et = min(
        until_for(nominal, delay_minutes=int(cfg["provider"]["delay_minutes"])), session_close
    )
    provider = provider or build_provider(args, cfg)

    watchlist_path = Path(cfg["watchlist"]["file"])
    if not watchlist_path.is_absolute():
        watchlist_path = REPO_ROOT / watchlist_path
    vcp_json = Path(args.vcp_json) if args.vcp_json else None
    watchlist = watchlist_signals.load_watchlist(
        watchlist_path, vcp_json=vcp_json, vcp_min_rating=cfg["watchlist"]["vcp_min_rating"]
    )
    watchlist_levels = watchlist_signals.load_watchlist_levels(watchlist_path)

    metrics = collect(
        provider,
        cfg,
        session_date=session_date,
        slot=slot,
        until_et=until_et,
        session_open=session_open,
        session_close=session_close,
        watchlist=watchlist,
        watchlist_levels=watchlist_levels,
    )

    # Posture.
    pcfg = cfg["posture"]
    parts = {
        "breadth": posture_mod.breadth_score(metrics["breadth"]),
        "index": posture_mod.index_score(
            [metrics["index"].get(s, {}) for s in cfg["sectors"]["core"][:2]]
        ),
        "sector": posture_mod.sector_score(metrics["sectors"]),
    }
    score = posture_mod.composite(parts, pcfg["weights"])
    spy_state = metrics["index"].get(cfg["sectors"]["benchmark"], {})
    candidate, reasons = posture_mod.recommend(score, metrics["breadth"], spy_state, pcfg)
    state_store = posture_mod.PostureState(state_dir)
    prev_state = state_store.load(session_date.isoformat())
    hyst = posture_mod.apply_hysteresis(candidate, score, prev_state, pcfg)
    baseline = posture_mod.load_daily_baseline(pcfg["daily_baseline_glob"], REPO_ROOT)
    final, capped = posture_mod.apply_daily_cap(
        hyst["recommendation"], (baseline or {}).get("recommendation"), int(pcfg["daily_cap_steps"])
    )
    if capped:
        reasons = reasons + ["capped_by_daily_baseline"]

    # data_asof is the bar horizon every metric was computed through; the
    # snapshot's own update time is reported separately (it can trail or, after
    # the close, run ahead of the horizon).
    data_asof = until_et.isoformat()
    snapshot_asof = provider.data_asof() if hasattr(provider, "data_asof") else None
    payload = {
        "schema_version": report_writer.SCHEMA_VERSION,
        "skill": SKILL_ID,
        "session_date": session_date.isoformat(),
        "run_slot": slot,
        "next_slot": next((s for s in cfg["slots"] if s > slot), None),
        "run_at_utc": (
            now.isoformat() if getattr(args, "now_et", None) else datetime.now(tz=ET).isoformat()
        ),
        "data_asof": data_asof,
        "data_horizon_et": until_et.isoformat(),
        "snapshot_asof": snapshot_asof,
        "delay_minutes": int(cfg["provider"]["delay_minutes"]),
        "provider": getattr(provider, "name", "polygon"),
        "recommendation": final,
        "posture": {
            "recommendation": final,
            "candidate": candidate,
            "score": score,
            "component_scores": parts,
            "reason_codes": reasons,
            "flipped_from": hyst.get("flipped_from"),
            "pending_flip": hyst.get("pending_flip"),
            "streak": hyst.get("streak"),
            "capped_by_daily": capped,
        },
        "metrics": {
            "breadth": metrics["breadth"],
            "index": metrics["index"],
            "sectors": metrics["sectors"],
        },
        "watchlist_symbols": watchlist,
        "watchlist_signals": metrics["watchlist"],
        "daily_baseline": baseline,
        "warnings": metrics["warnings"],
        "api_stats": provider.stats() if hasattr(provider, "stats") else {},
        "narrative": {"requested": False, "written": False, "path": None, "error": None},
        "discord": {"posted": False, "http_status": None, "error": None},
    }

    # Persist state before side effects so a crash mid-notify does not re-run.
    state_store.save(
        {
            "session_date": session_date.isoformat(),
            "run_slot": slot,
            "recommendation": final,
            "score": score,
            "streak": hyst.get("streak"),
            "pending_flip": hyst.get("pending_flip"),
            "pending_count": hyst.get("pending_count", 0),
        }
    )
    ledger.mark(slot)

    # Discord.
    if cfg["discord"]["enabled"] and not args.no_discord:
        payload["discord"] = discord_notify.post(
            discord_notify.format_summary(payload, max_chars=int(cfg["discord"]["max_chars"]))
        )

    # Narrative.
    mode = args.narrative or cfg["narrative"]["mode"]
    flipped = bool(hyst.get("flipped_from"))
    if narrative.should_run(mode, slot, list(cfg["narrative_slots"]), flipped):
        previous = _previous_payload(out_dir, session_date.isoformat(), slot, list(cfg["slots"]))
        prompt = narrative.build_prompt(payload, previous, baseline)
        payload["narrative"] = narrative.run_claude(
            prompt,
            out_dir / session_date.isoformat() / f"narrative_{slot}.md",
            claude_bin=cfg["narrative"]["claude_bin"],
            timeout=float(cfg["narrative"]["timeout_seconds"]),
        )
        if (
            payload["narrative"].get("written")
            and cfg["discord"]["enabled"]
            and not args.no_discord
        ):
            text = Path(payload["narrative"]["path"]).read_text(encoding="utf-8")
            discord_notify.post(text[: int(cfg["discord"]["max_chars"])])

    json_path = report_writer.write_json(payload, out_dir, session_date.isoformat(), slot)
    report_writer.write_markdown(payload, out_dir, session_date.isoformat(), slot)
    print(
        f"{session_date} {slot}: {final} (score {score}) data_asof={data_asof} "
        f"discord={'ok' if payload['discord']['posted'] else 'skipped/failed'} -> {json_path}"
    )
    for w in metrics["warnings"]:
        print(f"WARN: {w}", file=sys.stderr)
    return 0


def _previous_payload(out_dir: Path, session_date: str, slot: str, slots: list[str]) -> dict | None:
    earlier = [s for s in slots if s < slot]
    for s in reversed(earlier):
        p = Path(out_dir) / session_date / f"intraday_{s}.json"
        if p.is_file():
            try:
                return json.loads(p.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                return None
    return None


# --------------------------------------------------------------------- CLI
def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    sub = p.add_subparsers(dest="command", required=True)

    def common(sp):
        sp.add_argument(
            "--config", type=Path, default=None, help="YAML overriding config/default.yaml"
        )
        sp.add_argument("--provider", choices=["polygon", "fixture"], default=None)
        sp.add_argument(
            "--fixture-dir", default=None, help="cache-layout directory for --provider fixture"
        )
        sp.add_argument(
            "--api-key", default=None, help="Polygon API key (default: POLYGON_API_KEY)"
        )
        sp.add_argument("--no-cache", action="store_true", help="bypass the on-disk provider cache")
        sp.add_argument("--output-dir", default=str(REPO_ROOT / "reports" / "intraday"))
        sp.add_argument("--state-dir", default=str(REPO_ROOT / "state" / "intraday"))
        sp.add_argument(
            "--vcp-json", default=None, help="vcp_screener_*.json whose A/B rows join the watchlist"
        )
        sp.add_argument("--no-discord", action="store_true")
        sp.add_argument("--narrative", choices=["auto", "always", "never"], default=None)
        sp.add_argument("--force", action="store_true", help="re-run a slot already in the ledger")

    r = sub.add_parser("run", help="run one slot")
    common(r)
    g = r.add_mutually_exclusive_group(required=True)
    g.add_argument("--slot", help="HHMM ET slot, e.g. 1020")
    g.add_argument("--auto-slot", action="store_true", help="latest due slot not yet run")
    r.add_argument(
        "--now-et", default=None, help="ISO timestamp overriding the wall clock (replay/tests)"
    )

    rp = sub.add_parser("replay", help="re-run every slot of a past session from cache")
    common(rp)
    rp.add_argument("--date", required=True)

    d = sub.add_parser("discord-test", help="post a one-line ping to DISCORD_MARKET_REPORT_URL")
    d.add_argument("--message", default=None)
    return p


def _now(args: argparse.Namespace) -> datetime:
    if getattr(args, "now_et", None):
        return (
            parse_ts_et(args.now_et)
            if "T" in args.now_et
            else datetime.fromisoformat(args.now_et).replace(tzinfo=ET)
        )
    return now_et()


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "discord-test":
        msg = (
            args.message or f"intraday-market-monitor ping {now_et().isoformat(timespec='seconds')}"
        )
        result = discord_notify.post(msg)
        print(json.dumps(result))
        return 0 if result["posted"] else 1
    cfg = load_config(args.config)
    if args.command == "replay":
        session_date = date.fromisoformat(args.date)
        args.force = True
        args.no_discord = True
        args.narrative = args.narrative or "never"
        rc = 0
        for slot in cfg["slots"]:
            rc |= run_slot(args, cfg, slot=slot, now=slot_time(session_date, slot))
        return rc
    now = _now(args)
    if args.auto_slot:
        session_date = now.date()
        if session_bounds_or_none(session_date) is None:
            print(f"{session_date}: not an XNYS session; nothing to do")
            return 0
        ledger = SlotLedger(Path(args.state_dir), session_date)
        done = ledger.load()
        slot = resolve_auto_slot(now, done, tuple(cfg["slots"]))
        if slot is None:
            print(f"{now.isoformat(timespec='minutes')}: no due slot pending")
            return 0
        # Catch-up runs only the latest pending slot; older missed slots are
        # recorded as skipped so the next fire does not replay stale hours.
        skipped = [s for s in due_slots(now, tuple(cfg["slots"])) if s < slot and s not in done]
        if skipped:
            ledger.mark_many(skipped)
            print(f"{session_date}: skipping missed slots {', '.join(skipped)}")
    else:
        slot = args.slot
        if slot not in cfg["slots"]:
            print(f"ERROR: unknown slot {slot}; valid: {', '.join(cfg['slots'])}", file=sys.stderr)
            return 1
    try:
        return run_slot(args, cfg, slot=slot, now=now)
    except ValueError as exc:  # missing key etc.
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
