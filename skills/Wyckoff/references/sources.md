# Sources and design provenance

Reviewed for this implementation on 2026-10-07. This skill is an original synthesis of public methodological ideas and the repository's reporting conventions; it does not vendor third-party skill text, books or article collections.

## Methodology sources

- [Wyckoff Analytics: The Wyckoff Method](https://www.wyckoffanalytics.com/wyckoff-method/). Modern practitioner exposition of phases, events, optional springs/UTADs, P&F objectives and the nine buying/selling tests. Use to check terminology; it is not independent proof of trading profitability or a verbatim original Wyckoff text.
- [Bruce Fraser: Context Is King](https://articles.stockcharts.com/article/articles-wyckoff-2015-09-context-is-king/). Applied explanation of contextual schematic reading. Treat examples as illustrations, not an unbiased performance sample.

## Skill design references

- [naiemk/wyckoff-ai, skill entrypoint at commit 8c5700c](https://github.com/naiemk/wyckoff-ai/blob/8c5700c95c05088b28184c088248c793cb27f245/skills/wyckoff-trader-skill/SKILL.md). Informed observation-first reasoning, competing scenarios, explicit disconfirmation and abstention. This implementation adds information-availability rules and a report contract; it does not adopt crypto-specific rotations as universal constraints or bundle the upstream corpus.
- [MinnMinn/trading-decision-system, Wyckoff skill](https://github.com/MinnMinn/trading-decision-system/blob/master/.claude/skills/wyckoff-skill/SKILL.md). Informed separation of source concepts, project thresholds and volume-data types. Do not import compulsory phase completion or case-insensitive minor/major label handling.

These are design references, not runtime dependencies or endorsements of every upstream rule. Linked branch contents may change.

## Research boundaries

- [Lo, Mamaysky and Wang: Foundations of Technical Analysis](https://www.mit.edu/~wangj/pap/LoMamayskyWang00.pdf). Systematic testing of selected technical patterns; not validation of this skill or every Wyckoff interpretation.
- [Cont, Kukanov and Stoikov: The Price Impact of Order Book Events](https://arxiv.org/abs/1011.6402). Evidence about order-flow imbalance and short-horizon price behavior; not a means of identifying institutional actors from OHLCV.
- [Bailey et al.: The Probability of Backtest Overfitting](https://www.davidhbailey.com/dhbpapers/backtest-prob.pdf). Motivation for accounting for repeated strategy selection and preserving genuine held-out evaluation.
- [Pal: Long Short-Term Memory Pattern Recognition in Currency Trading](https://arxiv.org/html/2403.18839v1). Its high pattern-recognition accuracy uses synthetic swing-point patterns; do not present it as live-market Wyckoff trading accuracy.

## Local conventions

The report statuses, qualitative evidence-strength vocabulary, event-ledger fields and file format are implementation choices. They are not historical Wyckoff laws. No numerical threshold, probability, return or position-sizing rule is validated merely by inclusion in this skill.
