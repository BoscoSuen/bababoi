"""Market-data wrapper + OHLCV quality validation (Polygon via scripts/market_data).

Returns most-recent-first list[dict] (no pandas). Records data quality
issues as audit_flags / skipped_sessions for the report layer.
"""

from __future__ import annotations

from typing import Any


def normalize_history(payload: Any) -> list[dict]:
    """Coerce provider payload variants into a flat most-recent-first list[dict].

    - dict with "historical" key (legacy FMP v3 / PolygonCompatClient shape)
    - list (flat most-recent-first rows): return as-is
    - None or unrecognized shape: return []
    """
    if payload is None:
        return []
    if isinstance(payload, dict):
        return list(payload.get("historical") or [])
    if isinstance(payload, list):
        return list(payload)
    return []


def validate_history_quality(history: list[dict]) -> tuple[list[str], list[dict]]:
    """Identify data quality problems.

    Returns (audit_flags, skipped_sessions). Each skipped session has
    {date, reason}. The caller's downstream code is expected to treat
    skipped sessions as no-op (no DD detection / enrichment for them).
    """
    flags: list[str] = []
    skipped: list[dict] = []
    for row in history:
        date = row.get("date")
        close = row.get("close")
        volume = row.get("volume")

        if close is None:
            skipped.append({"date": date, "reason": "missing_close"})
        elif close <= 0:
            skipped.append({"date": date, "reason": "invalid_close"})

        if volume is None:
            skipped.append({"date": date, "reason": "missing_volume"})
        elif volume <= 0:
            skipped.append({"date": date, "reason": "invalid_volume"})

    if skipped:
        flags.append("data_quality_warnings")
    return flags, skipped


def fetch_ohlcv(
    client: Any,
    symbol: str,
    days: int,
) -> tuple[list[dict], dict]:
    """Fetch most-recent-first OHLCV for `symbol` via the provided market-data client.

    Returns (history, audit) where audit has:
        - data_source: provider name (e.g. "polygon", "fixture")
        - symbol: str
        - days_requested: int
        - sessions_loaded: int
        - audit_flags: list[str]
        - skipped_sessions: list[dict]
    """
    audit: dict = {
        "data_source": _data_source(client),
        "symbol": symbol,
        "days_requested": days,
        "sessions_loaded": 0,
        "audit_flags": [],
        "skipped_sessions": [],
    }

    payload = client.get_historical_prices(symbol, days=days)
    history = normalize_history(payload)

    if not history:
        audit["audit_flags"].append("no_data_returned")
        return [], audit

    flags, skipped = validate_history_quality(history)
    audit["sessions_loaded"] = len(history)
    audit["audit_flags"].extend(flags)
    audit["skipped_sessions"] = skipped
    return history, audit


def _data_source(client: Any) -> str:
    getter = getattr(client, "get_data_mode", None)
    try:
        value = getter() if callable(getter) else None
    except Exception:
        value = None
    return value if isinstance(value, str) and value else "polygon"


def build_market_data_client(
    api_key: str | None = None,
    max_api_calls: int = 200,
    *,
    fixture_dir: str | None = None,
):
    """Lazy import so unit tests that mock the client never touch scripts/market_data."""
    import _repo_bootstrap  # noqa: F401

    from scripts.market_data.legacy import PolygonCompatClient

    if fixture_dir:
        return PolygonCompatClient(fixture_dir=fixture_dir, max_api_calls=max_api_calls)
    return PolygonCompatClient(api_key=api_key, max_api_calls=max_api_calls)


# Backwards-compatible alias for callers written against the FMP-era name.
build_fmp_client = build_market_data_client
