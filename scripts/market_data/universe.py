"""Universe lists that Polygon does not provide (index membership)."""

from __future__ import annotations

import csv
import io
from typing import Any

SP500_CSV_URL = (
    "https://raw.githubusercontent.com/datasets/s-and-p-500-companies/main/data/constituents.csv"
)


def sp500_constituents(session: Any = None, *, timeout: float = 30.0) -> list[dict] | None:
    """Public S&P 500 list → ``[{symbol, name, sector, subSector}]`` (Polygon dot
    class notation, e.g. ``BRK.B``), or ``None`` when unavailable.

    No API key is involved; a bare session is used on purpose.
    """
    try:
        if session is None:
            import requests

            session = requests
        response = session.get(SP500_CSV_URL, timeout=timeout)
        if getattr(response, "status_code", 0) != 200:
            return None
        rows = [
            {
                "symbol": row["Symbol"].strip().upper(),
                "name": row.get("Security", ""),
                "sector": row.get("GICS Sector", ""),
                "subSector": row.get("GICS Sub-Industry", ""),
            }
            for row in csv.DictReader(io.StringIO(response.text))
            if row.get("Symbol")
        ]
    except Exception:
        return None
    return rows or None
