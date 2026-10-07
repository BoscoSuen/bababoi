---
layout: default
title: "Wyckoff"
grand_parent: English
parent: Skill Guides
nav_order: 90
lang_peer: /zh/skills/Wyckoff/
permalink: /en/skills/Wyckoff/
generated: false
---

# Wyckoff

Interpret supplied charts, timestamped OHLCV or US equity daily bars fetched through the shared Polygon provider. This experimental skill separates observable behavior, structural interpretation and conditional planning. Its data helper does not identify phases or provide a calibrated probability model or demonstrated trading edge.

## 1. Prerequisites

Supply a readable chart or chronological OHLCV, the instrument and timeframe, and an analysis cutoff. Alternatively supply a US stock/ETF ticker and fetch daily bars through the shared data layer. Supplied data requires no API key; live fetching requires `POLYGON_API_KEY`, Python 3.9+ and the skill's `requirements.txt`. Missing volume permits a qualified price-only assessment, not volume-confirmed claims.

The requested folder and skill name are case-sensitive `Wyckoff`. The repository's name-to-folder check accepts this pairing; generic skill validators that require lowercase names flag it. A lowercase-only host needs both folder and frontmatter renamed together for its own installation.

## 2. Quick Start

Ask, for example:

> Use Wyckoff to review this daily chart as of its last completed bar. Compare accumulation with a continuing decline, identify evidence against each, and specify what would change the assessment. Do not invent a win probability.

For replay, supply data truncated at the intended cutoff. A chart exposing later outcomes supports retrospective interpretation, not a blind historical prediction.

To fetch daily observations, run from the repository:

```bash
python3 skills/Wyckoff/scripts/fetch_wyckoff_data.py \
  --symbol AAPL --start 2024-01-01 \
  --as-of 2024-10-01T12:00:00-04:00 --output-dir reports/
```

Use dates appropriate to the request. The helper excludes the entire New York cutoff date, even after close; this example includes at most September 30. It returns daily bars only. Add `--provider fixture --fixture-dir DIR` to replay a shared cache without network calls or an API key. A separately installed skill needs `TRADING_SKILLS_REPO_ROOT` pointing to a checkout containing `scripts/market_data`; the shared module is not bundled in the skill archive.

## 3. How It Works

1. Establish data provenance and the information boundary.
2. Describe price, spread, closes and comparable volume before assigning labels.
3. Record candidate/confirmed/failed events, their criteria and availability times.
4. Compare the leading interpretation with a plausible alternative.
5. Specify trigger, invalidation and missing evidence; return a conditional plan, wait, no trade or insufficient data.

Springs and UTADs are optional. Missing early phases are not filled in. A failed bullish setup does not automatically prove distribution. Statements about absorption remain interpretations rather than identification of institutional traders.

## 4. Output

Market assessments produce matching Markdown and JSON files in `reports/`, named `Wyckoff_<symbol>_<cutoff>_<run-id>`. Reports preserve source limitations, event timing, scenario evidence, triggers, invalidation and prior-report changes. Unknown values are null. Conceptual questions are answered directly without empty report files.

The fetch helper separately emits `Wyckoff_ohlcv_<symbol>_<cutoff>_<run-id>.json` with ascending bars and provenance. Read it before the analysis. It rejects malformed data and retains zero volume with a warning. Its split-adjusted OHLC does not mix in dividend-adjusted close; historical revisions mean it is not a point-in-time snapshot. Calendar coverage and staleness still need review. Exit 0 indicates a saved data bundle, 1 a fetch/data/output failure, and 2 an argument/setup problem.

| Status | Interpretation |
|---|---|
| `INSUFFICIENT_DATA` | Critical observations cannot be established |
| `WAIT` | The structure still needs evidence before a defensible plan can be specified |
| `NO_TRADE` | The assessed setup failed or lacks a defensible plan |
| `CONDITIONAL_PLAN` | Setup evidence supports explicit trigger/invalidation conditions; execution trigger may remain pending |

Evidence strength is qualitative and is not a win rate. Position sizing requires separate risk inputs; no orders, holdings updates or notifications are sent.

## 5. Research and Limitations

For empirical-validation requests, the skill requires a frozen specification, causal replay, chronological holdouts, dependence-aware uncertainty, accounting for repeated selection and realistic costs. Human judgments may be evaluated with blinded replay or prospective records. Synthetic pattern recognition and projected-level touches do not establish trading profitability.

This is an original synthesis informed by naiemk's scenario workflow and modern Wyckoff teaching, with additional timing and provenance constraints. It does not bundle third-party books or impose crypto rotation, Gann or Elliott Wave rules on ordinary Wyckoff analysis.

## 6. Resources

The skill package contains `SKILL.md`, four focused references (`methodology`, `data-and-timing`, `research-validation`, `sources`), an analysis-report template, the data-fetch helper and `requirements.txt`. Read the source attribution and evidence limits in `skills/Wyckoff/references/sources.md`.

[Chinese guide]({{ '/zh/skills/Wyckoff/' | relative_url }})
