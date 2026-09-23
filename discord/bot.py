#!/usr/bin/env python3
"""Minimal Discord bot that runs claude -p on @mention messages."""

import asyncio
import json
import os
import re
import shutil
import time

import discord

REPO_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MAX_MSG_LEN = 1900  # leave room for code fences / formatting

# Discord attachments are saved here (gitignored via .cache/) so claude -p can
# Read them by a repo-relative path. One sub-folder per message id.
UPLOAD_DIR_REL = os.path.join(".cache", "files")
UPLOAD_DIR = os.path.join(REPO_DIR, UPLOAD_DIR_REL)
MAX_ATTACHMENT_BYTES = 50 * 1024 * 1024
UPLOAD_TTL_SEC = 7 * 24 * 3600
DEFAULT_ATTACHMENT_PROMPT = "Summarize and analyze the attached file(s)."

ATTACHMENT_SYSTEM_PROMPT = """\
The user's Discord message includes file attachments. They are already saved on
disk; the paths (relative to the repo root) are listed at the end of the prompt.
- For any .pdf attachment, FIRST run the read-pdf skill:
    python3 skills/read-pdf/scripts/pdf_to_md.py <path>
  It prints the path of a temporary Markdown file. Read that Markdown file with
  the Read tool, then base the analysis on its content. Do not try WebFetch or
  other tools on the PDF.
- For images (.png/.jpg/.jpeg/.gif/.webp), Read the file directly.
- For text-like files (.md/.txt/.csv/.json/.yaml), Read the file directly.
Always analyze the attached files rather than searching the repo for other files.
"""

# Always appended: claude -p cannot ask for approval, so tell it up front how
# to stay inside ALLOWED_TOOLS instead of discovering it by trial and error.
BASE_SYSTEM_PROMPT = """\
You are running non-interactively behind a Discord bot, with the repo root as
the working directory. Tool calls outside the allowlist are denied automatically;
nobody can approve them, so follow these rules:
- Skills live in skills/<name>/ (SKILL.md, scripts/, references/). Read the
  SKILL.md, then run its scripts from the repo root with the full path:
    python3 skills/<name>/scripts/<script>.py ...
  If a SKILL.md shows `python3 scripts/x.py` or `cd skills/<name> && ...`,
  rewrite it as `python3 skills/<name>/scripts/x.py`.
- API keys (POLYGON_API_KEY, FMP_API_KEY) are already in the environment. Do not
  check, echo, export or source them, and do not pass --api-key; the scripts
  read the environment themselves.
- One command per Bash call: no `;`, `&&`, `$VAR`, env-var prefixes, heredocs,
  `python3 -c` or `python3 -`. Do not write ad-hoc scripts. For fresh data on
  specific tickers use the skill scripts, e.g.
    python3 skills/vcp-screener/scripts/screen_vcp.py --universe T1 T2 ...
    python3 skills/stockbee-momentum-burst-screener/scripts/screen_momentum_burst.py --symbols T1 T2 ...
- Only write files under reports/ (pass --output-dir reports/ to scripts).
- If a step you needed was denied, name the exact command that was denied
  instead of vaguely saying the data was unavailable.
"""

# Tools claude -p may use without an interactive permission prompt. Anything
# outside this list is denied (non-interactive mode cannot ask). The only code
# execution entry point is the repo's skill scripts; repo-root scripts/ (PR
# pipelines etc.), `python3 -c` and free Write are deliberately excluded.
ALLOWED_TOOLS = ",".join(
    [
        "Read",
        "Glob",
        "Grep",
        "WebSearch",
        "WebFetch",
        "Bash(python3 skills/*)",
        "Bash(python skills/*)",
        "Bash(uv run skills/*)",
        # Edit rules also cover Write; several skills save reports themselves.
        "Edit(reports/**)",
        "Bash(mkdir -p reports/*)",
        # scenario-analyzer delegates to a sub-agent.
        "Agent",
    ]
)

MAX_DENIALS_SHOWN = 5

