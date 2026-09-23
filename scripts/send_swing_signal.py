#!/usr/bin/env python3
"""Post swing-opportunity-daily signal summary to Discord.

Usage:
    # Manual send (reads today's existing reports, runs screeners if missing):
    python3 scripts/send_swing_signal.py --manual

    # Launchd mode (checks trading day + dedup, runs screeners if needed):
    python3 scripts/send_swing_signal.py --auto

    # Dry-run (format and print, don't post):
    python3 scripts/send_swing_signal.py --manual --dry-run
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import date, datetime
from glob import glob
from pathlib import Path
from zoneinfo import ZoneInfo

ET = ZoneInfo("America/New_York")
REPO_ROOT = Path(__file__).resolve().parents[1]
REPORTS_DIR = REPO_ROOT / "reports"
STATE_DIR = REPO_ROOT / "state" / "swing_signal"
UNIVERSE_FILE = STATE_DIR / "liquid_pool_universe.txt"
# Consumed by skills/intraday-market-monitor (config watchlist.file). Overwritten daily;
# only its "manual" list survives regeneration.
DAILY_WATCHLIST_FILE = REPO_ROOT / "state" / "daily_watchlist.json"
MAX_DISCORD_CHARS = 1950


def now_et() -> datetime:
    return datetime.now(ET)


def is_trading_day(d: date) -> bool:
    sys.path.insert(0, str(REPO_ROOT))
    try:
        from scripts.market_calendar.market_calendar import session_for_date

        return session_for_date("XNYS", d) is not None
    except Exception:
        return d.weekday() < 5


def _find_report(prefix: str, today_str: str) -> Path | None:
    pattern = str(REPORTS_DIR / f"{prefix}_{today_str}*.json")
    matches = sorted(glob(pattern))
    return Path(matches[-1]) if matches else None


def _build_finviz_universe() -> Path:
    """Build liquid pool universe (source: finviz, price>$20, avg vol>2M, ex-funds)."""
    from finvizfinance.screener.overview import Overview

    foverview = Overview()
    foverview.set_filter(filters_dict={
        "Price": "Over $20",
        "Average Volume": "Over 2M",
        "Industry": "Stocks only (ex-Funds)",
    })
    df = foverview.screener_view()
    tickers = sorted(df["Ticker"].tolist())
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    header = f"# liquid_pool_universe — source: finviz (price>$20, avg_vol>2M, ex-funds)\n"
    UNIVERSE_FILE.write_text(header + "\n".join(tickers) + "\n")
    print(f"  Liquid pool universe: {len(tickers)} tickers (source: finviz)", flush=True)
    return UNIVERSE_FILE


def _get_universe_file() -> Path:
    """Return cached liquid_pool_universe file, or rebuild if stale (>18h old)."""
    if UNIVERSE_FILE.exists():
        age_h = (time.time() - UNIVERSE_FILE.stat().st_mtime) / 3600
        if age_h < 18:
            lines = [l for l in UNIVERSE_FILE.read_text().strip().splitlines() if not l.startswith("#")]
            print(f"  Reusing liquid pool universe ({len(lines)} tickers, {age_h:.1f}h old)", flush=True)
            return UNIVERSE_FILE
    return _build_finviz_universe()


def _run_screener(cmd: list[str], label: str) -> int:
    py = str(REPO_ROOT / ".venv" / "bin" / "python3")
    full = [py] + cmd
    print(f"  Running {label}...", flush=True)
    result = subprocess.run(full, cwd=str(REPO_ROOT), capture_output=True, text=True, timeout=600)
    if result.returncode != 0:
        print(f"  WARNING: {label} failed (rc={result.returncode}): {result.stderr[:200]}")
    return result.returncode


def ensure_reports(today_str: str) -> dict[str, Path | None]:
    """Find or generate today's screener reports."""
    reports = {}

    needs_screener = False
    for prefix in ("vcp_screener", "stockbee_momentum_burst", "stockbee_exhaustion_hammer"):
        if not _find_report(prefix, today_str):
            needs_screener = True
            break

    universe_file = None
    if needs_screener:
        try:
            universe_file = str(_get_universe_file())
        except Exception as exc:
            print(f"  WARNING: finviz universe failed ({exc}), falling back to S&P 500")

    # VCP
    reports["vcp"] = _find_report("vcp_screener", today_str)
    if not reports["vcp"]:
        cmd = [
            str(REPO_ROOT / "skills" / "vcp-screener" / "scripts" / "screen_vcp.py"),
            "--output-dir",
            str(REPORTS_DIR),
        ]
        if universe_file:
            syms = [s for s in Path(universe_file).read_text().strip().splitlines() if not s.startswith("#")]
            cmd += ["--universe"] + syms
        _run_screener(cmd, "VCP screener")
        reports["vcp"] = _find_report("vcp_screener", today_str)

    # Momentum Burst
    reports["mb"] = _find_report("stockbee_momentum_burst", today_str)
    if not reports["mb"]:
        cmd = [
            str(
                REPO_ROOT
                / "skills"
                / "stockbee-momentum-burst-screener"
                / "scripts"
                / "screen_momentum_burst.py"
            ),
            "--output-dir",
            str(REPORTS_DIR),
        ]
        if universe_file:
            cmd += ["--universe-file", universe_file]
        else:
            cmd += ["--polygon-universe"]
        _run_screener(cmd, "Momentum Burst screener")
        reports["mb"] = _find_report("stockbee_momentum_burst", today_str)

    # Exhaustion Hammer
    reports["eh"] = _find_report("stockbee_exhaustion_hammer", today_str)
    if not reports["eh"]:
        cmd = [
            str(
                REPO_ROOT
                / "skills"
                / "stockbee-exhaustion-hammer-screener"
                / "scripts"
                / "screen_exhaustion_hammer.py"
            ),
            "--output-dir",
            str(REPORTS_DIR),
        ]
        if universe_file:
            cmd += ["--universe-file", universe_file]
        else:
            cmd += ["--sp500-universe"]
        _run_screener(cmd, "Exhaustion Hammer screener")
        reports["eh"] = _find_report("stockbee_exhaustion_hammer", today_str)

    # Theme (optional, don't run if missing — it's slow)
    reports["theme"] = _find_report("theme_detector", today_str)

    return reports


