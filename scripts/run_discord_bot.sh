#!/bin/bash
# launchd → discord/bot.py. Sources .envrc for DISCORD_BOT_TOKEN, then exec so
# launchd tracks the python process itself (no nohup, no pid file).
#
# Install:  see launchd/com.trade-analysis.discord-bot.plist
# Manual:   bash scripts/run_discord_bot.sh

set -o pipefail
export PATH="/opt/homebrew/bin:/opt/homebrew/sbin:${HOME}/.local/bin:/usr/local/bin:$PATH"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${PROJECT_DIR}" || exit 1
mkdir -p logs

if [ -f .envrc ]; then
    set -a
    # shellcheck disable=SC1091
    . ./.envrc
    set +a
fi
: "${DISCORD_BOT_TOKEN:?DISCORD_BOT_TOKEN not set (put it in .envrc)}"

echo "[$(date '+%Y-%m-%dT%H:%M:%S%z')] discord-bot start"
exec "${PROJECT_DIR}/.venv/bin/python" "${PROJECT_DIR}/discord/bot.py"
