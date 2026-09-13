# Posture rules (initial defaults — tune in `config/default.yaml`)

## Component scores (0–100)

| Component | Inputs | Mapping |
|---|---|---|
| breadth | % advancers, % above day VWAP, up/down volume ratio | mean of: pct_advancers, pct_above_vwap, `50 + 25·log2(ud_ratio)` clipped |
| index | SPY and QQQ state on the last confirmed 5-min bar | 50 ± 12.5 per index for above/below VWAP, +7.5 above prior-day high, −12.5 below prior-day low, ±5 max for return since open |
| sector | risk-on spread = mean RS(XLK, XLY, XLC, IWM, HYG) − mean RS(XLP, XLU, XLV, TLT, GLD), RS vs SPY since open | `50 + 25·spread%` clipped |

Composite = `0.4·breadth + 0.3·index + 0.3·sector`, renormalised over the components
that are available.

## Recommendation

1. `CASH_PRIORITY` if any of: score < 40; (% advancers < 30 and U/D ratio < 0.5);
   SPY below prior-day low.
2. `NEW_ENTRY_ALLOWED` if score ≥ 60 and SPY above session VWAP.
3. Otherwise `REDUCE_ONLY` (score ≥ 60 but SPY below VWAP also lands here).

## Hysteresis

A change of recommendation must be produced by two consecutive slots, unless the
composite score moved by 15 points or more since the previous slot. The pending
candidate is reported as `posture.pending_flip`. State resets each session.

## Daily cap

The latest `reports/exposure_posture_*.json` (exposure-coach) is the ceiling: the hourly
posture may sit at most one step above it (`CASH_PRIORITY → REDUCE_ONLY` allowed,
`CASH_PRIORITY → NEW_ENTRY_ALLOWED` not). `posture.capped_by_daily` records when the cap
bit.

## Watchlist signals (last closed clock-hour bar)

| Signal | Condition |
|---|---|
| `FHR_BREAKOUT` | hourly close > first-hour (09:30–10:30) high and rel_vol ≥ 1.2 |
| `FHR_BREAKDOWN` | hourly close < first-hour low |
| `GAP_HOLD` | gap ≥ +2% and hourly close > prior-day high |
| `GAP_FAIL` | gap ≥ +2% and hourly close < session open |
| `VWAP_RECLAIM` | previous hour closed below VWAP, this hour closed at/above |
| `VWAP_LOSS` | previous hour closed above VWAP, this hour closed at/below |

`rel_vol = session volume so far / (20-session average volume × expected fraction traded
by now)` using the piecewise volume curve in the config.

## Slot timing (ET, 15-minute delayed feed)

| Slot | Data through | Purpose |
|---|---|---|
| 09:50 | 09:35 | opening read (gap, first bars) |
| 10:20 | 10:05 | first-hour bar (09:30–10:00) closed; first narrative |
| 11:20–14:20 | HH:05 | hourly updates |
| 15:20 | 15:05 | last actionable read; second narrative |
| 15:50 | 15:35 | pre-close strength/weakness |
| 16:20 | 16:00 | full-session wrap-up; feeds the next morning |