# Pinned ID: the `opus` alias follows CLI auto-updates (it silently moved from
# claude-opus-5 to claude-opus-5-5 with CLI 2.1.280).
MODEL = "claude-opus-5-5"

AUTH_RETRY_DELAY_SEC = 5
AUTH_ERROR_MARKER = "authenticate"


def strip_mention(content: str, bot_id: int) -> str:
    """Remove the @mention of the bot from the message text."""
    return re.sub(rf"<@!?{bot_id}>\s*", "", content).strip()


def owner_id_from_env(env=os.environ) -> int | None:
    """Parse DISCORD_OWNER_ID; None means 'no restriction'."""
    raw = env.get("DISCORD_OWNER_ID", "").strip()
    return int(raw) if raw else None


def is_authorized(author_id: int, owner_id: int | None) -> bool:
    return owner_id is None or author_id == owner_id


def claude_argv(prompt: str, system_prompt: str | None = None) -> list[str]:
    full_system_prompt = BASE_SYSTEM_PROMPT
    if system_prompt:
        full_system_prompt += "\n" + system_prompt
    return [
        "claude",
        "-p",
        prompt,
        "--model",
        MODEL,
        "--effort",
        "medium",
        "--output-format",
        "json",
        "--allowedTools",
        ALLOWED_TOOLS,
        "--append-system-prompt",
        full_system_prompt,
    ]


def safe_filename(name: str) -> str:
    """Strip path components and anything unsafe; keep the extension."""
    base = os.path.basename(name.replace("\\", "/")).strip() or "file"
    base = re.sub(r"[^\w.\-\u4e00-\u9fff ]", "_", base)
    return base[:120]


def build_prompt(prompt: str, attachment_paths: list[str]) -> str:
    """Append the saved attachment paths so claude knows where to look."""
    if not attachment_paths:
        return prompt
    prompt = prompt or DEFAULT_ATTACHMENT_PROMPT
    listing = "\n".join(f"- {p}" for p in attachment_paths)
    return f"{prompt}\n\nAttached files (saved locally, paths relative to repo root):\n{listing}"


def prune_uploads(root: str = UPLOAD_DIR, ttl_sec: int = UPLOAD_TTL_SEC, now: float | None = None):
    """Delete per-message upload folders older than ttl_sec."""
    now = time.time() if now is None else now
    if not os.path.isdir(root):
        return
    for name in os.listdir(root):
        path = os.path.join(root, name)
        try:
            if os.path.isdir(path) and now - os.path.getmtime(path) > ttl_sec:
                shutil.rmtree(path, ignore_errors=True)
        except OSError:
            pass


async def save_attachments(message: discord.Message) -> list[str]:
    """Download message attachments; return repo-relative paths."""
    if not message.attachments:
        return []
    prune_uploads()
    folder = os.path.join(UPLOAD_DIR, str(message.id))
    os.makedirs(folder, exist_ok=True)
    saved: list[str] = []
    for att in message.attachments:
        if att.size > MAX_ATTACHMENT_BYTES:
            print(f"skip attachment {att.filename}: {att.size} bytes", flush=True)
            continue
        dest = os.path.join(folder, safe_filename(att.filename))
        await att.save(dest)
        saved.append(os.path.relpath(dest, REPO_DIR))
    return saved


def format_failure(returncode: int, stdout: str, stderr: str) -> str:
    """claude prints many errors (e.g. auth failures) to stdout, so show both."""
    body = "\n".join(s for s in (stdout.strip(), stderr.strip()) if s) or "(no output)"
    return f"**claude exited {returncode}**\n```\n{body[:1500]}\n```"


def is_auth_failure(stdout: str, stderr: str) -> bool:
    return AUTH_ERROR_MARKER in (stdout + stderr).lower()


def parse_claude_json(stdout: str) -> dict | None:
    """Parse `--output-format json` output; None if claude printed plain text."""
    try:
        data = json.loads(stdout)
    except ValueError:
        return None
    return data if isinstance(data, dict) else None


