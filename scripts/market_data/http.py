"""Thin HTTP layer for Polygon: Bearer auth, pacing, retry, paging, redaction."""

from __future__ import annotations

import re
import time
from typing import Any

from scripts.market_data.provider import NotAvailable, ProviderError

POLYGON_BASE_URL = "https://api.polygon.io"

# Belt and braces: the key is sent as a header, but redact any query-style
# leak (apiKey=...) and the literal secret from anything we might print.
_APIKEY_PATTERNS = (
    re.compile(r"api_?key\s*=\s*[^&\s'\"]+", re.IGNORECASE),
    re.compile(r"api_?key%3d[^&\s'\"]+", re.IGNORECASE),
)


def redact(text: str | None, secret: str | None = None) -> str | None:
    """Mask the API key in an error string."""
    if not text:
        return text
    if secret:
        text = text.replace(secret, "***REDACTED***")
    for pattern in _APIKEY_PATTERNS:
        text = pattern.sub("apiKey=***REDACTED***", text)
    return text


class HttpClient:
    """GET JSON from Polygon with polite pacing and bounded retries.

    ``session`` is duck-typed (``get(url, params=, headers=, timeout=)``
    returning an object with ``status_code``, ``text``, ``json()`` and
    ``headers``) so tests inject a fake without ``requests``.
    """

    def __init__(
        self,
        api_key: str | None,
        *,
        session: Any = None,
        base_url: str = POLYGON_BASE_URL,
        timeout: float = 30.0,
        min_interval: float = 0.1,
        max_retries: int = 3,
        sleep=time.sleep,
    ) -> None:
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.min_interval = min_interval
        self.max_retries = max_retries
        self._sleep = sleep
        self._session = session
        self._last_call = 0.0
        self.calls_made = 0

    # -- session -----------------------------------------------------------
    @property
    def session(self):
        if self._session is None:
            import requests  # lazy: fixture/offline paths never need it

            self._session = requests.Session()
        return self._session

    def _headers(self) -> dict[str, str]:
        headers = {"Accept": "application/json", "User-Agent": "trading-skills/market_data"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    # -- core --------------------------------------------------------------
    def get_json(self, path_or_url: str, params: dict | None = None) -> dict:
        """Single GET (no paging). Raises ``NotAvailable`` on 401/403/404,
        ``ProviderError`` on other failures after retries."""
        url = path_or_url if path_or_url.startswith("http") else f"{self.base_url}{path_or_url}"
        delay = 1.0
        last_error = "unknown error"
        for attempt in range(self.max_retries + 1):
            self._pace()
            try:
                resp = self.session.get(
                    url, params=params or {}, headers=self._headers(), timeout=self.timeout
                )
                self.calls_made += 1
            except Exception as exc:  # requests.RequestException or fake errors
                last_error = redact(str(exc), self.api_key) or "request failed"
                if attempt < self.max_retries:
                    self._sleep(delay)
                    delay *= 2
                    continue
                raise ProviderError(f"GET {self._short(url)} failed: {last_error}") from None

            status = getattr(resp, "status_code", 0)
            if status == 200:
                try:
                    return resp.json()
                except ValueError as exc:
                    raise ProviderError(f"GET {self._short(url)}: invalid JSON ({exc})") from None
            if status in (401, 403):
                raise NotAvailable(
                    f"GET {self._short(url)}: {status} not entitled: "
                    f"{redact(self._message(resp), self.api_key)}"
                )
            if status == 404:
                raise NotAvailable(f"GET {self._short(url)}: 404 not found")
            if status == 429 or status >= 500:
                last_error = f"HTTP {status}"
                if attempt < self.max_retries:
                    retry_after = self._retry_after(resp)
                    self._sleep(retry_after if retry_after is not None else delay)
                    delay *= 2
                    continue
                raise ProviderError(f"GET {self._short(url)}: {last_error} after retries")
            raise ProviderError(
                f"GET {self._short(url)}: HTTP {status}: {redact(self._message(resp), self.api_key)}"
            )
        raise ProviderError(f"GET {self._short(url)}: {last_error}")  # pragma: no cover

    def get_paged(self, path: str, params: dict | None = None, *, key: str = "results") -> dict:
        """GET and follow ``next_url`` until exhausted, concatenating ``key``."""
        first = self.get_json(path, params)
        rows = list(first.get(key) or [])
        next_url = first.get("next_url")
        guard = 0
        while next_url and guard < 200:
            page = self.get_json(next_url, None)
            rows.extend(page.get(key) or [])
            next_url = page.get("next_url")
            guard += 1
        first[key] = rows
        first.pop("next_url", None)
        return first

    # -- helpers -----------------------------------------------------------
    def _pace(self) -> None:
        if self.min_interval <= 0:
            return
        now = time.monotonic()
        wait = self.min_interval - (now - self._last_call)
        if wait > 0:
            self._sleep(wait)
        self._last_call = time.monotonic()

    @staticmethod
    def _retry_after(resp) -> float | None:
        try:
            value = resp.headers.get("Retry-After") if getattr(resp, "headers", None) else None
            return float(value) if value else None
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _message(resp) -> str:
        try:
            body = resp.json()
            if isinstance(body, dict):
                return str(body.get("message") or body.get("error") or "")[:200]
        except Exception:
            pass
        text = getattr(resp, "text", "") or ""
        return text[:200]

    @staticmethod
    def _short(url: str) -> str:
        return url.split("?", 1)[0]