def _load_json(path: Path | None) -> dict | None:
    if path and path.exists():
        return json.loads(path.read_text())
    return None


def _candidates(data: dict | None) -> list[dict]:
    if not data:
        return []
    return data.get("candidates", data.get("results", []))


def select_sections(reports: dict[str, Path | None]) -> dict:
    """Pick the rows each Discord section shows. One place, so the message and the
    daily watchlist can never disagree about what was signalled."""
    vcp_rows = _candidates(_load_json(reports.get("vcp")))
    mb_rows = _candidates(_load_json(reports.get("mb")))
    eh_rows = _candidates(_load_json(reports.get("eh")))

    mb_actionable = [c for c in mb_rows if c.get("state", "").startswith("ACTIONABLE")]
    eh_actionable = [c for c in eh_rows if c.get("state", "").startswith("ACTIONABLE")]

    vcp_by = {r["symbol"]: r for r in vcp_rows[:20]}
    mb_by = {c["symbol"]: c for c in mb_rows if c.get("state", "") != "REJECTED"}
    eh_by = {c["symbol"]: c for c in eh_rows if c.get("state", "") != "REJECTED"}

    overlaps = []
    for sym in sorted(set(vcp_by) | set(mb_by) | set(eh_by)):
        sources = []
        if sym in vcp_by:
            sources.append("VCP")
        if sym in mb_by:
            sources.append("MomBurst")
        if sym in eh_by:
            sources.append("ExhHammer")
        if len(sources) >= 2:
            overlaps.append({"symbol": sym, "sources": sources})
    overlaps = overlaps[:6]

    pre_breakout = [r for r in vcp_rows[:15] if r.get("execution_state") == "Pre-breakout"]
    near_pivot = [r for r in pre_breakout if abs(r.get("distance_from_pivot_pct", 99)) < 6][:4]

    return {
        "mb_actionable": mb_actionable,
        "eh_actionable": eh_actionable,
        "overlaps": overlaps,
        "near_pivot": near_pivot,
        "vcp_by": vcp_by,
        "mb_by": mb_by,
        "eh_by": eh_by,
    }


