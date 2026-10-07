# Data provenance and causal timing

## Input audit

Record the source/file/chart, instrument and venue, timeframe, timezone, currency/units, covered period, adjustment convention, last completed bar and analysis cutoff. Identify volume as exchange-traded units, contracts, notional, tick volume or unavailable.

For OHLCV data, inspect chronological order, duplicate timestamps, missing sessions and finite numeric values. Require low <= open/close <= high and nonnegative volume when volume is present. Investigate invalid or conflicting rows; do not silently fill price or volume gaps. Check split/dividend adjustments and futures rolls before interpreting discontinuities. A negative futures price is not automatically a corrupt observation.

For screenshots, establish visible scale, timeframe and timestamps. Mark visually estimated levels approximate. If axes or dates are unreadable, do not invent precise prices or confirmation times. Price-only structure may be discussed if supported; report the missing volume assessment.

Use consistent volume definitions and comparable venues. Forex tick counts are not consolidated traded volume. A single crypto venue does not represent the whole market; exchange transfers and funding rates are context, not direct proof of accumulation. Do not compare unnormalized dollar volume with share volume or assume a split-adjusted price series has correspondingly adjusted volume.

## Historical availability

Separate four times when relevant:

1. `observed_at`: bar/event time, with bar timestamp convention stated.
2. `confirmed_at`: earliest time all stated event conditions were available.
3. `as_of`: information cutoff for this assessment.
4. `generated_at`: when the report was written.

For example, a pivot at Monday's low requiring two subsequent completed daily bars is not known on Monday. It can become usable only after Wednesday's bar completes. A Monday/Tuesday replay must keep it provisional. A signal using Wednesday's close does not receive a fill at that close unless a feasible execution assumption is demonstrated.

Use only completed higher-timeframe bars available at `as_of`; a midweek read cannot use Friday's final weekly high, low or volume. Truncate observations before computing thresholds, extrema, normalizers or resampled features. Track publication delays and revisions where external context matters.

If only event order is visible, retain the order but set exact times to null. Do not classify an event as causally confirmed at a historical cutoff unless its availability can be established. When a hindsight chart has already exposed subsequent outcomes, label that assessment retrospective; do not claim it as a blind replay.

## Updates and degraded inputs

Preserve previous reports. Describe each change in hypothesis with new evidence and the time it became available. If a data correction rather than a new bar changed the view, say so.

Distinguish unavailable evidence from negative evidence: missing benchmark data does not mean weak relative strength; missing volume does not mean low volume; an unseen earlier phase does not mean it never occurred.

Return `INSUFFICIENT_DATA` when critical context or levels are unreadable. Use a qualified price-only scenario when prices suffice, but leave volume claims unassessed. Where price and volume sources disagree materially, resolve the mismatch or abstain from conclusions depending on it.

## Polygon helper contract

`scripts/fetch_wyckoff_data.py` calls the existing `scripts.market_data.get_provider(...).daily_bars(...)`. It inherits the shared cache, pagination, bounded retries and credential redaction. It adds a daily cutoff, OHLCV validation and an auditable JSON input bundle; it does not implement a second HTTP client or infer Wyckoff labels.

- Supply `--symbol`, inclusive `--start` and timezone-aware `--as-of`. The final requested date is the day before the cutoff in America/New_York. Same-date bars are excluded even after close. Future cutoffs, invalid intervals and implicit index proxies are rejected.
- Set `POLYGON_API_KEY` for live calls. `--provider fixture --fixture-dir DIR` reads the shared DiskCache layout and never fetches missing cache entries from the network. Ordinary user-supplied CSV/JSON remains an agent input, not a fixture cache directory.
- Run inside this repository. For a separately installed skill package, set `TRADING_SKILLS_REPO_ROOT` to a checkout containing `scripts/market_data` and install the skill's `requirements.txt`; the package does not vendor the shared layer. Charts and supplied data remain usable without this setup.
- Read the emitted `reports/Wyckoff_ohlcv_<symbol>_<cutoff>_<run-id>.json`. It records requested/actual coverage, provider, original and normalized ticker, generation/cutoff times, adjustment basis, volume type, warnings and ascending `bars` with `date/open/high/low/close/volume`.
- Use the provider's split-adjusted O/H/L/C consistently. Ignore its separately dividend-adjusted `adjClose` rather than mixing adjustment bases. Provider history can be revised or adjusted for later splits; `point_in_time_snapshot` is false. Investigate corporate-action effects before treating historical replay as empirical evidence.
- Duplicate dates, non-finite values, invalid equity OHLC, missing normalized volume and negative volume fail the fetch. Zero volume is retained with a warning because the shared provider can normalize absent raw volume to zero. Do not interpret such rows as proof of absent supply/demand.
- No exchange-calendar completeness check or fixed minimum history proves structural sufficiency. Inspect coverage, gaps and the actual last bar before analyzing. Do not silently fill gaps.
- Exit codes: 0 means a data bundle was saved; 1 means a fetch/data/output failure; 2 means invalid arguments, missing credentials, missing dependencies or missing repository setup. No signal is produced on any path.
