from __future__ import annotations

import json
import subprocess
from pathlib import Path

import discord_notify
import intraday_monitor as cli
import narrative
import pytest
from fake_provider import FakeProvider

NOW = "2026-09-11T10:20:00-04:00"


class _Resp:
    def __init__(self, status, headers=None):
        self.status_code = status
        self.headers = headers or {}


class _Session:
    def __init__(self, statuses):
        self.statuses = list(statuses)
        self.posts = []

    def post(self, url, json=None, timeout=None):
        self.posts.append(json["content"])
        status = self.statuses.pop(0) if len(self.statuses) > 1 else self.statuses[0]
        return _Resp(status, {"Retry-After": "1"} if status == 429 else None)


def test_discord_post_success_retry_and_missing_url(monkeypatch):
    slept = []
    ok = _Session([204])
    assert (
        discord_notify.post("hi", url="https://x/hook", session=ok, sleep=slept.append)["posted"]
        is True
    )
    flaky = _Session([429, 204])
    out = discord_notify.post("hi", url="https://x/hook", session=flaky, sleep=slept.append)
    assert out["posted"] is True and slept == [1.0]
    bad = _Session([400])
    assert (
        discord_notify.post("hi", url="https://x/hook", session=bad, sleep=slept.append)[
            "http_status"
        ]
        == 400
    )
    monkeypatch.delenv("DISCORD_MARKET_REPORT_URL", raising=False)
    assert discord_notify.post("hi")["posted"] is False


def test_narrative_should_run_and_runner(tmp_path):
    assert narrative.should_run("auto", "1020", ["1020", "1520"], False)
    assert not narrative.should_run("auto", "1120", ["1020", "1520"], False)
    assert narrative.should_run("auto", "1120", ["1020", "1520"], True)
    assert narrative.should_run("always", "1120", [], False) and not narrative.should_run(
        "never", "1020", ["1020"], True
    )

    def fake_runner(cmd, **kw):
        assert cmd[1] == "-p" and "{{CURRENT_JSON}}" not in cmd[2]
        return subprocess.CompletedProcess(cmd, 0, stdout="Posture holds.\n", stderr="")

    prompt = narrative.build_prompt(
        {"recommendation": "REDUCE_ONLY", "narrative": {}, "discord": {}}, None, None
    )
    assert '"recommendation": "REDUCE_ONLY"' in prompt and "{{" not in prompt
    out = narrative.run_claude(prompt, tmp_path / "n.md", runner=fake_runner)
    assert out["written"] and (tmp_path / "n.md").read_text() == "Posture holds.\n"

    def failing(cmd, **kw):
        return subprocess.CompletedProcess(cmd, 1, stdout="", stderr="boom")

    assert narrative.run_claude(prompt, tmp_path / "n2.md", runner=failing)["written"] is False
    assert (
        narrative.run_claude(prompt, tmp_path / "n3.md", claude_bin="/definitely/missing")[
            "written"
        ]
        is False
    )


@pytest.fixture
def env(tmp_path, monkeypatch):
    monkeypatch.setattr(cli, "build_provider", lambda args, cfg: FakeProvider())
    monkeypatch.setattr(cli, "REPO_ROOT", tmp_path)  # no daily baseline, watchlist under tmp
    out = tmp_path / "reports" / "intraday"
    state = tmp_path / "state" / "intraday"
    wl = tmp_path / "state" / "daily_watchlist.json"
    wl.parent.mkdir(parents=True)
    wl.write_text(
        '{"date": "2026-09-11", "symbols": [{"symbol": "AAPL", "pivot": 1.0}, "XLK"]}',
        encoding="utf-8",
    )
    return {"out": out, "state": state}


def _run(env, slot, extra=()):
    return cli.main(
        [
            "run",
            "--slot",
            slot,
            "--now-et",
            NOW.replace("10:20", f"{slot[:2]}:{slot[2:]}"),
            "--output-dir",
            str(env["out"]),
            "--state-dir",
            str(env["state"]),
            "--no-discord",
            "--narrative",
            "never",
            *extra,
        ]
    )


