#!/usr/bin/env python3
"""Minimal Discord bot that runs claude -p on @mention messages."""

import asyncio
import os
import re

import discord

REPO_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MAX_MSG_LEN = 1900  # leave room for code fences / formatting

# Tools claude -p may use without an interactive permission prompt. Anything
# outside this list is denied (non-interactive mode cannot ask), so keep it to
# read-only / data-fetching tools plus the repo's own skill scripts.
ALLOWED_TOOLS = ",".join(
    [
        "WebSearch",
        "WebFetch",
        "Read",
        "Glob",
        "Grep",
        "Bash(python3 skills/*)",
        "Bash(uv run skills/*)",
    ]
)

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


def claude_argv(prompt: str) -> list[str]:
    return [
        "claude",
        "-p",
        prompt,
        "--model",
        "opus",
        "--effort",
        "medium",
        "--allowedTools",
        ALLOWED_TOOLS,
    ]


def format_failure(returncode: int, stdout: str, stderr: str) -> str:
    """claude prints many errors (e.g. auth failures) to stdout, so show both."""
    body = "\n".join(s for s in (stdout.strip(), stderr.strip()) if s) or "(no output)"
    return f"**claude exited {returncode}**\n```\n{body[:1500]}\n```"


def is_auth_failure(stdout: str, stderr: str) -> bool:
    return AUTH_ERROR_MARKER in (stdout + stderr).lower()


async def _run_once(prompt: str) -> tuple[int, str, str]:
    proc = await asyncio.create_subprocess_exec(
        *claude_argv(prompt),
        stdin=asyncio.subprocess.DEVNULL,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd=REPO_DIR,
    )
    stdout, stderr = await proc.communicate()
    return proc.returncode, stdout.decode(errors="replace"), stderr.decode(errors="replace")


async def run_claude(prompt: str) -> str:
    rc, out, err = await _run_once(prompt)
    if rc != 0 and is_auth_failure(out, err):
        # OAuth refresh races are transient; one retry usually clears it.
        await asyncio.sleep(AUTH_RETRY_DELAY_SEC)
        rc, out, err = await _run_once(prompt)
    if rc != 0:
        return format_failure(rc, out, err)
    return out.strip()


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
        if not prompt:
            await message.reply("Give me a prompt after the mention.")
            return

        # Decide where to reply: create thread for top-level, use existing thread
        if isinstance(message.channel, discord.Thread):
            thread = message.channel
        else:
            thread = await message.create_thread(name=prompt[:100])
        thinking = await thread.send("Thinking...")

        result = await run_claude(prompt)
        await thinking.delete()
        await send_long(thread, result)

    return client


if __name__ == "__main__":
    make_client(owner_id_from_env()).run(os.environ["DISCORD_BOT_TOKEN"])
