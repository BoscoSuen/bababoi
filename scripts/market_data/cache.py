"""On-disk JSON cache keyed by endpoint + canonical params.

Layout (shared with the fixture/replay provider)::

    <root>/<endpoint>/<sha1(canonical params)>.json
    {"meta": {"endpoint", "params", "fetched_at", "immutable"}, "payload": {...}}

Immutable entries (history fully in the past) never expire; mutable ones
(today's bars, snapshots) expire after ``ttl_seconds`` unless the caller
asks for a specific replay key.
"""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
import time
from pathlib import Path
from typing import Any


def canonical_key(params: dict | None) -> str:
    blob = json.dumps(params or {}, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha1(blob.encode("utf-8")).hexdigest()  # noqa: S324 - not security


class DiskCache:
    def __init__(self, root: Path, *, ttl_seconds: float = 900.0, clock=time.time) -> None:
        self.root = Path(root)
        self.ttl_seconds = ttl_seconds
        self._clock = clock
        self.hits = 0
        self.misses = 0

    def path_for(self, endpoint: str, params: dict | None) -> Path:
        return self.root / endpoint / f"{canonical_key(params)}.json"

    def get(self, endpoint: str, params: dict | None) -> Any | None:
        path = self.path_for(endpoint, params)
        if not path.is_file():
            self.misses += 1
            return None
        try:
            with path.open("r", encoding="utf-8") as fh:
                doc = json.load(fh)
        except (OSError, ValueError):
            self.misses += 1
            return None
        meta = doc.get("meta") or {}
        if not meta.get("immutable", False):
            age = self._clock() - float(meta.get("fetched_at", 0))
            if age > self.ttl_seconds:
                self.misses += 1
                return None
        self.hits += 1
        return doc.get("payload")

    def put(self, endpoint: str, params: dict | None, payload: Any, *, immutable: bool) -> Path:
        path = self.path_for(endpoint, params)
        path.parent.mkdir(parents=True, exist_ok=True)
        doc = {
            "meta": {
                "endpoint": endpoint,
                "params": params or {},
                "fetched_at": self._clock(),
                "immutable": bool(immutable),
            },
            "payload": payload,
        }
        fd, tmp = tempfile.mkstemp(prefix=".tmp-", dir=str(path.parent))
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as fh:
                json.dump(doc, fh, sort_keys=True)
            os.replace(tmp, path)
        finally:
            if os.path.exists(tmp):
                os.unlink(tmp)
        return path
