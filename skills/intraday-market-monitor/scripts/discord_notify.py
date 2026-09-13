"""Discord webhook notifier. Never raises; returns a status dict for the report."""

from __future__ import annotations

import os
import time
from typing import Any

WEBHOOK_ENV = "DISCORD_WEBHOOK_URL"
MAX_CHARS = 1900


def webhook_url() -> str | None:
    return os.environ.get(WEBHOOK_ENV) or None


def _fmt(x, digits=1, suffix="") -> str:
    if x is None:
        return "n/a"
    if isinstance(x, (int, float)) and not isinstance(x, bool):
        return f"{x:.{digits}f}{suffix}"
    return str(x)


def format_summary(p: dict, *, max_chars: int = MAX_CHARS) -> str:
    post = p["posture"]
    b = p["metrics"]["breadth"]
    idx = p["metrics"]["index"]
    sec = p["metrics"]["sectors"]
    slot = f"{p['run_slot'][:2]}:{p['run_slot'][2:]}"
    asof = (p.get("data_asof") or "")[11:16]
    head = f"**Intraday Monitor** {p['session_date']} {slot} ET  (data as of {asof}, {p['delay_minutes']}m delayed)"
    flip = f"  ⇐ flipped from {post['flipped_from']}" if post.get("flipped_from") else ""
    pend = f"  (pending → {post['pending_flip']})" if post.get("pending_flip") else ""
    lines = [f"Posture : {p['recommendation']}  score {_fmt(post.get('score'))}{flip}{pend}"]
    if b.get("available"):
        lines.append(
            f"Breadth : adv {_fmt(b['pct_advancers'], 0, '%')} | >VWAP {_fmt(b['pct_above_vwap'], 0, '%')} | "
            f"U/D {_fmt(b['ud_ratio'], 2)} | pace {_fmt(b['volume_pace'], 2)} | n={b['universe_size']}"
        )
    parts = []
    for sym, s in idx.items():
        if s.get("available"):
            parts.append(
                f"{sym} {_fmt(s['ret_open_pct'], 2, '%')} {'↑VWAP' if s['above_vwap'] else '↓VWAP'}"
            )
    if parts:
        lines.append("Index   : " + " | ".join(parts))
    if sec.get("available") and sec["sectors"]:
        top = ", ".join(f"{r['symbol']} {_fmt(r['rs_open_pct'], 2)}" for r in sec["sectors"][:3])
        bot = ", ".join(f"{r['symbol']} {_fmt(r['rs_open_pct'], 2)}" for r in sec["sectors"][-3:])
        lines.append(
            f"Sectors : top {top} / bottom {bot} | risk-on spread {_fmt(sec.get('risk_on_spread_pct'), 2)}"
        )
    sigs = [
        f"{w['symbol']} {'+'.join(w['signals'])}"
        for w in p.get("watchlist_signals") or []
        if w.get("signals")
    ]
    lines.append("Signals : " + (", ".join(sigs) if sigs else "none"))
    body = head + "\n```\n" + "\n".join(lines) + "\n```"
    if len(body) > max_chars:
        body = body[: max_chars - 4] + "…```"
    return body


def post(
    content: str,
    *,
    url: str | None = None,
    session: Any = None,
    retries: int = 3,
    sleep=time.sleep,
    timeout: float = 15.0,
) -> dict:
    url = url or webhook_url()
    if not url:
        return {"posted": False, "http_status": None, "error": f"{WEBHOOK_ENV} not set"}
    if session is None:
        try:
            import requests

            session = requests.Session()
        except ImportError:  # pragma: no cover
            return {"posted": False, "http_status": None, "error": "requests not installed"}
    delay = 1.0
    error = None
    for attempt in range(retries + 1):
        try:
            resp = session.post(url, json={"content": content}, timeout=timeout)
        except Exception as exc:  # network failure
            error = str(exc).replace(url, "<webhook>")
            resp = None
        if resp is not None:
            status = getattr(resp, "status_code", 0)
            if 200 <= status < 300:
                return {"posted": True, "http_status": status, "error": None}
            error = f"HTTP {status}"
            if status == 429:
                try:
                    retry_after = float(resp.headers.get("Retry-After", delay))
                except (TypeError, ValueError, AttributeError):
                    retry_after = delay
                if attempt < retries:
                    sleep(retry_after)
                    delay *= 2
                    continue
            elif status < 500:
                return {"posted": False, "http_status": status, "error": error}
        if attempt < retries:
            sleep(delay)
            delay *= 2
    return {"posted": False, "http_status": None, "error": error or "unknown"}
