"""Packaged-dependency contract for macro-regime-detector (issue #330).

Covers the #311 regression shape: a broken install (missing ``requests``) or a
missing ``POLYGON_API_KEY`` must fail with an actionable exit 2, never with a
silent all-zero report.
"""

import os
import subprocess
import sys
import zipfile
from pathlib import Path
from unittest.mock import patch

import macro_regime_detector
import pytest

SCRIPTS_DIR = Path(__file__).resolve().parent.parent
SKILL_DIR = SCRIPTS_DIR.parent
REPO_ROOT = SKILL_DIR.parent.parent


def test_missing_package_exits_actionable(tmp_path, monkeypatch, capsys):
    """A missing required package exits 2 and names requirements.txt."""
    monkeypatch.setattr(
        sys,
        "argv",
        ["macro_regime_detector.py", "--output-dir", str(tmp_path)],
    )
    with (
        patch.object(macro_regime_detector, "missing_required_packages", return_value=["requests"]),
        pytest.raises(SystemExit) as exc_info,
    ):
        macro_regime_detector.main()
    assert exc_info.value.code == 2
    err = capsys.readouterr().err
    assert "requests" in err
    assert "requirements.txt" in err
    assert not list(tmp_path.rglob("macro_regime_*.json"))


def test_probe_ignores_present_packages():
    """Installed required packages are never reported missing."""
    assert "requests" not in macro_regime_detector.missing_required_packages()


def test_help_exits_zero():
    """--help works without credentials, network, or data packages."""
    completed = subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "macro_regime_detector.py"), "--help"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0


def test_missing_polygon_key_exits_actionable(tmp_path):
    """No POLYGON_API_KEY and no --api-key → exit 2 naming the variable."""
    env = dict(os.environ)
    env.pop("POLYGON_API_KEY", None)
    env.pop("FMP_API_KEY", None)
    completed = subprocess.run(
        [
            sys.executable,
            str(SCRIPTS_DIR / "macro_regime_detector.py"),
            "--output-dir",
            str(tmp_path / "reports"),
        ],
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )
    assert completed.returncode == 2
    assert "POLYGON_API_KEY" in completed.stderr
    assert (
        not list((tmp_path / "reports").rglob("*.json"))
        if (tmp_path / "reports").exists()
        else True
    )


def test_packaged_skill_declares_requests():
    """The committed .skill ships requirements.txt including requests."""
    archive = REPO_ROOT / "skill-packages" / "macro-regime-detector.skill"
    assert archive.is_file(), "packaged archive must be committed in this repo"
    with zipfile.ZipFile(archive) as bundle:
        name = "macro-regime-detector/requirements.txt"
        assert name in bundle.namelist()
        text = bundle.read(name).decode("utf-8")
    assert "requests" in text


def test_missing_requests_exits_actionable_before_import(tmp_path):
    """Blocking requests still yields exit 2 (not an import traceback).

    scripts/market_data imports requests lazily, so the module imports even
    when requests is blocked and the startup probe reports exit 2 with an
    actionable message. --help must also survive it.
    """
    preamble = (
        "import sys; sys.modules['requests'] = None; "
        "sys.argv = ['macro_regime_detector.py', '--output-dir', r'{}']; ".format(
            tmp_path / "reports"
        )
        + "import macro_regime_detector; macro_regime_detector.main()"
    )
    completed = subprocess.run(
        [sys.executable, "-c", preamble],
        capture_output=True,
        text=True,
        check=False,
        cwd=str(SCRIPTS_DIR),
    )
    assert completed.returncode == 2
    assert "requirements.txt" in completed.stderr

    help_preamble = (
        "import sys; sys.modules['requests'] = None; "
        "sys.argv = ['macro_regime_detector.py', '--help']; "
        "import macro_regime_detector; macro_regime_detector.main()"
    )
    completed_help = subprocess.run(
        [sys.executable, "-c", help_preamble],
        capture_output=True,
        text=True,
        check=False,
        cwd=str(SCRIPTS_DIR),
    )
    assert completed_help.returncode == 0
