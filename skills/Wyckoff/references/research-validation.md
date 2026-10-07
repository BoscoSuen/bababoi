# Testing a Wyckoff hypothesis

Use this reference when the user requests a backtest, validation or formal detector design. An ordinary chart interpretation does not require running a research program.

## Freeze the claim before measuring it

Specify the market/universe, timeframe, data adjustments, information cutoff policy, range construction, event thresholds, confirmation delay, entry timing, exit/invalidation, maximum holding time and transaction costs. State how overlapping setups and missing data are handled. Separate source definitions from operational choices such as lookback windows or volume ratios.

For discretionary assessment, prospective timestamped judgments or blinded replay can be tested. Code is useful for reproducibility, but lack of a mechanical definition does not make a human judgment inherently untestable. Record the prompt/model version if an LLM supplies labels, and prevent access to later outcomes.

## Evaluate the right question

- Label agreement measures annotation consistency, not profitability.
- Synthetic-pattern classification measures recognition of that generator, not real-market prediction.
- Price touching a projected level does not demonstrate tradable excess returns.
- Confluence among features derived from the same prices is not independent corroboration.

Compare with relevant simple strategies and matched nulls that preserve the opportunity set, timing and important dependence. Random horizontal lines or uniform prices may answer a geometric coverage question, but not the entire trading question.

## Validation design

Keep chronological training, selection and held-out evaluation separate. Purge overlapping outcome windows across splits and account for serially dependent events. Use suitable block resampling or another dependence-aware method when estimating uncertainty; do not silently apply independent Bernoulli assumptions to clustered events.

Record all tried rules, markets, thresholds and prompt variants. Correct for selection/multiple testing across the actual search family. Do not tune on the holdout and continue calling it out-of-sample. Show unsuccessful tests as well as winners.

Model executable timing, spread, fees, slippage, liquidity, funding or borrow where applicable. Report turnover, exposure, drawdown and net returns against the chosen benchmark, alongside uncertainty and sample size. Handle same-bar stop/target ambiguity with finer data or a stated conservative assumption.

For probability claims, define the predicted event and horizon, then show held-out calibration and an appropriate scoring rule. A qualitative assessment or hand-assigned weight has no calibrated percentage by default.

## Evidence status

Use one of `not_tested`, `inconclusive`, `supported_in_tested_scope` or `not_supported_in_tested_scope`, accompanied by the tested specification and limitations. A supported result applies to that implementation, dataset and period; it does not validate every use of Wyckoff.

This skill ships no empirical edge claim, calibrated classifier or execution engine. Do not report a test as run merely because its procedure is described here.
