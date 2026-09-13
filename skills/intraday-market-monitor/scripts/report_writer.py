"""JSON + Markdown writers for one monitor run."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

SCHEMA_VERSION = 1


def write_json(payload: dict, out_dir: Path, session_date: str, slot: str) -> Path:
    day_dir = Path(out_dir) / session_date
    day_dir.mkdir(parents=True, exist_ok=True)
    path = day_dir / f"intraday_{slot}.json"
    path.write_text(
        json.dumps(payload, indent=1, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8"
    )
    latest = Path(out_dir) / "latest.json"
    shutil.copyfile(path, latest)
    return path


def write_markdown(payload: dict, out_dir: Path, session_date: str, slot: str) -> Path:
    path = Path(out_dir) / session_date / f"intraday_{slot}.md"
    path.write_text(render_markdown(payload), encoding="utf-8")
    return path


def _fmt(x, digits=1, suffix="") -> str:
    if x is None:
        return "n/a"
    if isinstance(x, bool):
        return "yes" if x else "no"
    if isinstance(x, (int, float)):
        return f"{x:.{digits}f}{suffix}"
    return str(x)


def render_markdown(p: dict) -> str:
    post = p["posture"]
    b = p["metrics"]["breadth"]
    idx = p["metrics"]["index"]
    sec = p["metrics"]["sectors"]
    lines = [
        f"# Intraday Market Monitor — {p['session_date']} {p['run_slot'][:2]}:{p['run_slot'][2:]} ET",
        "",
        f"- **Data as of:** {p['data_asof']} ({p['delay_minutes']}-minute delayed feed)",
        f"- **Provider:** {p['provider']}",
        f"- **Recommendation:** **{p['recommendation']}** (score {_fmt(post.get('score'))})",
    ]
    if post.get("flipped_from"):
        lines.append(f"- **Flipped from:** {post['flipped_from']}")
    if post.get("pending_flip"):
        lines.append(
            f"- Pending flip toward: {post['pending_flip']} (needs confirmation next slot)"
        )
    if post.get("capped_by_daily"):
        lines.append(f"- Capped by daily posture: {p['daily_baseline'].get('recommendation')}")
    lines += ["- Reasons: " + ", ".join(post.get("reason_codes") or []), "", "## Breadth", ""]
    if b.get("available"):
        lines += [
            "| Metric | Value |",
            "|---|---|",
            f"| Universe | {b['universe_size']} |",
            f"| Advancers | {_fmt(b['pct_advancers'], 1, '%')} |",
            f"| Above day VWAP | {_fmt(b['pct_above_vwap'], 1, '%')} |",
            f"| Above prev high | {_fmt(b['pct_above_prev_high'], 1, '%')} |",
            f"| Below prev low | {_fmt(b['pct_below_prev_low'], 1, '%')} |",
            f"| Up/Down volume | {_fmt(b['ud_ratio'], 2)} |",
            f"| Volume pace vs 20d | {_fmt(b['volume_pace'], 2)} |",
        ]
    else:
        lines.append("_Breadth unavailable this run._")
    lines += ["", "## Index", ""]
    for sym, s in idx.items():
        if not s.get("available"):
            lines.append(f"- {sym}: unavailable")
            continue
        lines.append(
            f"- **{sym}** {_fmt(s['last'], 2)} | vs open {_fmt(s['ret_open_pct'], 2, '%')} | "
            f"{'above' if s['above_vwap'] else 'below'} VWAP {_fmt(s['vwap'], 2)} | "
            f"prev high {'broken' if s['above_prev_high'] else 'intact'} | "
            f"prev low {'broken' if s['below_prev_low'] else 'intact'}"
        )
    lines += ["", "## Sector relative strength vs " + str(sec.get("benchmark")), ""]
    if sec.get("available"):
        lines += [
            "| Rank | ETF | vs open | RS open | RS last hour | >VWAP |",
            "|---|---|---|---|---|---|",
        ]
        for r in sec["sectors"]:
            lines.append(
                f"| {r['rank']} | {r['symbol']} | {_fmt(r['ret_open_pct'], 2, '%')} | "
                f"{_fmt(r['rs_open_pct'], 2, '%')} | {_fmt(r['rs_last_hour_pct'], 2, '%')} | {_fmt(r['above_vwap'])} |"
            )
        lines.append("")
        lines.append(f"Risk-on spread: {_fmt(sec.get('risk_on_spread_pct'), 2, '%')}")
    lines += ["", "## Watchlist signals (last closed hour bar)", ""]
    ws = p.get("watchlist_signals") or []
    if not ws:
        lines.append("_No watchlist symbols._")
    for w in ws:
        sig = ", ".join(w.get("signals") or []) or "—"
        lines.append(
            f"- **{w['symbol']}**: {sig} | hourly close {_fmt(w.get('hourly_close'), 2)} | "
            f"VWAP {_fmt(w.get('vwap'), 2)} | FHR {_fmt(w.get('fhr_low'), 2)}–{_fmt(w.get('fhr_high'), 2)} | "
            f"gap {_fmt(w.get('gap_pct'), 2, '%')} | rel vol {_fmt(w.get('rel_vol'), 2)}"
        )
    lines += [
        "",
        "---",
        "_Not a trade signal. Posture is a ceiling on new risk; execution decisions stay with the trader._",
        "",
    ]
    return "\n".join(lines)
