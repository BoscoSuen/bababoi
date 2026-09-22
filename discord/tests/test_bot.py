"""Tests for the pure helpers in discord/bot.py."""

import sys
from pathlib import Path

# The repo has a top-level ``discord/`` folder that shadows the discord.py
# package when the repo root is on sys.path (pytest rootdir conftest). Drop it
# and any namespace-package import of it so ``bot`` picks up the real library.
_REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path[:] = [p for p in sys.path if Path(p or ".").resolve() != _REPO_ROOT]
sys.modules.pop("discord", None)
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import bot  # noqa: E402


def test_strip_mention_handles_both_mention_forms():
    assert bot.strip_mention("<@123> hello", 123) == "hello"
    assert bot.strip_mention("<@!123>   hello", 123) == "hello"
    assert bot.strip_mention("<@999> hello", 123) == "<@999> hello"


def test_owner_id_from_env():
    assert bot.owner_id_from_env({}) is None
    assert bot.owner_id_from_env({"DISCORD_OWNER_ID": ""}) is None
    assert bot.owner_id_from_env({"DISCORD_OWNER_ID": " 42 "}) == 42


def test_is_authorized():
    assert bot.is_authorized(1, None)
    assert bot.is_authorized(42, 42)
    assert not bot.is_authorized(1, 42)


def test_claude_argv_includes_allowed_tools():
    argv = bot.claude_argv("hi")
    assert argv[:3] == ["claude", "-p", "hi"]
    assert "--allowedTools" in argv
    tools = argv[argv.index("--allowedTools") + 1]
    assert "WebSearch" in tools
    assert "Bash(python3 skills/*)" in tools
    assert "--dangerously-skip-permissions" not in argv


def test_format_failure_shows_stdout_and_stderr():
    msg = bot.format_failure(1, "Failed to authenticate: expired\n", "")
    assert "claude exited 1" in msg
    assert "Failed to authenticate" in msg
    msg = bot.format_failure(1, "", "")
    assert "(no output)" in msg


def test_is_auth_failure():
    assert bot.is_auth_failure("Failed to authenticate: OAuth session expired", "")
    assert not bot.is_auth_failure("some other error", "")