def format_signal(today_str: str, reports: dict[str, Path | None]) -> list[str]:
    """Format screener results into a Discord message."""
    sec = select_sections(reports)

    lines = [f"**Swing Daily Signal** — {today_str}", ""]

    # Momentum Burst
    if sec["mb_actionable"]:
        lines.append("**⚡ 动量爆发 (今日可执行):**")
        for c in sec["mb_actionable"]:
            sym = c["symbol"]
            score = c.get("setup_score", 0)
            rating = c.get("rating", "")
            gain = c.get("day_gain_pct", 0)
            vol_r = c.get("volume_ratio_20d", 0)
            trigger = c.get("primary_trigger", "")
            lines.append(
                f"• {sym} {score}分 {rating} — {trigger}, "
                f"+{gain:.1f}%, 量比{vol_r:.1f}x"
            )
        lines.append("")

    # Exhaustion Hammer
    if sec["eh_actionable"]:
        lines.append("**🔨 衰竭锤反弹 (收盘买入/次日确认):**")
        for c in sec["eh_actionable"]:
            sym = c["symbol"]
            score = c.get("setup_score", 0)
            rating = c.get("rating", "")
            gain = c.get("day_gain_pct", 0)
            trigger = c.get("primary_trigger", "")
            lines.append(f"• {sym} {score}分 {rating} — {trigger}, +{gain:.1f}%")
        lines.append("")

    # Cross-reference
    if sec["overlaps"]:
        lines.append("**🔥 多重信号交叉:**")
        for o in sec["overlaps"]:
            lines.append(f"• {o['symbol']} — {' + '.join(o['sources'])}")
        lines.append("")

    # VCP near-pivot
    if sec["near_pivot"]:
        lines.append("**📊 VCP 接近突破:**")
        for r in sec["near_pivot"]:
            sym = r["symbol"]
            price = r["price"]
            piv = r.get("pivot_proximity", {}).get("pivot_price", 0)
            dist = r.get("distance_from_pivot_pct", 0)
            lines.append(f"• {sym} ${price:.2f} → Pivot ${piv:.2f} ({dist:+.1f}%)")
        lines.append("")

    # Empty check
    if len(lines) <= 2:
        lines.append("今日无显著波段信号。")

    return _split_for_discord("\n".join(lines))


def _score_note(sym: str, sec: dict) -> str:
    """Compact per-screener score/state summary, e.g. 'VCP 61 Pre-breakout + MB 62 WATCH_ONLY'."""
    parts = []
    v = sec["vcp_by"].get(sym)
    if v:
        parts.append(f"VCP {round(v.get('composite_score') or 0)} {v.get('execution_state', '')}")
    m = sec["mb_by"].get(sym)
    if m:
        parts.append(f"MB {m.get('setup_score', 0)} {m.get('state', '')}")
    e = sec["eh_by"].get(sym)
    if e:
        parts.append(f"EH {e.get('setup_score', 0)} {e.get('state', '')}")
    return " + ".join(parts)


def build_watchlist(reports: dict[str, Path | None]) -> list[dict]:
    """Every symbol the Discord message names, with the levels the intraday monitor
    needs: pivot (VCP), stop/entry (VCP stop first, else the screener's stop_reference)."""
    sec = select_sections(reports)
    entries: dict[str, dict] = {}

    def _add(sym: str, source: str) -> None:
        e = entries.setdefault(sym, {"symbol": sym, "sources": []})
        if source not in e["sources"]:
            e["sources"].append(source)

    for c in sec["mb_actionable"]:
        _add(c["symbol"], "momentum_burst")
    for c in sec["eh_actionable"]:
        _add(c["symbol"], "exhaustion_hammer")
    for r in sec["near_pivot"]:
        _add(r["symbol"], "vcp_near_pivot")
    for o in sec["overlaps"]:
        _add(o["symbol"], "cross")

    for sym, e in entries.items():
        v = sec["vcp_by"].get(sym)
        pp = (v or {}).get("pivot_proximity") or {}
        # Only a Pre-breakout pivot is a buy level. An Overextended/Early-post-breakout
        # name keeps its VCP stop for reference but gets no pivot, so the intraday
        # monitor cannot re-trigger a breakout that already happened.
        if pp.get("pivot_price") is not None and v.get("execution_state") == "Pre-breakout":
            e["pivot"] = pp["pivot_price"]
        if pp.get("stop_loss_price") is not None:
            e["stop"] = pp["stop_loss_price"]  # VCP stop wins: it is pattern-based
        else:
            row = sec["mb_by"].get(sym) or sec["eh_by"].get(sym) or {}
            if row.get("entry_reference") is not None:
                e["entry"] = row["entry_reference"]
            if row.get("stop_reference") is not None:
                e["stop"] = row["stop_reference"]
        e["note"] = _score_note(sym, sec)
    return list(entries.values())


def write_daily_watchlist(path: Path, today_str: str, entries: list[dict]) -> Path:
    """Overwrite ``state/daily_watchlist.json``. The screener-derived ``symbols`` list is
    replaced wholesale each run; a hand-maintained ``manual`` list (positions, ad-hoc
    names) is carried over untouched."""
    manual: list = []
    if path.exists():
        try:
            prev = json.loads(path.read_text() or "{}")
            if isinstance(prev, dict) and isinstance(prev.get("manual"), list):
                manual = prev["manual"]
        except ValueError:
            pass
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "date": today_str,
                "generated_at": now_et().isoformat(timespec="seconds"),
                "source": "send_swing_signal",
                "symbols": entries,
                "manual": manual,
            },
            indent=1,
            ensure_ascii=False,
        )
        + "\n"
    )
    return path


