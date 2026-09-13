"""Optional Claude narrative via ``claude -p`` (non-fatal on any failure)."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

PROMPT_TEMPLATE = Path(__file__).resolve().parents[1] / "references" / "narrative-prompt.md"


def should_run(mode: str, slot: str, narrative_slots: list[str], flipped: bool) -> bool:
    if mode == "never":
        return False
    if mode == "always":
        return True
    return slot in narrative_slots or flipped


def build_prompt(
    current: dict, previous: dict | None, baseline: dict | None, template: Path = PROMPT_TEMPLATE
) -> str:
    text = template.read_text(encoding="utf-8") if template.is_file() else "{{CURRENT_JSON}}"
    slim = dict(current)
    slim.pop("narrative", None)
    slim.pop("discord", None)
    return (
        text.replace("{{CURRENT_JSON}}", json.dumps(slim, indent=1, sort_keys=True))
        .replace(
            "{{PREVIOUS_JSON}}",
            json.dumps(previous, indent=1, sort_keys=True) if previous else "null",
        )
        .replace(
            "{{BASELINE_JSON}}",
            json.dumps(baseline, indent=1, sort_keys=True) if baseline else "null",
        )
    )


def run_claude(
    prompt: str,
    out_path: Path,
    *,
    claude_bin: str = "claude",
    timeout: float = 180.0,
    runner=subprocess.run,
) -> dict:
    exe = shutil.which(claude_bin) or claude_bin
    try:
        proc = runner(
            [exe, "-p", prompt, "--output-format", "text"],
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except FileNotFoundError:
        return {
            "requested": True,
            "written": False,
            "path": None,
            "error": f"{claude_bin} not found",
        }
    except subprocess.TimeoutExpired:
        return {
            "requested": True,
            "written": False,
            "path": None,
            "error": f"timeout after {timeout:.0f}s",
        }
    except Exception as exc:  # pragma: no cover - defensive
        return {"requested": True, "written": False, "path": None, "error": str(exc)[:200]}
    if proc.returncode != 0 or not (proc.stdout or "").strip():
        return {
            "requested": True,
            "written": False,
            "path": None,
            "error": f"exit {proc.returncode}: {(proc.stderr or '')[:200].strip()}",
        }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(proc.stdout.strip() + "\n", encoding="utf-8")
    return {"requested": True, "written": True, "path": str(out_path), "error": None}
