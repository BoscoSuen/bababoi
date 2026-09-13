# Output schema — `reports/intraday/<date>/intraday_<HHMM>.json` (schema_version 1)

```json
{
  "schema_version": 1,
  "skill": "intraday-market-monitor",
  "session_date": "2026-09-11",
  "run_slot": "1020",
  "run_at_utc": "...",
  "data_asof": "2026-09-11T10:05:00-04:00",
  "data_horizon_et": "2026-09-11T10:05:00-04:00",
  "delay_minutes": 15,
  "provider": "polygon",
  "recommendation": "NEW_ENTRY_ALLOWED | REDUCE_ONLY | CASH_PRIORITY",
  "posture": {
    "recommendation": "...", "candidate": "...", "score": 63.4,
    "component_scores": {"breadth": 61.0, "index": 70.0, "sector": 58.0},
    "reason_codes": ["score>=60", "spy_above_vwap"],
    "flipped_from": null, "pending_flip": null, "streak": 2, "capped_by_daily": false
  },
  "metrics": {
    "breadth": {"available": true, "universe_size": 4300, "pct_advancers": 58.2,
                "pct_above_vwap": 61.0, "pct_above_prev_high": 22.1, "pct_below_prev_low": 9.4,
                "ud_ratio": 1.8, "volume_pace": 1.05, "elapsed_fraction": 0.24},
    "index": {"SPY": {"available": true, "last": 764.1, "vwap": 763.7, "above_vwap": true,
                      "above_prev_high": false, "below_prev_low": false, "ret_open_pct": 0.31,
                      "gap_pct": 0.2, "last_hour": {"ts_et": "...", "end_et": "...", "ret_pct": 0.1}},
              "QQQ": {...}, "IWM": {...}},
    "sectors": {"available": true, "benchmark": "SPY", "sectors": [{"symbol": "XLK", "rank": 1,
                "ret_open_pct": 0.8, "rs_open_pct": 0.5, "rs_last_hour_pct": 0.2, "above_vwap": true}],
                "risk_on_spread_pct": 0.7}
  },
  "watchlist_symbols": ["AAPL"],
  "watchlist_signals": [{"symbol": "AAPL", "available": true, "signals": ["VWAP_RECLAIM"],
                         "hourly_close": 333.1, "vwap": 332.9, "fhr_high": 334.0, "fhr_low": 330.2,
                         "gap_pct": 1.1, "rel_vol": 1.3}],
  "daily_baseline": {"recommendation": "REDUCE_ONLY", "source_file": "reports/exposure_posture_....json"},
  "warnings": [],
  "api_stats": {"provider": "polygon", "api_calls_made": 40, "cache_hits": 20},
  "narrative": {"requested": true, "written": true, "path": "reports/intraday/2026-09-11/narrative_1020.md"},
  "discord": {"posted": true, "http_status": 204, "error": null}
}
```

Downstream: `pre-trade-discipline-gate --market-regime-decision reports/intraday/latest.json`
reads the top-level `recommendation`; `exposure-coach --intraday reports/intraday/latest.json`
(when wired) reads `posture.score`.

State files: `state/intraday/<date>/slots_done.json` (ledger),
`state/intraday/last_posture.json` (hysteresis).
