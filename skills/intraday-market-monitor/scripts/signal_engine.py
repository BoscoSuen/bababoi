"""Tiered intraday buy/hold/exit signals for the watchlist + finviz scan names.

Pure evaluation: all market data comes in through ``SlotData`` callables, so the
launchd monitor and the offline replay (calpico scan snapshots + Polygon cache)
run exactly the same code.

Signal kinds
  PIVOT  watchlist name with a VCP pivot (Pre-breakout only)
  MB     Stockbee momentum burst, day 1 (scan names or pivot-less watchlist names)
  EH     exhaustion-hammer next-day confirmation (watchlist ``exhaustion_hammer``)
  POS    a held position from ``daily_watchlist.json`` → ``manual`` (HOLD / EXIT only)

Tiers are evidence counts that accumulate across slots (state persisted per
session), so the first slot a name triggers is usually 🟢 and 🟢🟢🟢 needs the
name to keep holding. Nothing here gates on market posture by design.
"""

from __future__ import annotations

import statistics
from dataclasses import dataclass, field
from datetime import datetime
from typing import Callable

import _repo_bootstrap  # noqa: F401

from scripts.market_data.timeutil import cumulative_vwap

DEFAULT_CFG: dict = {
    "min_price": 20.0,
    "history_sessions": 20,  # same-time volume baseline
    "min_history": 8,
    "vol_pct_trigger": 90.0,  # today's same-time volume percentile vs baseline
    "vol_ratio_trigger": 1.5,  # ... or ratio vs baseline median
    "vol_pct_strong": 100.0,  # E2: today is the busiest of the last 20 sessions at this time
    "pivot_chase_pct": 2.0,  # Minervini: never chase > 2% above pivot
    "pivot_stop_pct": 5.0,  # stop = max(contraction low − 1%, pivot − 5%)
    "pivot_fall_pct": 0.5,  # confirmed close this far under pivot → back to armed
    "pivot_armed_max_pct": 5.0,  # over the pivot by more than this = breakout already gone, not even armed
    "mb_min_gain_pct": 4.0,
    "mb_max_gain_pct": 10.0,
    "mb_min_from_open_pct": 2.0,
    "mb_max_risk_pct": 5.0,  # distance to day low
    "mb_prior_day_max_pct": 4.0,  # no single > +4% day in the prior 3 sessions
    "rs_pct": 4.0,  # E4: outperform sector ETF by this much
    "close_loc": 0.70,  # E3
    "ext_atr_mult": 2.0,  # E5: not above SMA20 + 2·ATR
    "theme_min": 3,  # E7: this many same-industry names live (incl. self)
    "vwap_bars": 6,  # "above VWAP" = ≥4 of the last 6 five-minute closes
    "vwap_bars_min_above": 4,
    "below_vwap_slots": 2,  # consecutive slots below VWAP before a demotion
    "shakeout_vol_ratio": 0.8,  # dip below VWAP on < 0.8× session 5-min volume → not counted
}

SECTOR_ETF = {
    "Technology": "XLK",
    "Communication Services": "XLC",
    "Healthcare": "XLV",
    "Financial": "XLF",
    "Consumer Cyclical": "XLY",
    "Consumer Defensive": "XLP",
    "Industrials": "XLI",
    "Energy": "XLE",
    "Basic Materials": "XLB",
    "Utilities": "XLU",
    "Real Estate": "XLRE",
}

TIER_ICON = {0: "⚪", 1: "🟢", 2: "🟢🟢", 3: "🟢🟢🟢"}


@dataclass
class SlotData:
    """Data access for one slot. Every callable may return ``[]``/``None`` on failure."""

    bars: Callable[[str], list[dict]]  # today's confirmed 5-min bars through the data horizon
    hist_bars: Callable[[str], list[list[dict]]]  # prior sessions' full-day 5-min bars, newest first
    daily: Callable[[str], list[dict]]  # prior sessions' daily rows newest first: close/high/low/volume
    etf_chg: Callable[[str], float | None]  # sector ETF % change vs prev close at the horizon
    sector: Callable[[str], dict]  # {"sector":..., "industry":...}
    until_hm: str = "16:00"  # HH:MM ET data horizon
    session_date: str = ""
    extra: dict = field(default_factory=dict)


