---
name: Wyckoff
description: Analyze charts, supplied OHLCV or US stock/ETF daily bars fetched through the repository's Polygon data layer using Wyckoff structure. Assess accumulation, distribution and price-volume events with competing scenarios, confirmation times and explicit invalidation. Use for Wyckoff chart reviews, symbol analysis, scenario updates or research specifications; not for generic screening or automatic orders.
---

# Wyckoff

## Overview

Build falsifiable market scenarios from observable price and volume behavior. Separate observations, structural interpretations and conditional plans. Treat phase labels as hypotheses, not proof of institutional intent or a profitable strategy.

Use supplied charts/data directly, or fetch US stock/ETF daily OHLCV with the bundled helper through the repository's shared Polygon provider. The helper prepares data only; interpret phases and scenarios using the references. No API key is needed for supplied data or fixture replay. Live fetching requires `POLYGON_API_KEY`, Python 3.9+ and `requirements.txt`. Do not invent a detector, backtest or measured win rate.

## When to Use

- Review accumulation, reaccumulation, distribution or redistribution on a chart.
- Distinguish a possible spring/upthrust from a continuing breakdown/breakout.
- Reassess a prior Wyckoff thesis using newly available bars.
- Turn a discretionary Wyckoff hypothesis into a testable research specification.

For a conceptual question, explain only the relevant concepts. For a market assessment, follow the workflow below. For a research request, additionally load [research-validation.md](references/research-validation.md). Keep Gann, Elliott Wave and crypto rotation out of the core method unless the user explicitly asks for a separate overlay.

## Workflow

### 0. Obtain the observations

For supplied charts or OHLCV, proceed to the input audit. For a US stock/ETF symbol without usable observations, run:

```bash
python3 skills/Wyckoff/scripts/fetch_wyckoff_data.py \
  --symbol AAPL --start 2024-01-01 \
  --as-of 2024-10-01T12:00:00-04:00 --output-dir reports/
```

Replace the illustrative symbol and dates with the requested interval. Use a timezone-aware current timestamp for a current assessment; use the user's information boundary for historical work. If no history length is specified, request roughly two years of calendar history as an operational starting point, then assess whether the returned structure is sufficient. This is not a Wyckoff threshold.

The helper deliberately excludes the entire New York cutoff date, even after the close. For example, an October 1 cutoff can include September 30, not October 1. Disclose the actual last bar and do not call it today's closing analysis. It fetches daily bars only, without generating weekly or intraday bars. For other markets/timeframes, use suitable supplied data or another explicitly identified source; do not silently replace an index with an ETF.

