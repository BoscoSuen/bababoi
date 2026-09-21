---
name: intraday-market-monitor
description: Run an hourly, deterministic intraday market read on 15-minute-delayed Polygon data (breadth from one all-tickers snapshot, SPY/QQQ vs VWAP and prior-day range, sector relative strength, hourly-close watchlist signals) and emit an exposure posture (NEW_ENTRY_ALLOWED / REDUCE_ONLY / CASH_PRIORITY) with Discord notification and optional Claude narrative. Use during the US session at :20 past the hour, or to replay a past session.
---

# Intraday Market Monitor

## Overview

A launchd-driven script that, every 30 minutes at fixed ET slots (09:50, 10:20, 10:50 … 15:50, 16:20),
pulls Polygon Stocks Starter data (15-minute delayed), computes an hourly market
posture, writes `reports/intraday/<date>/intraday_<HHMM>.{json,md}`, posts a compact
summary to Discord, and at 10:20 / 15:20 / on a posture flip asks Claude (`claude -p`)
for a short narrative. The JSON's top-level `recommendation` uses the same tokens as
exposure-coach, so `pre-trade-discipline-gate --market-regime-decision` can consume it.

The delay is a design input, not a bug: every slot judges the **last closed clock-hour
bar** (at HH:20 the bar that closed at HH:00 is confirmed). Nothing here reacts within
minutes; that is out of scope on this plan tier.

## When to Use

- Every 30 minutes during the US regular session, via launchd (`--auto-slot`). Watchlist names and pivot/stop levels come from `state/daily_watchlist.json`, written after the close by `scripts/send_swing_signal.py`.
- After the close (16:20 slot) to record the full-session posture for the next morning.
- To replay a past session from the on-disk cache (`replay --date`) when tuning thresholds.
- Not for entry timing on a single stock; not a substitute for the daily
  `market-regime-daily` workflow (its exposure-coach output caps this monitor's posture).

## Prerequisites

- `POLYGON_API_KEY` (Polygon Stocks Starter or higher) in the environment or `.envrc`
- `DISCORD_MARKET_REPORT_URL` (optional; `--no-discord` to skip)
- `claude` CLI on PATH for narratives (optional; `--narrative never` to skip)
- `pip install -r skills/intraday-market-monitor/requirements.txt`
- Optional `state/watchlist.yaml` (see `references/watchlist.example.yaml`) and/or the
  latest `reports/vcp_screener_*.json` via `--vcp-json`

## Workflow

1. Determine the slot: `--auto-slot` picks the latest due slot not in
   `state/intraday/<date>/slots_done.json` (catch-up after sleep); exit 0 on non-session days.
2. Data horizon `until_et = floor5(slot − 15 min)`; all bars after it are dropped.
3. Breadth: one `/v2/snapshot/.../tickers` call → filter `^[A-Z]{1,5}$`, prev close ≥ 5,
   prev volume ≥ 100k → % advancers, % above day VWAP, % above prior high / below prior
   low, up/down volume ratio, volume pace vs 20-session average (grouped-daily, cached).
4. Index + sectors: 5-minute RTH bars for SPY/QQQ/IWM, 11 SPDR sectors, TLT/HYG/GLD →
   VWAP, prior-day range breaks, RS vs SPY since open and over the last closed hour,
   risk-on spread.
5. Watchlist: hourly bars from 5-minute bars → `FHR_BREAKOUT/BREAKDOWN`, `GAP_HOLD/FAIL`,
   `VWAP_RECLAIM/LOSS` on the last closed hour.
6. Posture: `0.4·breadth + 0.3·index + 0.3·sector` → rules in
   `references/posture-rules.md`, two-slot hysteresis, capped one step above the latest
   `reports/exposure_posture_*.json`.
7. Write JSON + Markdown, update `state/intraday/last_posture.json`, post to Discord,
   run the narrative when due.

## Commands

```bash
# launchd entry point (see launchd/com.trade-analysis.intraday-monitor.plist)
python3 skills/intraday-market-monitor/scripts/intraday_monitor.py run --auto-slot

# explicit slot, no side effects
python3 skills/intraday-market-monitor/scripts/intraday_monitor.py run --slot 1020 \
  --no-discord --narrative never

# offline replay from a recorded cache directory
python3 skills/intraday-market-monitor/scripts/intraday_monitor.py run --slot 1020 \
  --provider fixture --fixture-dir .cache/market_data --no-discord --narrative never

# webhook smoke test
python3 skills/intraday-market-monitor/scripts/intraday_monitor.py discord-test
```

## Output Format

See `references/output-schema.md`. Key fields: `recommendation`, `posture{score,
reason_codes, flipped_from, pending_flip, capped_by_daily}`, `metrics{breadth, index,
sectors}`, `watchlist_signals[]`, `data_asof`, `data_horizon_et`, `delay_minutes`.

## Resources

- `config/default.yaml` — every threshold, universe, and slot (tunable)
- `references/posture-rules.md` — scoring and recommendation rules
- `references/output-schema.md` — JSON contract consumed by downstream gates
- `references/narrative-prompt.md` — the `claude -p` prompt template
- `scripts/market_data/` (repo root) — shared Polygon provider, cache, and replay fixture