# ----------------------------------------------------------------- indicators
def daily_context(rows: list[dict]) -> dict | None:
    """SMA20 / ATR14 / prior-3-day changes from daily rows (newest first, ≥16 rows)."""
    if len(rows) < 16:
        return None
    closes = [r["close"] for r in rows]
    sma20 = sum(closes[:20]) / min(20, len(closes))
    trs = []
    for i in range(14):
        h, lo, pc = rows[i]["high"], rows[i]["low"], rows[i + 1]["close"]
        trs.append(max(h - lo, abs(h - pc), abs(lo - pc)))
    chg3 = [(rows[i]["close"] / rows[i + 1]["close"] - 1) * 100 for i in range(3)]
    return {"sma20": sma20, "atr": sum(trs) / 14, "chg3": chg3, "prev_close": closes[0], "prev_low": rows[0]["low"]}


def same_time_volume(today: list[dict], hist: list[list[dict]], until_hm: str, cfg: dict) -> tuple[float, float] | None:
    """(ratio vs median, percentile) of today's cumulative volume through ``until_hm``
    against the same clock time on prior sessions. Scale-free per symbol, so a name
    that has been busy for two weeks is judged against its own busy baseline."""
    today_v = sum(b["v"] for b in today if b["ts_et"][11:16] <= until_hm)
    base = [sum(b["v"] for b in bb if b["ts_et"][11:16] <= until_hm) for bb in hist if bb]
    base = [v for v in base if v]
    if not today_v or len(base) < cfg["min_history"]:
        return None
    med = statistics.median(base)
    pct = sum(1 for v in base if v < today_v) / len(base) * 100
    return (today_v / med if med else 0.0, pct)


def snapshot(bars: list[dict], ctx: dict, cfg: dict) -> dict | None:
    if len(bars) < 3:
        return None
    vw = cumulative_vwap(bars)
    last = bars[-1]["c"]
    n = cfg["vwap_bars"]
    tail = bars[-n:]
    above = sum(1 for b, v in zip(tail, vw[-len(tail):]) if b["c"] > v)
    hi, lo = max(b["h"] for b in bars), min(b["l"] for b in bars)
    # volume on the bars that closed below VWAP in this window vs the session's 5-min average
    sess_avg = sum(b["v"] for b in bars) / len(bars)
    below_bars = [b for b, v in zip(tail, vw[-len(tail):]) if b["c"] <= v]
    dip_vol = (sum(b["v"] for b in below_bars) / len(below_bars) / sess_avg) if below_bars and sess_avg else 0.0
    return {
        "last": last,
        "chg": (last / ctx["prev_close"] - 1) * 100,
        "from_open": (last / bars[0]["o"] - 1) * 100,
        "above_vwap": above >= cfg["vwap_bars_min_above"],
        "dip_vol_ratio": dip_vol,
        "close_loc": (last - lo) / (hi - lo) if hi > lo else 1.0,
        "day_low": lo,
        "extended": last > ctx["sma20"] + cfg["ext_atr_mult"] * ctx["atr"],
        "vwap": vw[-1],
    }


# ----------------------------------------------------------------- engine
def _kind(entry: dict) -> str:
    if entry.get("position"):
        return "POS"
    if entry.get("pivot"):
        return "PIVOT"
    if "exhaustion_hammer" in (entry.get("sources") or []):
        return "EH"
    return "MB"


def _stop_for(kind: str, entry: dict, s: dict, cfg: dict) -> float:
    if kind == "PIVOT":
        piv = entry["pivot"]
        floor = piv * (1 - cfg["pivot_stop_pct"] / 100)
        contraction = entry.get("stop")
        return max(floor, contraction * 0.99) if contraction else floor
    if kind == "EH" and entry.get("stop"):
        return float(entry["stop"])
    return s["day_low"]


def _new_state(kind: str, industry: str | None) -> dict:
    return {
        "kind": kind,
        "tier": 0,
        "held": 0,
        "below": 0,
        "dead": False,
        "entry": None,
        "entry_slot": None,
        "entry_tier": None,
        "stop": None,
        "max_tier": 0,
        "industry": industry,
        "hist": [],
    }


