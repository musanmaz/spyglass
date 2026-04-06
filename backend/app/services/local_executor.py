"""Execute ping / traceroute locally via subprocess with streaming output."""

import asyncio
import re
import shutil
from typing import Optional

from app.services.output_parser import OutputParser
from app.config import settings

_SAFE_TARGET = re.compile(r"^[a-fA-F0-9:./%]+$")

PING_TIMEOUT = 30
TRACEROUTE_TIMEOUT = 60

_BIN_CACHE: dict[str, Optional[str]] = {}


def _find_bin(name: str) -> Optional[str]:
    if name not in _BIN_CACHE:
        _BIN_CACHE[name] = shutil.which(name)
    return _BIN_CACHE[name]


def build_local_command(query_type: str, target: str, ip_version: int = 4) -> Optional[list[str]]:
    if not _SAFE_TARGET.match(target):
        return None

    if query_type == "ping":
        binary = _find_bin("ping")
        if not binary:
            return None
        if ip_version == 6:
            return [binary, "-6", "-c", "5", "-W", "2", target]
        return [binary, "-c", "5", "-W", "2", target]

    if query_type == "traceroute":
        if ip_version == 6:
            binary = _find_bin("traceroute6") or _find_bin("traceroute")
            if not binary:
                return None
            if "traceroute6" in binary:
                return [binary, "-w", "2", "-m", "30", target]
            return [binary, "-6", "-w", "2", "-m", "30", target]
        binary = _find_bin("traceroute")
        if not binary:
            return None
        return [binary, "-w", "2", "-m", "30", target]

    return None


def is_local_command_allowed(query_type: str) -> bool:
    return query_type in ("ping", "traceroute")


async def stream_local_command(
    cmd_args: list[str],
    queue: asyncio.Queue,
    timeout: int = TRACEROUTE_TIMEOUT,
) -> None:
    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd_args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )

        try:
            deadline = asyncio.get_event_loop().time() + timeout
            while True:
                remaining = deadline - asyncio.get_event_loop().time()
                if remaining <= 0:
                    proc.kill()
                    await queue.put(("error", "Query timed out"))
                    return

                try:
                    line_bytes = await asyncio.wait_for(
                        proc.stdout.readline(), timeout=min(remaining, 10)
                    )
                except asyncio.TimeoutError:
                    if proc.returncode is not None:
                        break
                    continue

                if not line_bytes:
                    break

                line = line_bytes.decode("utf-8", errors="replace").rstrip()
                if line:
                    sanitized = OutputParser.sanitize(line)
                    await queue.put(("line", sanitized))

            await proc.wait()
        except Exception:
            proc.kill()
            raise

        await queue.put(("done", ""))
    except Exception:
        await queue.put(("error", "Local command execution failed"))