def _split_for_discord(text: str) -> list[str]:
    """Split a long message into <=2000-char chunks on blank-line boundaries."""
    if len(text) <= MAX_DISCORD_CHARS:
        return [text]
    chunks: list[str] = []
    current: list[str] = []
    current_len = 0
    for line in text.split("\n"):
        added = len(line) + (1 if current else 0)
        if current_len + added > MAX_DISCORD_CHARS and current:
            chunks.append("\n".join(current))
            current = [line]
            current_len = len(line)
        else:
            current.append(line)
            current_len += added
    if current:
        chunks.append("\n".join(current))
    return chunks


def post_to_discord(content: str, url: str) -> dict:
    """Post message to Discord webhook. Returns status dict."""
    try:
        import requests
    except ImportError:
        return {"posted": False, "error": "requests not installed"}

    delay = 1.0
    for attempt in range(4):
        try:
            resp = requests.post(url, json={"content": content}, timeout=15)
        except Exception as exc:
            if attempt < 3:
                time.sleep(delay)
                delay *= 2
                continue
            return {"posted": False, "error": str(exc)}
        if 200 <= resp.status_code < 300:
            return {"posted": True, "http_status": resp.status_code}
        if resp.status_code == 429 and attempt < 3:
            retry_after = float(resp.headers.get("Retry-After", delay))
            time.sleep(retry_after)
            delay *= 2
            continue
        if resp.status_code < 500:
            return {"posted": False, "http_status": resp.status_code, "error": f"HTTP {resp.status_code}"}
        if attempt < 3:
            time.sleep(delay)
            delay *= 2
    return {"posted": False, "error": "max retries exceeded"}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Post swing daily signal to Discord")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--auto", action="store_true", help="launchd mode: check time + dedup")
    mode.add_argument("--manual", action="store_true", help="send now, skip time check")
    parser.add_argument("--dry-run", action="store_true", help="print message, don't post")
    parser.add_argument(
        "--date", default=None, help="override date (YYYY-MM-DD), default: today ET"
    )
    args = parser.parse_args(argv)

    now = now_et()
    target_date = date.fromisoformat(args.date) if args.date else now.date()
    today_str = target_date.isoformat()

    # Auto mode: check trading day + time window (16:45–17:30 ET)
    if args.auto:
        if not is_trading_day(target_date):
            print(f"{today_str}: not a trading day, skipping")
            return 0
        if not args.date:
            hour, minute = now.hour, now.minute
            t = hour * 60 + minute
            if t < 16 * 60 + 45 or t > 17 * 60 + 30:
                return 0

    # Dedup: check if already sent today
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    sent_file = STATE_DIR / f"{today_str}_sent.json"
    if sent_file.exists() and not args.dry_run:
        print(f"Already sent for {today_str}, skipping")
        return 0

    # Find or run screeners
    print(f"Preparing swing signal for {today_str}...")
    reports = ensure_reports(today_str)

    any_data = any(reports.get(k) for k in ("vcp", "mb", "eh"))
    if not any_data:
        print("No screener data available, skipping")
        return 1

    # Format
    chunks = format_signal(today_str, reports)
    total_chars = sum(len(c) for c in chunks)

    # Hand the signalled names to the intraday monitor for tomorrow's session.
    watchlist = build_watchlist(reports)
    wl_path = write_daily_watchlist(DAILY_WATCHLIST_FILE, today_str, watchlist)
    print(f"Daily watchlist: {len(watchlist)} symbols -> {wl_path}")

    if args.dry_run:
        print("--- DRY RUN ---")
        for i, chunk in enumerate(chunks, 1):
            if len(chunks) > 1:
                print(f"--- message {i}/{len(chunks)} ---")
            print(chunk)
        print(f"--- ({total_chars} chars, {len(chunks)} message(s)) ---")
        return 0

    # Post
    url = os.environ.get("DISCORD_SWING_SIGNAL_URL")
    if not url:
        print("ERROR: DISCORD_SWING_SIGNAL_URL not set", file=sys.stderr)
        return 1

    all_ok = True
    for i, chunk in enumerate(chunks, 1):
        result = post_to_discord(chunk, url)
        print(json.dumps({**result, "part": f"{i}/{len(chunks)}"}))
        if not result["posted"]:
            all_ok = False
            break
        if i < len(chunks):
            time.sleep(0.5)

    if all_ok:
        sent_file.write_text(
            json.dumps({
                "date": today_str,
                "sent_at": now_et().isoformat(),
                "chars": total_chars,
                "parts": len(chunks),
            })
        )

    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