def summarize_denial(denial: dict) -> str:
    tool_input = denial.get("tool_input") or {}
    detail = tool_input.get("command") or tool_input.get("file_path") or ""
    if not detail and tool_input:
        detail = json.dumps(tool_input, ensure_ascii=False)
    detail = " ".join(str(detail).split())
    return f"{denial.get('tool_name', '?')}: {detail}"[:130]


def denial_footer(denials: list[dict]) -> str:
    if not denials:
        return ""
    lines = [f"-# ⚠️ {len(denials)} tool call(s) denied:"]
    lines += [f"-# • `{summarize_denial(d)}`" for d in denials[:MAX_DENIALS_SHOWN]]
    if len(denials) > MAX_DENIALS_SHOWN:
        more = len(denials) - MAX_DENIALS_SHOWN
        lines.append(f"-# • … {more} more (see logs/discord-bot.log)")
    return "\n\n" + "\n".join(lines)


def render_result(rc: int, stdout: str, stderr: str) -> str:
    """Turn claude's JSON result into the Discord reply; log denied tool calls."""
    data = parse_claude_json(stdout)
    if data is None:
        return format_failure(rc, stdout, stderr) if rc != 0 else stdout.strip()
    denials = data.get("permission_denials") or []
    for denial in denials:
        print(f"permission denied: {summarize_denial(denial)}", flush=True)
    text = str(data.get("result") or "")
    if rc != 0 or data.get("is_error"):
        return format_failure(rc, text, stderr) + denial_footer(denials)
    return text.strip() + denial_footer(denials)


async def _run_once(prompt: str, system_prompt: str | None) -> tuple[int, str, str]:
    proc = await asyncio.create_subprocess_exec(
        *claude_argv(prompt, system_prompt),
        stdin=asyncio.subprocess.DEVNULL,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd=REPO_DIR,
    )
    stdout, stderr = await proc.communicate()
    return proc.returncode, stdout.decode(errors="replace"), stderr.decode(errors="replace")


async def run_claude(prompt: str, system_prompt: str | None = None) -> str:
    rc, out, err = await _run_once(prompt, system_prompt)
    if rc != 0 and is_auth_failure(out, err):
        # OAuth refresh races are transient; one retry usually clears it.
        await asyncio.sleep(AUTH_RETRY_DELAY_SEC)
        rc, out, err = await _run_once(prompt, system_prompt)
    return render_result(rc, out, err)


async def send_long(channel, text: str):
    """Send text, splitting into multiple messages if needed."""
    while text:
        chunk, text = text[:MAX_MSG_LEN], text[MAX_MSG_LEN:]
        await channel.send(chunk)


def make_client(owner_id: int | None) -> discord.Client:
    intents = discord.Intents(guilds=True, messages=True, message_content=True)
    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        scope = f"owner={owner_id}" if owner_id else "owner=ANY (DISCORD_OWNER_ID unset)"
        print(f"Bot ready: {client.user} (id={client.user.id}) {scope}", flush=True)

    @client.event
    async def on_message(message: discord.Message):
        if message.author == client.user:
            return
        if not client.user.mentioned_in(message):
            return
        if not is_authorized(message.author.id, owner_id):
            await message.reply("Sorry, only the bot owner can run commands.")
            return

        prompt = strip_mention(message.content, client.user.id)
        if not prompt and not message.attachments:
            await message.reply("Give me a prompt (or a file) after the mention.")
            return

        # Decide where to reply: create thread for top-level, use existing thread
        if isinstance(message.channel, discord.Thread):
            thread = message.channel
        else:
            thread = await message.create_thread(name=(prompt or DEFAULT_ATTACHMENT_PROMPT)[:100])
        thinking = await thread.send("Thinking...")

        attachment_paths = await save_attachments(message)
        full_prompt = build_prompt(prompt, attachment_paths)
        system_prompt = ATTACHMENT_SYSTEM_PROMPT if attachment_paths else None
        result = await run_claude(full_prompt, system_prompt)
        await thinking.delete()
        await send_long(thread, result)

    return client


if __name__ == "__main__":
    make_client(owner_id_from_env()).run(os.environ["DISCORD_BOT_TOKEN"])