def evaluate_slot(
    state: dict,
    *,
    slot: str,
    candidates: dict[str, dict],
    data: SlotData,
    cfg: dict | None = None,
) -> tuple[dict, list[dict]]:
    """Advance ``state`` (symbol → tracking dict) by one slot and return the signal rows.

    ``candidates`` maps symbol → watchlist/scan entry: {pivot, stop, entry, sources,
    sector, industry, position:{entry_price, entry_date, shares, stop}}.
    """
    cfg = {**DEFAULT_CFG, **(cfg or {})}
    state = {k: dict(v) for k, v in state.items()}
    syms = sorted(set(candidates) | set(state))
    evals: dict[str, dict] = {}

    for sym in syms:
        entry = candidates.get(sym, {})
        kind = state.get(sym, {}).get("kind") or _kind(entry)
        rows = data.daily(sym)
        ctx = daily_context(rows) if rows else None
        if not ctx or ctx["prev_close"] < cfg["min_price"] and kind != "POS":
            continue
        bars = data.bars(sym)
        s = snapshot(bars, ctx, cfg)
        if not s:
            continue
        sec = entry.get("sector") or (data.sector(sym) or {}).get("sector")
        industry = entry.get("industry") or (data.sector(sym) or {}).get("industry")
        etf = SECTOR_ETF.get(sec or "")
        etf_c = data.etf_chg(etf) if etf else None
        rs = s["chg"] - etf_c if etf_c is not None else None
        if kind == "POS":
            evals[sym] = {"kind": kind, "s": s, "ctx": ctx, "entry": entry, "industry": industry, "rs": rs, "etf": etf}
            continue
        # gross price checks first; the same-time volume baseline is only pulled for names that pass
        if kind == "PIVOT":
            gross = s["last"] > entry["pivot"]
        elif kind == "EH":
            gross = bool(entry.get("entry")) and s["last"] > entry["entry"]
        else:
            gross = (
                cfg["mb_min_gain_pct"] <= s["chg"] <= cfg["mb_max_gain_pct"]
                and s["from_open"] >= cfg["mb_min_from_open_pct"]
                and all(c <= cfg["mb_prior_day_max_pct"] for c in ctx["chg3"])
            )
        tracked = sym in state and state[sym]["tier"] > 0 and not state[sym]["dead"]
        if not gross and not tracked and sym not in state:
            continue
        vol = same_time_volume(bars, data.hist_bars(sym), data.until_hm, cfg) if (gross or tracked) else None
        ratio, pct = vol if vol else (0.0, 0.0)
        evals[sym] = {
            "kind": kind, "s": s, "ctx": ctx, "entry": entry, "gross": gross, "ratio": ratio, "pct": pct,
            "rs": rs, "etf": etf, "industry": industry,
        }

    # E1 per symbol
    trig: dict[str, str | None] = {}
    for sym, ev in evals.items():
        if ev["kind"] == "POS":
            continue
        s, e, kind = ev["s"], ev["entry"], ev["kind"]
        volok = ev["pct"] >= cfg["vol_pct_trigger"] or ev["ratio"] >= cfg["vol_ratio_trigger"]
        if kind == "PIVOT":
            over = s["last"] > e["pivot"]
            chase_ok = s["last"] <= e["pivot"] * (1 + cfg["pivot_chase_pct"] / 100)
            near = s["last"] <= e["pivot"] * (1 + cfg["pivot_armed_max_pct"] / 100)
            trig[sym] = "E1" if (over and chase_ok and s["above_vwap"] and volok) else ("armed" if (over and near) else None)
        elif kind == "EH":
            trig[sym] = "E1" if (ev["gross"] and s["above_vwap"] and volok) else None
        else:
            risk_ok = (s["day_low"] / s["last"] - 1) >= -cfg["mb_max_risk_pct"] / 100
            trig[sym] = "E1" if (ev["gross"] and s["above_vwap"] and volok and risk_ok) else None
        st = state.get(sym)
        if st and st["tier"] > 0 and not st["dead"] and trig[sym] != "E1":
            # already in: price holding keeps the evidence loop alive; the entry trigger need not repeat
            holding = s["above_vwap"] and (kind != "PIVOT" or s["last"] > e["pivot"]) and (st["stop"] is None or s["last"] > st["stop"])
            if holding:
                trig[sym] = "E1"

    # theme: industries with enough live names this slot
    ind_count: dict[str, int] = {}
    for sym, ev in evals.items():
        if ev["kind"] != "POS" and (trig.get(sym) == "E1" or state.get(sym, {}).get("tier", 0) > 0):
            ind_count[ev["industry"]] = ind_count.get(ev["industry"], 0) + 1

    signals: list[dict] = []
    for sym, ev in evals.items():
        s, e, kind = ev["s"], ev["entry"], ev["kind"]
        st = state.get(sym)

        if kind == "POS":
            pos = e.get("position") or {}
            stop = pos.get("stop") or e.get("stop")
            ep = pos.get("entry_price") or e.get("entry")
            exit_ = bool(stop and s["last"] < stop) or (not s["above_vwap"] and s["last"] < ev["ctx"]["prev_low"])
            signals.append({
                "symbol": sym, "kind": "POS", "level": "EXIT" if exit_ else "HOLD", "tier": None, "new": False,
                "price": s["last"], "stop": stop, "stop_pct": (stop / s["last"] - 1) * 100 if stop else None,
                "pnl_pct": (s["last"] / ep - 1) * 100 if ep else None, "entry_date": pos.get("entry_date"),
                "above_vwap": s["above_vwap"], "rs": ev["rs"], "etf": ev["etf"], "industry": ev["industry"],
                "reason": ("< stop" if stop and s["last"] < stop else ("↓VWAP & < prev low" if exit_ else None)),
            })
            continue

        t = trig.get(sym)
        common = {
            "symbol": sym, "kind": kind, "price": s["last"], "pivot": e.get("pivot"), "chg": s["chg"],
            "from_open": s["from_open"], "vol_pct": ev.get("pct"), "vol_ratio": ev.get("ratio"), "rs": ev["rs"],
            "etf": ev["etf"], "close_loc": s["close_loc"], "extended": s["extended"], "industry": ev["industry"],
            "above_vwap": s["above_vwap"], "theme_n": ind_count.get(ev["industry"], 0),
        }

        # kills / fall-backs for tracked names
        if st and st["tier"] > 0 and not st["dead"]:
            if st["stop"] is not None and s["last"] < st["stop"]:
                st["dead"] = True
                st["hist"].append([slot, "dead"])
                signals.append({**common, "level": "DEAD", "tier": st["tier"], "new": False, "stop": st["stop"], "reason": f"< stop {st['stop']:.2f}"})
                continue
            if kind == "PIVOT" and s["last"] < e["pivot"] * (1 - cfg["pivot_fall_pct"] / 100):
                st["tier"], st["held"], st["below"] = 0, 0, 0
                st["hist"].append([slot, "fell"])
                signals.append({**common, "level": "ARMED", "tier": 0, "new": False, "stop": st["stop"], "reason": "back under pivot"})
                continue

        if t == "E1":
            if not st:
                st = state[sym] = _new_state(kind, ev["industry"])
            if st["dead"]:
                continue
            if st["stop"] is None:
                st["stop"] = _stop_for(kind, e, s, cfg)
            st["held"] += 1
            st["below"] = 0
            E2 = ev["pct"] >= cfg["vol_pct_strong"]
            E3 = s["close_loc"] >= cfg["close_loc"] and s["above_vwap"]
            E4 = ev["rs"] is not None and ev["rs"] >= cfg["rs_pct"]
            E5 = not s["extended"]
            E7 = ind_count.get(ev["industry"], 0) >= cfg["theme_min"]
            n = sum([E2, E3, E4, E5])
            if st["held"] == 1:
                tier = 2 if (E2 and E4 and E5) else 1
            elif n == 4 or (n == 3 and E7):
                tier = 3
            elif n >= 3:
                tier = 2
            else:
                tier = 1
            prev_tier = st["tier"]
            if prev_tier and tier < prev_tier - 1:
                tier = prev_tier - 1  # evidence can fade one step per slot; only a kill drops faster
            st["tier"] = tier
            st["max_tier"] = max(st["max_tier"], tier)
            new = st["entry"] is None
            if new:
                st["entry"], st["entry_slot"], st["entry_tier"] = s["last"], slot, tier
            st["hist"].append([slot, tier])
            signals.append({
                **common, "level": "BUY", "tier": tier, "new": new, "stop": st["stop"],
                "stop_pct": (st["stop"] / s["last"] - 1) * 100, "held": st["held"], "entry": st["entry"],
                "evidence": {"E2": E2, "E3": E3, "E4": E4, "E5": E5, "E7": E7},
                "change": (tier - prev_tier) if prev_tier else 0,
            })
        elif t == "armed":
            if not st:
                st = state[sym] = _new_state(kind, ev["industry"])
            if st["dead"]:
                continue
            if st["tier"] == 0:
                st["hist"].append([slot, "armed"])
                signals.append({**common, "level": "ARMED", "tier": 0, "new": False, "stop": st["stop"], "reason": "volume light"})
            else:
                _demote(st, s, slot, cfg, signals, common)
        elif st and st["tier"] > 0 and not st["dead"]:
            _demote(st, s, slot, cfg, signals, common)

    return state, signals


