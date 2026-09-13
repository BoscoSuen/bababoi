"""Thin Polygon price adapter for MAE/MFE calculation.

Single-purpose: fetch daily closes (oldest first) through the shared
``scripts/market_data`` layer. Duck-typed into
``thesis_review.compute_mae_mfe(thesis, price_adapter=...)``.
"""

from __future__ import annotations

import os
from datetime import date

import _repo_bootstrap  # noqa: F401  (repo root → scripts.market_data)

from scripts.market_data import get_provider


class PolygonPriceAdapter:
    """Fetch daily (dividend-adjusted) closes from Polygon."""

    def __init__(
        self,
        api_key: str | None = None,
        *,
        provider=None,
        fixture_dir: str | None = None,
    ):
        if provider is None:
            if fixture_dir:
                provider = get_provider("fixture", fixture_dir=fixture_dir)
            else:
                key = api_key or os.environ.get("POLYGON_API_KEY")
                if not key:
                    raise ValueError(
                        "Polygon API key required. Set POLYGON_API_KEY env var or pass api_key."
                    )
                provider = get_provider("polygon", api_key=key)
        self.provider = provider

    def get_daily_closes(self, ticker: str, from_date: str, to_date: str) -> list[dict]:
        """Return ``[{"date": "YYYY-MM-DD", "close": float}]`` oldest first.

        ``close`` is the dividend-adjusted close (``adjClose``) so MAE/MFE
        are total-return excursions; falls back to the raw close.
        """
        bars = self.provider.daily_bars(
            ticker, date.fromisoformat(from_date[:10]), date.fromisoformat(to_date[:10])
        )
        return [{"date": b["date"], "close": b.get("adjClose") or b["close"]} for b in bars]


# Backwards-compatible alias for callers written against the FMP-era name.
FMPPriceAdapter = PolygonPriceAdapter
