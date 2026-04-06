import asyncio
import json
import re
import time
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Request, Query
from fastapi.responses import StreamingResponse

from app.api.deps import get_devices_config, get_redis, find_device_for_query
from app.services.command_builder import CommandBuilder
from app.services.acl_checker import AclChecker
from app.services.validators import get_ip_version
from app.services.output_parser import OutputParser
from app.services.device_connector import (
    _is_command_allowed,
    _get_semaphore,
    _resolve_device_type,
)
from app.services.local_executor import (
    build_local_command,
    is_local_command_allowed,
    stream_local_command,
    PING_TIMEOUT,
    TRACEROUTE_TIMEOUT,
)
from app.core.constants import SUPPORTED_QUERY_TYPES
from app.core.exceptions import TargetDeniedError, SecurityError
from app.core.security import validate_ip_or_prefix, _check_forbidden_patterns
from app.core.logging import get_logger
from app.config import settings

router = APIRouter()
logger = get_logger("api.stream")


_PROMPT_RE = re.compile(r"^[\w\-./]+[#>]\s*$")


def _is_noise(line: str, command: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return True
    if _PROMPT_RE.match(stripped):
        return True
    if stripped.endswith("#") or stripped.endswith(">"):
        if len(stripped) < 80 and " " not in stripped:
            return True
    if command and command in stripped:
        return True
    return False


def _stream_command(params: dict, command: str, queue: asyncio.Queue, loop):
    from netmiko import ConnectHandler

    try:
        conn = ConnectHandler(**params)
        try:
            conn.find_prompt()
            conn.write_channel(command + "\n")
            time.sleep(0.5)

            output_buf = ""
            empty_reads = 0
            deadline = time.monotonic() + settings.SSH_COMMAND_TIMEOUT

            while time.monotonic() < deadline:
                chunk = conn.read_channel()
                if chunk:
                    empty_reads = 0
                    output_buf += chunk
                    lines = output_buf.split("\n")
                    for line in lines[:-1]:
                        clean = line.rstrip()
                        if not _is_noise(clean, command):
                            sanitized = OutputParser.sanitize(clean)
                            asyncio.run_coroutine_threadsafe(
                                queue.put(("line", sanitized)), loop
                            )
                    output_buf = lines[-1]
                else:
                    empty_reads += 1
                    if empty_reads > 6:
                        break
                    time.sleep(0.5)

            if output_buf.strip():
                remainder = output_buf.strip()
                if not _is_noise(remainder, command):
                    sanitized = OutputParser.sanitize(remainder)
                    asyncio.run_coroutine_threadsafe(
                        queue.put(("line", sanitized)), loop
                    )
        finally:
            conn.disconnect()

        asyncio.run_coroutine_threadsafe(queue.put(("done", "")), loop)
    except Exception:
        asyncio.run_coroutine_threadsafe(
            queue.put(("error", "Device connection failed")), loop
        )


@router.get("/query/stream")
async def stream_query(
    request: Request,
    query_type: str = Query(...),
    target: str = Query(...),
    devices: dict = Depends(get_devices_config),
):
    query_type = query_type.strip().lower()
    if query_type not in SUPPORTED_QUERY_TYPES:
        return StreamingResponse(
            _error_stream("Unsupported query type"),
            media_type="text/event-stream",
        )

    target = target.strip()
    if not target:
        return StreamingResponse(
            _error_stream("Target address cannot be empty"),
            media_type="text/event-stream",
        )

    try:
        _check_forbidden_patterns(target)
        if query_type in ("bgp_route", "ping", "traceroute"):
            target = validate_ip_or_prefix(target)
    except Exception:
        return StreamingResponse(
            _error_stream("Invalid or forbidden target address"),
            media_type="text/event-stream",
        )

    acl = AclChecker(settings.ACL_CONFIG_PATH)
    if acl.check_target(target):
        return StreamingResponse(
            _error_stream("Query not allowed for this target address"),
            media_type="text/event-stream",
        )

    match = find_device_for_query(query_type)
    if not match:
        return StreamingResponse(
            _error_stream(f"No device available for {query_type.replace('_', ' ')} queries"),
            media_type="text/event-stream",
        )

    device_id, device = match
    platform = device["platform"]
    ip_version = get_ip_version(target)
    use_local = platform == "local"

    if use_local:
        if not is_local_command_allowed(query_type):
            return StreamingResponse(_error_stream("This query type is not supported locally"), media_type="text/event-stream")
        cmd_args = build_local_command(query_type, target, ip_version)
        if not cmd_args:
            return StreamingResponse(_error_stream("Failed to build local command"), media_type="text/event-stream")
    else:
        cmd_builder = CommandBuilder(settings.COMMANDS_CONFIG_PATH)
        command = cmd_builder.build(
            platform=platform,
            query_type=query_type,
            target=target,
            ip_version=ip_version,
            source_ipv4=device.get("network", {}).get("ipv4_source", ""),
            source_ipv6=device.get("network", {}).get("ipv6_source", ""),
        )
        if not command:
            return StreamingResponse(_error_stream("This query type is not supported"), media_type="text/event-stream")
        if not _is_command_allowed(command, platform):
            return StreamingResponse(_error_stream("Security: command not allowed"), media_type="text/event-stream")

    request_id = str(uuid.uuid4())

    async def event_generator():
        yield _sse("status", json.dumps({
            "request_id": request_id,
            "device": device.get("name", device_id),
            "query_type": query_type,
            "target": target,
            "message": "Running query..." if use_local else "Connecting to device...",
        }))

        queue: asyncio.Queue = asyncio.Queue()
        start = time.monotonic()

        if use_local:
            timeout = PING_TIMEOUT if query_type == "ping" else TRACEROUTE_TIMEOUT
            task = asyncio.create_task(stream_local_command(cmd_args, queue, timeout))
        else:
            protocol = device.get("protocol", "ssh")
            netmiko_params = {
                "device_type": _resolve_device_type(platform, protocol),
                "host": device["host"],
                "port": device.get("ssh", {}).get("port", 22 if protocol == "ssh" else 23),
                "username": device.get("username", ""),
                "password": device.get("password", ""),
                "timeout": device.get("ssh", {}).get("timeout", settings.SSH_TIMEOUT),
            }
            loop = asyncio.get_event_loop()
            task = loop.run_in_executor(None, _stream_command, netmiko_params, command, queue, loop)

        read_timeout = (PING_TIMEOUT if query_type == "ping" else TRACEROUTE_TIMEOUT) if use_local else settings.SSH_COMMAND_TIMEOUT

        try:
            while True:
                try:
                    msg_type, data = await asyncio.wait_for(queue.get(), timeout=read_timeout)
                except asyncio.TimeoutError:
                    yield _sse("error", json.dumps({"message": "Query timed out"}))
                    break

                if msg_type == "line":
                    yield _sse("output", data)
                elif msg_type == "done":
                    elapsed = round((time.monotonic() - start) * 1000)
                    yield _sse("complete", json.dumps({"response_time_ms": elapsed, "request_id": request_id}))
                    break
                elif msg_type == "error":
                    yield _sse("error", json.dumps({"message": data}))
                    break
        finally:
            task.cancel()

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive", "X-Accel-Buffering": "no"},
    )


def _sse(event: str, data: str) -> str:
    return f"event: {event}\ndata: {data}\n\n"


async def _error_stream(message: str):
    yield _sse("error", json.dumps({"message": message}))
