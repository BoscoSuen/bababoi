#!/bin/bash
# Thin launcher for launchd → skills/intraday-market-monitor/scripts/intraday_monitor.py
#
# Runs in the primary working tree (read-only with respect to git; it only writes
# reports/, state/, logs/ and .cache/). Secrets come from the gitignored .envrc:
#   export POLYGON_API_KEY=...
#   export DISCORD_MARKET_REPORT_URL=...
#
# Install:  see launchd/com.trade-analysis.intraday-monitor.plist
# Manual:   bash scripts/run_intraday_monitor.sh                # --auto-slot
#           bash scripts/run_intraday_monitor.sh --slot 1020 --no-discord

set -o pipefail

export PATH="/opt/homebrew/bin:/opt/homebrew/sbin:${HOME}/.local/bin:/usr/local/bin:$PATH"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${PROJECT_DIR}" || exit 1
mkdir -p logs

# Load secrets. direnv is optional; a plain `export` .envrc sources fine.
if command -v direnv >/dev/null 2>&1 && [ -f .envrc ]; then
    eval "$(direnv export bash 2>/dev/null)"
elif [ -f .envrc ]; then
    set -a
    # shellcheck disable=SC1091
    . ./.envrc
    set +a
fi

if [ -x "${PROJECT_DIR}/.venv/bin/python" ]; then
    PY="${PROJECT_DIR}/.venv/bin/python"
else
    PY="$(command -v python3)"
fi

if [ "$#" -eq 0 ]; then
    set -- --auto-slot
fi

echo "[$(date '+%Y-%m-%dT%H:%M:%S%z')] intraday-monitor start: $*"
"${PY}" "${PROJECT_DIR}/skills/intraday-market-monitor/scripts/intraday_monitor.py" run "$@"
rc=$?
echo "[$(date '+%Y-%m-%dT%H:%M:%S%z')] intraday-monitor exit ${rc}"
exit ${rc}
