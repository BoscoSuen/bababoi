"""Shared market-data layer (Polygon.io Starter) for trading skills.

Skills import this package via a small ``_repo_bootstrap.py`` that puts the
repository root on ``sys.path``::

    import _repo_bootstrap  # noqa: F401
    from scripts.market_data import get_provider
    from scripts.market_data.legacy import PolygonCompatClient

Providers:
- ``polygon``  – live Polygon REST (``POLYGON_API_KEY``), with an on-disk cache
- ``fixture``  – offline replay from a directory laid out exactly like the cache

The canonical bar shape is ascending (oldest first). ``legacy.PolygonCompatClient``
re-exposes the historical FMP shapes (descending ``{"symbol", "historical"}``)
so migrated skills change as little as possible.
"""

from __future__ import annotations

import os
from pathlib import Path

from scripts.market_data.cache import DiskCache
from scripts.market_data.polygon import PolygonProvider
from scripts.market_data.provider import MarketDataProvider, NotAvailable, ProviderError

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CACHE_DIR = REPO_ROOT / ".cache" / "market_data"
API_KEY_ENV = "POLYGON_API_KEY"

__all__ = [
    "API_KEY_ENV",
    "DEFAULT_CACHE_DIR",
    "MarketDataProvider",
    "NotAvailable",
    "PolygonProvider",
    "ProviderError",
    "get_provider",
    "resolve_api_key",
]


def resolve_api_key(cli_key: str | None = None) -> str | None:
    """``--api-key`` wins, then ``POLYGON_API_KEY``; ``None`` when neither is set."""
    return cli_key or os.environ.get(API_KEY_ENV) or None


def get_provider(
    name: str = "polygon",
    *,
    api_key: str | None = None,
    fixture_dir: os.PathLike | None = None,
    cache_dir: os.PathLike | None = None,
    use_cache: bool = True,
) -> MarketDataProvider:
    """Build a provider by name.

    ``polygon`` needs an API key (argument or ``POLYGON_API_KEY``). ``fixture``
    replays a recorded cache directory and never touches the network.
    """
    if name == "fixture":
        if fixture_dir is None:
            raise ValueError("fixture provider requires fixture_dir")
        return PolygonProvider(api_key=None, cache=DiskCache(Path(fixture_dir)), offline=True)
    if name == "polygon":
        key = resolve_api_key(api_key)
        if not key:
            raise ValueError(f"Polygon API key required. Set {API_KEY_ENV} or pass --api-key.")
        cache = (
            DiskCache(Path(cache_dir) if cache_dir else DEFAULT_CACHE_DIR) if use_cache else None
        )
        return PolygonProvider(api_key=key, cache=cache)
    raise ValueError(f"unknown provider: {name!r} (use 'polygon' or 'fixture')")