def _demote(st: dict, s: dict, slot: str, cfg: dict, signals: list, common: dict) -> None:
    """Tracked name lost the hold condition this slot. A dip under VWAP only counts
    after ``below_vwap_slots`` consecutive slots, and not when it happened on thin
    volume (shakeout)."""
    counted = (not s["above_vwap"]) and s["dip_vol_ratio"] >= cfg["shakeout_vol_ratio"]
    st["below"] = st["below"] + 1 if counted else st["below"]
    if st["below"] >= cfg["below_vwap_slots"]:
        st["tier"] = max(0, st["tier"] - 1)
        st["below"] = 0
        st["hist"].append([slot, f"down{st['tier']}"])
        signals.append({**common, "level": "DOWN", "tier": st["tier"], "new": False, "stop": st["stop"],
                        "reason": f"↓VWAP {cfg['below_vwap_slots']} slots on volume"})
    else:
        st["hist"].append([slot, "hold"])
        note = "↓VWAP thin volume (shakeout?)" if (not s["above_vwap"] and not counted) else ("↓VWAP 1 slot" if not s["above_vwap"] else "holding")
        signals.append({**common, "level": "BUY", "tier": st["tier"], "new": False, "stop": st["stop"],
                        "stop_pct": (st["stop"] / s["last"] - 1) * 100 if st["stop"] else None,
                        "held": st["held"], "entry": st["entry"], "change": 0, "note": note})