For offline replay of the shared cache format, append `--provider fixture --fixture-dir PATH`. Read [data-and-timing.md](references/data-and-timing.md#polygon-helper-contract) for the output contract, standalone-package setup and limitations. On a nonzero exit, report the fetch failure and request/use another input; do not reuse an unrelated old report or invent bars.

Read the generated JSON's `bars` and metadata before interpreting the market. The data bundle is not a completed analysis report and contains no phase or trade signal. Its historical split adjustments may reflect later revisions: date filtering alone does not make it a point-in-time data snapshot.

### 1. Establish the information boundary

Read [data-and-timing.md](references/data-and-timing.md). Record the instrument, venue, timeframe, timezone, analysis cutoff, last completed bar, input source and volume type. Distinguish the report's creation time from the historical information cutoff.

Use only information available by that cutoff, including higher-timeframe bars, pivot confirmations and benchmark observations. Mark an unfinished bar provisional. If a historical chart reveals later bars, request a cropped view or timestamped data for a causal replay; label any current reading of that full image retrospective.

If the symbol, scale, timeframe or observations needed for a decision cannot be established, return `INSUFFICIENT_DATA`, name the missing input and leave unsupported fields null. Missing volume can permit a qualified price-only reading, but cannot establish a volume-confirmed setup.

### 2. Describe behavior before assigning labels

Read [methodology.md](references/methodology.md). Establish the preceding trend, higher-timeframe context and range boundaries from identifiable observations. Describe tests, rejection/acceptance, spread, closes and comparable volume. Cite the bar, date or visible chart region behind each observation.

Do not infer a hidden buyer's identity from OHLCV. Do not assume every range is purposeful accumulation or distribution. Compare relative strength only when aligned benchmark data is available; mark it unassessed otherwise.

### 3. Build an event ledger

For each material event, record its label, operational criteria, observation time, earliest confirmation time, supporting facts, contradictory facts and status (`candidate`, `confirmed` or `failed`). Here, confirmed means the stated event criteria were met; it does not confirm future returns or a hidden accumulation campaign. Record when and why a previously confirmed interpretation failed.

Use Phase A-E only where the visible evidence supports them. Allow an unknown phase, an incomplete history and structures without a spring or UTAD. Never fill missing phases to complete a schematic. Distinguish local events from the higher-timeframe structure. Use explicit minor/major wording rather than ambiguous case-only abbreviations.

### 4. Compare scenarios and define disconfirmation

Write the leading interpretation and at least one materially different plausible alternative when making a directional assessment. If the evidence is too sparse for either, report that instead of manufacturing alternatives.

For each scenario state:

- Evidence for and against it, with observation references.
- Trigger and confirmation behavior, including timeframe and whether a close or intrabar observation is required.
- Invalidation level or observable behavior; explain why it contradicts the thesis.
- Conditional next path and any target method, separating structural levels from projections.
- What remains unknown and what new evidence would change the assessment.

Use qualitative evidence strength (`weak`, `mixed`, `strong`) with reasons. It describes support for an interpretation, not a win probability. Leave numeric probability null unless a relevant calibrated model and its held-out evaluation are supplied; disclose their scope and limitations. Do not turn a confluence count into a probability.

### 5. Decide and preserve the audit trail

Choose a report status:

| Status | Meaning |
|---|---|
| `INSUFFICIENT_DATA` | Required observations cannot be established; no actionable plan |
| `WAIT` | Usable evidence, but the structure still needs discriminating confirmation before a defensible plan can be specified |
| `NO_TRADE` | Evidence is interpretable, but the proposed setup failed, conflicts materially, or lacks a defensible plan |
| `CONDITIONAL_PLAN` | Enough evidence supports an explicit trigger/invalidation plan; report whether its trigger is pending or observed |

These are analytical output conventions, not original Wyckoff rules or automated trading gates. Missing contextual evidence or an undefined trigger/invalidation prevents `CONDITIONAL_PLAN`; a future execution trigger may still be pending if the setup evidence and plan are otherwise established. A price-only conditional plan must be explicitly identified as such, without volume-confirmed claims.

When updating a report, preserve the prior cutoff, levels and scenario. Explain which newly available observations changed it. A failed spring invalidates or weakens that bullish setup; it does not by itself prove distribution. Keep prior failures in the record rather than relabeling them away.

If execution planning is requested, distinguish a thesis invalidation from an executable stop, account for gaps and costs, and pass explicit inputs to the repository's position-sizing skill when available. Do not infer account risk or size from evidence strength. This skill does not submit orders, update holdings or send notifications.

## Output Format

Use [analysis-report.md](assets/analysis-report.md) for market assessments. Save matching Markdown and JSON reports to `reports/Wyckoff_<symbol>_<cutoff>_<run-id>.md` and `.json`, using filename-safe identifiers and a unique run ID. Keep prior reports intact. Write reports in English by repository convention unless the user requests another language. Answer conceptual questions directly without creating empty report artifacts.

Keep Markdown and JSON consistent. Use null for unavailable numbers and times, never zero, guessed prices or fabricated dates. Include data limitations even when the conclusion is `WAIT` or `INSUFFICIENT_DATA`. If file output is unavailable, return the report inline and state that it was not saved.

## Resources

- [methodology.md](references/methodology.md): Load for structural readings and event interpretation.
- [data-and-timing.md](references/data-and-timing.md): Load for data checks, historical cutoffs and confirmation timing.
- [research-validation.md](references/research-validation.md): Load when specifying or reviewing empirical tests; not required for an ordinary chart read.
- [sources.md](references/sources.md): Consult for attribution, theoretical scope and evidence limits.
- [analysis-report.md](assets/analysis-report.md): Use for report fields and the JSON contract.
- [fetch_wyckoff_data.py](scripts/fetch_wyckoff_data.py): Fetch and validate daily US equity OHLCV via the shared Polygon/fixture provider.
