import asyncio
import json
import re
import time
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Request, Query
from fastapi.responses import StreamingResponse

from app.api.deps import get_devices_config, get_redis
from app.services.command_builder import CommandBuilder
from app.services.acl_checker import AclChecker
from app.services.validators import get_ip_version
from app.services.output_parser import OutputParser
from app.services.device_connector import (
    _is_command_allowed,
    _get_semaphore,
    _resolve_device_type,
)
from app.core.constants import SUPPORTED_QUERY_TYPES
from app.core.exceptions import TargetDeniedError, SecurityError
from app.core.security import validate_ip_or_prefix, _check_forbidden_patterns
from app.core.logging import get_logger
from app.config import settings

router = APIRouter()
logger = get_logger("api.stream")


def _stream_command(params: dict, command: str, queue: asyncio.Queue, loop):
    """Blocking Netmiko call that pushes output line-by-line to an asyncio queue."""
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
                        if clean and not clean.endswith("#") and command not in clean:
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
                if not remainder.endswith("#") and command not in remainder:
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

    device_id = list(devices.keys())[0]
    device = devices[device_id]
    platform = device["platform"]
    ip_version = get_ip_version(target)

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
        return StreamingResponse(
            _error_stream("This query type is not supported"),
            media_type="text/event-stream",
        )

    if not _is_command_allowed(command, platform):
        return StreamingResponse(
            _error_stream("Security: command not allowed"),
            media_type="text/event-stream",
        )

    protocol = device.get("protocol", "ssh")
    netmiko_params = {
        "device_type": _resolve_device_type(platform, protocol),
        "host": device["host"],
        "port": device.get("ssh", {}).get("port", 22 if protocol == "ssh" else 23),
        "username": device.get("username", ""),
        "password": device.get("password", ""),
        "timeout": device.get("ssh", {}).get("timeout", settings.SSH_TIMEOUT),
    }

    request_id = str(uuid.uuid4())

    async def event_generator():
        yield _sse("status", json.dumps({
            "request_id": request_id,
            "device": device.get("name", device_id),
            "query_type": query_type,
            "target": target,
            "message": "Connecting to device...",
        }))

        queue: asyncio.Queue = asyncio.Queue()
        loop = asyncio.get_event_loop()
        semaphore = _get_semaphore(device_id)

        async with semaphore:
            task = asyncio.get_event_loop().run_in_executor(
                None, _stream_command, netmiko_params, command, queue, loop
            )

            start = time.monotonic()
            try:
                while True:
                    try:
                        msg_type, data = await asyncio.wait_for(
                            queue.get(), timeout=settings.SSH_COMMAND_TIMEOUT
                        )
                    except asyncio.TimeoutError:
                        yield _sse("error", json.dumps({"message": "Query timed out"}))
                        break

                    if msg_type == "line":
                        yield _sse("output", data)
                    elif msg_type == "done":
                        elapsed = round((time.monotonic() - start) * 1000)
                        yield _sse("complete", json.dumps({
                            "response_time_ms": elapsed,
                            "request_id": request_id,
                        }))
                        break
                    elif msg_type == "error":
                        yield _sse("error", json.dumps({"message": data}))
                        break
            finally:
                task.cancel()

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


def _sse(event: str, data: str) -> str:
    return f"event: {event}\ndata: {data}\n\n"


async def _error_stream(message: str):
    yield _sse("error", json.dumps({"message": message}))
