#!/bin/bash
# Thin launcher for launchd → daily post-market tasks.
#
# Currently runs:
#   1. Swing daily signal to Discord (5 PM ET on trading days)
#
# Secrets come from the gitignored .envrc:
#   export POLYGON_API_KEY=...
#   export DISCORD_SWING_SIGNAL_URL=...
#
# Install:  see launchd/com.trade-analysis.daily-tasks.plist
# Manual:   bash scripts/run_daily_tasks.sh

set -o pipefail

export PATH="/opt/homebrew/bin:/opt/homebrew/sbin:${HOME}/.local/bin:/usr/local/bin:$PATH"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${PROJECT_DIR}" || exit 1
mkdir -p logs

# Load secrets.
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

MODE="${1:---auto}"

echo "[$(date '+%Y-%m-%dT%H:%M:%S%z')] daily-tasks start: swing signal ($MODE)"
"${PY}" "${PROJECT_DIR}/scripts/send_swing_signal.py" "${MODE}"
rc=$?
echo "[$(date '+%Y-%m-%dT%H:%M:%S%z')] swing signal exit ${rc}"

# Future daily tasks go here:
# echo "[$(date '+%Y-%m-%dT%H:%M:%S%z')] daily-tasks: next task..."
# "${PY}" "${PROJECT_DIR}/scripts/next_task.py" "${MODE}"

exit ${rc}
