"""Tests for the pure helpers in discord/bot.py."""

import json
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


def _system_prompt(argv):
    return argv[argv.index("--append-system-prompt") + 1]


def test_claude_argv_always_appends_base_system_prompt():
    sys_prompt = _system_prompt(bot.claude_argv("hi"))
    assert sys_prompt == bot.BASE_SYSTEM_PROMPT
    sys_prompt = _system_prompt(bot.claude_argv("hi", "EXTRA"))
    assert sys_prompt.startswith(bot.BASE_SYSTEM_PROMPT)
    assert sys_prompt.endswith("EXTRA")


def test_claude_argv_requests_json_output():
    argv = bot.claude_argv("hi")
    assert argv[argv.index("--output-format") + 1] == "json"


def test_base_system_prompt_steers_to_skill_scripts():
    p = bot.BASE_SYSTEM_PROMPT
    assert "python3 skills/<name>/scripts/" in p
    assert "POLYGON_API_KEY" in p
    assert "One command per Bash call" in p
    assert "reports/" in p


def test_safe_filename():
    assert bot.safe_filename("../../etc/passwd") == "passwd"
    assert bot.safe_filename("GS Flow: of Funds.pdf") == "GS Flow_ of Funds.pdf"
    assert bot.safe_filename("周前瞻.pdf") == "周前瞻.pdf"
    assert bot.safe_filename("") == "file"


def test_build_prompt():
    assert bot.build_prompt("hi", []) == "hi"
    out = bot.build_prompt("分析", [".cache/files/1/a.pdf"])
    assert out.startswith("分析\n\nAttached files")
    assert "- .cache/files/1/a.pdf" in out
    assert bot.build_prompt("", ["x.pdf"]).startswith(bot.DEFAULT_ATTACHMENT_PROMPT)


def test_attachment_system_prompt_points_at_read_pdf():
    assert "skills/read-pdf/scripts/pdf_to_md.py" in bot.ATTACHMENT_SYSTEM_PROMPT


def test_prune_uploads(tmp_path):
    old = tmp_path / "1"
    new = tmp_path / "2"
    old.mkdir()
    new.mkdir()
    import os

    os.utime(old, (0, 0))
    bot.prune_uploads(str(tmp_path), ttl_sec=60)
    assert not old.exists()
    assert new.exists()


def test_claude_argv_includes_allowed_tools():
    argv = bot.claude_argv("hi")
    assert argv[:3] == ["claude", "-p", "hi"]
    assert "--allowedTools" in argv
    tools = argv[argv.index("--allowedTools") + 1]
    assert "WebSearch" in tools
    assert "Bash(python3 skills/*)" in tools
    assert "--dangerously-skip-permissions" not in argv


def test_allowed_tools_cover_skills_but_not_arbitrary_code():
    tools = bot.ALLOWED_TOOLS.split(",")
    for expected in (
        "Read",
        "Glob",
        "Grep",
        "WebSearch",
        "WebFetch",
        "Bash(python3 skills/*)",
        "Bash(python skills/*)",
        "Bash(uv run skills/*)",
        "Edit(reports/**)",
        "Bash(mkdir -p reports/*)",
        "Agent",
    ):
        assert expected in tools
    for forbidden in ("Write", "Edit", "Bash", "Bash(python3 scripts/*)", "Bash(python3 *)"):
        assert forbidden not in tools


def test_format_failure_shows_stdout_and_stderr():
    msg = bot.format_failure(1, "Failed to authenticate: expired\n", "")
    assert "claude exited 1" in msg
    assert "Failed to authenticate" in msg
    msg = bot.format_failure(1, "", "")
    assert "(no output)" in msg


def test_is_auth_failure():
    assert bot.is_auth_failure("Failed to authenticate: OAuth session expired", "")
    assert not bot.is_auth_failure("some other error", "")


def test_parse_claude_json():
    out = json.dumps(
        {
            "result": "answer",
            "is_error": False,
            "permission_denials": [
                {"tool_name": "Bash", "tool_input": {"command": "env | wc -l"}},
            ],
        }
    )
    data = bot.parse_claude_json(out)
    assert data["result"] == "answer"
    assert bot.parse_claude_json("Failed to authenticate") is None
    assert bot.parse_claude_json("") is None
    assert bot.parse_claude_json("[1, 2]") is None


def test_summarize_denial():
    bash = {"tool_name": "Bash", "tool_input": {"command": "env | wc -l"}}
    assert bot.summarize_denial(bash) == "Bash: env | wc -l"
    write = {"tool_name": "Write", "tool_input": {"file_path": "/tmp/x.py", "content": "..."}}
    assert bot.summarize_denial(write) == "Write: /tmp/x.py"
    long = bot.summarize_denial({"tool_name": "Bash", "tool_input": {"command": "x" * 500}})
    assert len(long) <= 130
    assert bot.summarize_denial({}) == "?: "


def test_denial_footer():
    assert bot.denial_footer([]) == ""
    footer = bot.denial_footer(
        [
            {"tool_name": "Bash", "tool_input": {"command": "env"}},
            {"tool_name": "Write", "tool_input": {"file_path": "/tmp/a.py"}},
        ]
    )
    assert "2 tool call(s) denied" in footer
    assert "Bash: env" in footer
    assert "Write: /tmp/a.py" in footer


def test_render_result_success_with_denials(capsys):
    out = json.dumps(
        {
            "result": "the answer",
            "is_error": False,
            "permission_denials": [{"tool_name": "Bash", "tool_input": {"command": "env"}}],
        }
    )
    text = bot.render_result(0, out, "")
    assert text.startswith("the answer")
    assert "1 tool call(s) denied" in text
    assert "permission denied: Bash: env" in capsys.readouterr().out


def test_render_result_plain_text_fallback():
    assert bot.render_result(0, "  plain  \n", "") == "plain"


def test_render_result_errors():
    err = json.dumps({"result": "API Error: boom", "is_error": True, "permission_denials": []})
    assert "API Error: boom" in bot.render_result(0, err, "")
    assert "claude exited 1" in bot.render_result(1, err, "")
    assert "Failed to authenticate" in bot.render_result(1, "Failed to authenticate", "")


def test_claude_argv_pins_exact_model():
    argv = bot.claude_argv("hi")
    # Pinned ID, not the `opus` alias, which silently moves with CLI updates.
    assert argv[argv.index("--model") + 1] == "claude-opus-5-5"