# ----------------------------------------------------------------- rendering
def _fmt_pct(x: float | None, signed: bool = True) -> str:
    if x is None:
        return "—"
    return f"{x:+.1f}%" if signed else f"{x:.1f}%"


def render_lines(signals: list[dict]) -> list[str]:
    """Discord/markdown lines, strongest first. Empty list → caller prints ``none``."""
    order = {"BUY": 0, "DOWN": 1, "DEAD": 2, "EXIT": 3, "HOLD": 4, "ARMED": 5}
    rows = sorted(signals, key=lambda r: (order.get(r["level"], 9), -(r.get("tier") or 0), r["symbol"]))
    out: list[str] = []
    for r in rows:
        sym = f"{r['symbol']:<5}"
        lvl = r["level"]
        if lvl == "BUY":
            icon = TIER_ICON[r["tier"]]
            if r.get("new"):
                icon += "★"
            head = f"{icon:<8} {sym} {r['kind']:<5}"
            if r["kind"] == "PIVOT":
                body = f"{r['price']:.2f}>{r['pivot']:.2f} ({(r['price'] / r['pivot'] - 1) * 100:+.1f}%)"
            else:
                body = f"{_fmt_pct(r['chg'])} fromOpen{_fmt_pct(r['from_open'])}"
            vol = f"vol p{r['vol_pct']:.0f}" if r.get("vol_pct") is not None else ""
            rs = f"RS{r['rs']:+.1f}/{r['etf']}" if r.get("rs") is not None and r.get("etf") else ""
            cl = f"cl{r['close_loc']:.2f}"
            held = f"held {r['held']}" if r.get("held") else ""
            stop = f"stop {r['stop']:.2f} ({r['stop_pct']:+.1f}%)" if r.get("stop") else ""
            theme = f"{r['industry']}×{r['theme_n']}" if r.get("theme_n", 0) >= 3 and r.get("industry") else ""
            note = r.get("note") or ""
            out.append(" ".join(x for x in [head, body, vol, rs, cl, held, stop, theme, note] if x))
        elif lvl == "DOWN":
            out.append(f"{'↓' + TIER_ICON[r['tier']]:<8} {sym} {r['kind']:<5} {r['reason']}  stop {r['stop']:.2f}" if r.get("stop") else f"{'↓' + TIER_ICON[r['tier']]:<8} {sym} {r['kind']:<5} {r['reason']}")
        elif lvl == "DEAD":
            out.append(f"{'✗':<8} {sym} {r['kind']:<5} {r['reason']}")
        elif lvl == "ARMED":
            piv = f"over {r['pivot']:.2f} ({(r['price'] / r['pivot'] - 1) * 100:+.1f}%)" if r.get("pivot") else ""
            vol = f"vol p{r['vol_pct']:.0f}" if r.get("vol_pct") is not None else ""
            out.append(" ".join(x for x in [f"{'⚪':<8} {sym} armed", piv, vol, r.get("reason") or ""] if x))
        elif lvl in ("HOLD", "EXIT"):
            pnl = _fmt_pct(r.get("pnl_pct"))
            stop = f"stop {r['stop']:.2f} ({r['stop_pct']:+.1f}%)" if r.get("stop") else "no stop"
            tag = "EXIT" if lvl == "EXIT" else "HOLD"
            reason = f"— {r['reason']}" if r.get("reason") else "no exit signal"
            out.append(f"{tag:<8} {sym} {pnl} {'↑' if r.get('above_vwap') else '↓'}VWAP {stop} {reason}")
    return out