def test_cli_end_to_end_writes_reports_and_state(env):
    assert _run(env, "1020") == 0
    day = env["out"] / "2026-09-11"
    payload = json.loads((day / "intraday_1020.json").read_text())
    assert payload["recommendation"] in ("NEW_ENTRY_ALLOWED", "REDUCE_ONLY", "CASH_PRIORITY")
    assert payload["data_horizon_et"] == "2026-09-11T10:05:00-04:00"
    assert (
        payload["metrics"]["breadth"]["available"]
        and payload["metrics"]["breadth"]["universe_size"] > 0
    )
    assert payload["metrics"]["index"]["SPY"]["available"]
    assert payload["metrics"]["sectors"]["available"] and payload["metrics"]["sectors"]["sectors"]
    assert [w["symbol"] for w in payload["watchlist_signals"]] == ["AAPL", "XLK"]
    assert payload["watchlist_signals"][0]["pivot"] == 1.0
    assert payload["discord"]["posted"] is False and payload["narrative"]["requested"] is False
    assert (day / "intraday_1020.md").is_file() and (env["out"] / "latest.json").is_file()
    assert json.loads((env["state"] / "2026-09-11" / "slots_done.json").read_text())["done"] == [
        "1020"
    ]
    assert json.loads((env["state"] / "last_posture.json").read_text())["run_slot"] == "1020"
    md = (day / "intraday_1020.md").read_text()
    assert "Not a trade signal" in md and "Sector relative strength" in md
    summary = discord_notify.format_summary(payload)
    assert summary.startswith("**Intraday Monitor** 2026-09-11 10:20 ET") and len(summary) <= 1900


def test_cli_slot_ledger_blocks_rerun_and_force_overrides(env, capsys):
    assert _run(env, "1120") == 0
    assert _run(env, "1120") == 0
    assert "already ran" in capsys.readouterr().out
    assert _run(env, "1120", ["--force"]) == 0


def test_cli_non_session_day_and_unknown_slot(env, capsys):
    rc = cli.main(
        [
            "run",
            "--slot",
            "1020",
            "--now-et",
            "2026-09-12T10:20:00-04:00",
            "--output-dir",
            str(env["out"]),
            "--state-dir",
            str(env["state"]),
            "--no-discord",
            "--narrative",
            "never",
        ]
    )
    assert rc == 0 and "not an XNYS session" in capsys.readouterr().out
    assert _run(env, "1000") == 1


def test_cli_auto_slot_picks_latest_pending(env, capsys):
    rc = cli.main(
        [
            "run",
            "--auto-slot",
            "--now-et",
            "2026-09-11T13:45:00-04:00",
            "--output-dir",
            str(env["out"]),
            "--state-dir",
            str(env["state"]),
            "--no-discord",
            "--narrative",
            "never",
        ]
    )
    assert rc == 0
    assert (env["out"] / "2026-09-11" / "intraday_1320.json").is_file()
    rc = cli.main(
        [
            "run",
            "--auto-slot",
            "--now-et",
            "2026-09-11T13:35:00-04:00",
            "--output-dir",
            str(env["out"]),
            "--state-dir",
            str(env["state"]),
            "--no-discord",
            "--narrative",
            "never",
        ]
    )
    assert rc == 0 and "no due slot pending" in capsys.readouterr().out


def test_cli_degrades_when_full_snapshot_fails(env, monkeypatch):
    monkeypatch.setattr(cli, "build_provider", lambda args, cfg: FakeProvider(fail_snapshot=True))
    assert _run(env, "1220") == 0
    payload = json.loads((env["out"] / "2026-09-11" / "intraday_1220.json").read_text())
    assert payload["metrics"]["breadth"]["available"] is False
    assert any("snapshot unavailable" in w for w in payload["warnings"])
    assert payload["metrics"]["index"]["SPY"]["available"]  # bars path still works


def test_replay_runs_every_slot(env):
    rc = cli.main(
        [
            "replay",
            "--date",
            "2026-09-11",
            "--output-dir",
            str(env["out"]),
            "--state-dir",
            str(env["state"]),
        ]
    )
    assert rc == 0
    files = sorted(p.name for p in (env["out"] / "2026-09-11").glob("intraday_*.json"))
    assert (
        len(files) == 14
        and files[0] == "intraday_0950.json"
        and files[-1] == "intraday_1620.json"
    )
    Path(env["out"] / "latest.json").is_file()
