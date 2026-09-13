---
layout: default
title: "Intraday Market Monitor"
grand_parent: English
parent: Skill Guides
nav_order: 37
lang_peer: /ja/skills/intraday-market-monitor/
permalink: /en/skills/intraday-market-monitor/
generated: true
---

# Intraday Market Monitor
{: .no_toc }

Run an hourly, deterministic intraday market read on 15-minute-delayed Polygon data (breadth from one all-tickers snapshot, SPY/QQQ vs VWAP and prior-day range, sector relative strength, hourly-close watchlist signals) and emit an exposure posture (NEW_ENTRY_ALLOWED / REDUCE_ONLY / CASH_PRIORITY) with Discord notification and optional Claude narrative. Use during the US session at :20 past the hour, or to replay a past session.
{: .fs-6 .fw-300 }

<span class="badge badge-free">No API</span>

[Download Skill Package (.skill)](https://github.com/tradermonty/claude-trading-skills/raw/main/skill-packages/intraday-market-monitor.skill){: .btn .btn-primary .fs-5 .mb-4 .mb-md-0 .mr-2 }
[View Source on GitHub](https://github.com/tradermonty/claude-trading-skills/tree/main/skills/intraday-market-monitor){: .btn .fs-5 .mb-4 .mb-md-0 }

<details open markdown="block">
  <summary>Table of Contents</summary>
  {: .text-delta }
- TOC
{:toc}
</details>

---

## 1. Overview

A launchd-driven script that, at fixed ET slots (09:50, 10:20 … 15:20, 15:50, 16:20),
pulls Polygon Stocks Starter data (15-minute delayed), computes an hourly market
posture, writes `reports/intraday/<date>/intraday_<HHMM>.{json,md}`, posts a compact
summary to Discord, and at 10:20 / 15:20 / on a posture flip asks Claude (`claude -p`)
for a short narrative. The JSON's top-level `recommendation` uses the same tokens as
exposure-coach, so `pre-trade-discipline-gate --market-regime-decision` can consume it.

The delay is a design input, not a bug: every slot judges the **last closed clock-hour
bar** (at HH:20 the bar that closed at HH:00 is confirmed). Nothing here reacts within
minutes; that is out of scope on this plan tier.

---

## 2. When to Use

- Hourly during the US regular session, via launchd (`--auto-slot`).
- After the close (16:20 slot) to record the full-session posture for the next morning.
- To replay a past session from the on-disk cache (`replay --date`) when tuning thresholds.
- Not for entry timing on a single stock; not a substitute for the daily
  `market-regime-daily` workflow (its exposure-coach output caps this monitor's posture).

---

## 3. Prerequisites

- `POLYGON_API_KEY` (Polygon Stocks Starter or higher) in the environment or `.envrc`
- `DISCORD_WEBHOOK_URL` (optional; `--no-discord` to skip)
- `claude` CLI on PATH for narratives (optional; `--narrative never` to skip)
- `pip install -r skills/intraday-market-monitor/requirements.txt`
- Optional `state/watchlist.yaml` (see `references/watchlist.example.yaml`) and/or the
  latest `reports/vcp_screener_*.json` via `--vcp-json`

---

## 4. Quick Start

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

---

## 5. Workflow

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

---

## 6. Resources

**References:**

- `skills/intraday-market-monitor/references/narrative-prompt.md`
- `skills/intraday-market-monitor/references/output-schema.md`
- `skills/intraday-market-monitor/references/posture-rules.md`
- `skills/intraday-market-monitor/references/watchlist.example.yaml`

**Scripts:**

- `skills/intraday-market-monitor/scripts/_repo_bootstrap.py`
- `skills/intraday-market-monitor/scripts/breadth_metrics.py`
- `skills/intraday-market-monitor/scripts/discord_notify.py`
- `skills/intraday-market-monitor/scripts/intraday_monitor.py`
- `skills/intraday-market-monitor/scripts/narrative.py`
- `skills/intraday-market-monitor/scripts/posture.py`
- `skills/intraday-market-monitor/scripts/report_writer.py`
- `skills/intraday-market-monitor/scripts/run_slots.py`
- `skills/intraday-market-monitor/scripts/sector_rs.py`
- `skills/intraday-market-monitor/scripts/watchlist_signals.py`
