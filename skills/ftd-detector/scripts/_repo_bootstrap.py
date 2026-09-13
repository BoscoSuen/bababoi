"""Put the repository root on ``sys.path`` so ``scripts.market_data`` imports work.

Mirrors ``skills/trader-memory-core/scripts/trader_memory_cli.py::find_repo_root``:
``TRADING_SKILLS_REPO_ROOT`` overrides the ``parents[3]`` guess.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

REPO_ENV = "TRADING_SKILLS_REPO_ROOT"


def repo_root() -> Path:
    env = os.environ.get(REPO_ENV)
    root = Path(env).resolve() if env else Path(__file__).resolve().parents[3]
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    return root


REPO_ROOT = repo_root()
