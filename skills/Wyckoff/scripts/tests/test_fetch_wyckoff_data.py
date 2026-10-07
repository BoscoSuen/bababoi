"""Data-boundary and offline integration tests; no live API calls."""

import json
import subprocess
import sys
from datetime import date, datetime, timezone

import pytest

import fetch_wyckoff_data as fetch
from scripts.market_data.cache import DiskCache
from scripts.market_data.http import HttpClient


def bar(day="2024-01-04", **changes):
    row = dict(date=day, open=100, high=105, low=98, close=103, volume=1000, adjClose=70)
    return {**row, **changes}


def test_cutoff_day_is_excluded_even_after_close():
    cutoff = fetch.parse_as_of("2024-01-05T23:00:00-05:00")
    rows, warnings = fetch.prepare_bars(
        [bar("2024-01-05"), bar(), bar("2024-01-03")], date(2024, 1, 4), cutoff
    )
    assert [x["date"] for x in rows] == ["2024-01-04"]
    assert rows[0]["close"] == 103
    assert "adjClose" not in rows[0]
    assert warnings == []


def test_cutoff_uses_new_york_date_not_utc_date():
    cutoff = fetch.parse_as_of("2024-01-05T02:00:00Z")
    assert fetch.request_end(cutoff) == date(2024, 1, 3)


@pytest.mark.parametrize("value", ["2024-01-05", "2024-01-05T12:00:00", "invalid"])
def test_cutoff_requires_explicit_timezone(value):
    with pytest.raises(ValueError):
        fetch.parse_as_of(value)


@pytest.mark.parametrize("changes", [
    {"close": 110}, {"low": 106}, {"volume": -1}, {"volume": None},
    {"close": float("nan")}, {"open": float("inf")}, {"volume": True},
])
def test_invalid_in_range_data_is_rejected(changes):
    with pytest.raises(ValueError):
        fetch.prepare_bars([bar(**changes)], date(2024, 1, 1), fetch.parse_as_of("2024-01-05T12:00:00Z"))


def test_duplicate_dates_are_rejected_not_silently_deduplicated():
    with pytest.raises(ValueError, match="duplicate"):
        fetch.prepare_bars([bar(), bar()], date(2024, 1, 1), fetch.parse_as_of("2024-01-05T12:00:00Z"))


def test_zero_volume_is_preserved_and_flagged():
    rows, warnings = fetch.prepare_bars([bar(volume=0)], date(2024, 1, 1), fetch.parse_as_of("2024-01-05T12:00:00Z"))
    assert rows[0]["volume"] == 0
    assert warnings


def test_no_eligible_bars_is_failure():
    with pytest.raises(ValueError, match="No completed"):
        fetch.prepare_bars([bar("2024-01-05")], date(2024, 1, 1), fetch.parse_as_of("2024-01-05T12:00:00Z"))


def test_missing_key_produces_no_report(tmp_path, monkeypatch, capsys):
    monkeypatch.delenv("POLYGON_API_KEY", raising=False)
    result = fetch.main(["--symbol", "AAPL", "--start", "2024-01-01", "--as-of", "2024-01-05T12:00:00Z", "--output-dir", str(tmp_path)])
    assert result == 2
    assert "POLYGON_API_KEY" in capsys.readouterr().err
    assert not list(tmp_path.iterdir())


def test_proxy_index_is_not_silently_substituted(tmp_path):
    with pytest.raises(SystemExit) as exc:
        fetch.main(["--symbol", "^GSPC", "--start", "2024-01-01", "--as-of", "2024-01-05T12:00:00Z", "--output-dir", str(tmp_path)])
    assert exc.value.code == 2
    assert not list(tmp_path.iterdir())


def test_fixture_cli_uses_shared_provider_and_writes_auditable_bundle(tmp_path, monkeypatch):
    def no_network(*args, **kwargs):
        pytest.fail("Fixture replay attempted network access")

    monkeypatch.setattr(HttpClient, "get_json", no_network)
    monkeypatch.setattr(HttpClient, "get_paged", no_network)
    cache = DiskCache(tmp_path / "fixture")
    raw = []
    for day in (3, 4, 5):
        ts = datetime(2024, 1, day, 5, tzinfo=timezone.utc)
        raw.append(dict(t=int(ts.timestamp() * 1000), o=100, h=105, l=98, c=103, v=1000))
    cache.put("aggs_day", {
        "path": "/v2/aggs/ticker/AAPL/range/1/day/2024-01-01/2024-01-04",
        "adjusted": "true", "sort": "asc", "limit": 50000,
    }, {"results": raw}, immutable=True)
    args = ["--symbol", "aapl", "--start", "2024-01-01", "--as-of", "2024-01-05T12:00:00Z", "--provider", "fixture", "--fixture-dir", str(cache.root), "--output-dir", str(tmp_path / "output")]
    assert fetch.main(args) == 0
    cli = subprocess.run([sys.executable, fetch.__file__, *args], capture_output=True, text=True)
    assert cli.returncode == 0, cli.stderr
    files = list((tmp_path / "output").glob("*.json"))
    assert len(files) == 2  # preserve earlier runs
    report = json.loads(files[0].read_text())
    assert report["symbol"] == "AAPL"
    assert report["source"]["provider"] == "fixture"
    assert report["last_completed_bar"] == "2024-01-04"
    assert [b["date"] for b in report["bars"]] == ["2024-01-03", "2024-01-04"]
    assert report["adjustment"] == "split_adjusted_ohlc_not_dividend_adjusted"
    assert report["point_in_time_snapshot"] is False
    assert report["warnings"]  # coverage/revisions remain unverified
    assert "phase" not in report


def test_fixture_miss_returns_error_without_report(tmp_path, capsys):
    result = fetch.main(["--symbol", "AAPL", "--start", "2024-01-01", "--as-of", "2024-01-05T12:00:00Z", "--provider", "fixture", "--fixture-dir", str(tmp_path / "missing"), "--output-dir", str(tmp_path / "out")])
    assert result == 1
    assert "fixture" in capsys.readouterr().err.lower()
    assert not (tmp_path / "out").exists()


def test_provider_failure_redacts_credentials(tmp_path, monkeypatch, capsys):
    from scripts.market_data.provider import ProviderError

    secret = "test-secret-for-redaction-only"  # pragma: allowlist secret
    monkeypatch.setenv("POLYGON_API_KEY", secret)

    def fail(*args, **kwargs):
        raise ProviderError(f"request failed: apiKey={secret}")

    monkeypatch.setattr("scripts.market_data.get_provider", fail)
    result = fetch.main(["--symbol", "AAPL", "--start", "2024-01-01", "--as-of", "2024-01-05T12:00:00Z", "--output-dir", str(tmp_path)])
    assert result == 1
    error = capsys.readouterr().err
    assert secret not in error
    assert "REDACTED" in error
    assert not list(tmp_path.iterdir())


def test_missing_shared_checkout_has_actionable_error(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("TRADING_SKILLS_REPO_ROOT", str(tmp_path))
    result = fetch.main(["--symbol", "AAPL", "--start", "2024-01-01", "--as-of", "2024-01-05T12:00:00Z", "--provider", "fixture", "--fixture-dir", str(tmp_path), "--output-dir", str(tmp_path / "out")])
    assert result == 2
    assert "TRADING_SKILLS_REPO_ROOT" in capsys.readouterr().err
    assert not (tmp_path / "out").exists()
