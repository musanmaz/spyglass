import asyncio
import hmac
import json
import re
import time
import uuid
from urllib.parse import urlparse

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from starlette.websockets import WebSocketState

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
from app.core.security import validate_ip_or_prefix, _check_forbidden_patterns
from app.core.logging import get_logger
from app.config import settings

router = APIRouter()
logger = get_logger("ws.query")


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
        asyncio.run_coroutine_threadsafe(queue.put(("error", "Device connection failed")), loop)


async def _check_rate_limit(client_ip: str) -> bool:
    redis = get_redis()
    key = f"ws:rl:{client_ip}"
    now = time.time()
    pipe = redis.pipeline()
    pipe.zremrangebyscore(key, 0, now - 60)
    pipe.zadd(key, {f"{now}:{uuid.uuid4().hex[:6]}": now})
    pipe.zcard(key)
    pipe.expire(key, 70)
    results = await pipe.execute()
    return results[2] <= settings.RATE_LIMIT_QUERY


def _is_origin_allowed(origin: str) -> bool:
    if not origin:
        return False
    if settings.ALLOWED_ORIGINS:
        return origin in settings.ALLOWED_ORIGINS
    try:
        parsed = urlparse(origin)
        return parsed.scheme in ("http", "https") and bool(parsed.netloc)
    except Exception:
        return False


def _verify_ws_token(websocket: WebSocket) -> bool:
    token = websocket.headers.get("x-api-token", "")
    if not token or not settings.API_PROXY_TOKEN:
        return False
    return hmac.compare_digest(token, settings.API_PROXY_TOKEN)


@router.websocket("/ws/query")
async def ws_query(websocket: WebSocket):
    if settings.REQUIRE_API_TOKEN and not _verify_ws_token(websocket):
        logger.warning("WS rejected: missing or invalid API token")
        await websocket.close(code=4003, reason="Forbidden")
        return

    origin = websocket.headers.get("origin", "")
    sec_fetch = websocket.headers.get("sec-fetch-site", "")

    if sec_fetch == "same-origin":
        pass
    elif _is_origin_allowed(origin):
        pass
    elif not settings.REQUIRE_API_TOKEN and origin:
        pass
    else:
        logger.warning("WS rejected: invalid origin=%s sec_fetch=%s", origin, sec_fetch)
        await websocket.close(code=4003, reason="Forbidden")
        return

    client_ip = (
        websocket.headers.get("x-real-ip")
        or websocket.headers.get("x-forwarded-for", "").split(",")[0].strip()
        or (websocket.client.host if websocket.client else "unknown")
    )

    if not await _check_rate_limit(client_ip):
        await websocket.close(code=4029, reason="Rate limited")
        return

    await websocket.accept()

    try:
        raw = await asyncio.wait_for(websocket.receive_text(), timeout=30)
        data = json.loads(raw)
    except (asyncio.TimeoutError, json.JSONDecodeError, WebSocketDisconnect):
        if websocket.client_state == WebSocketState.CONNECTED:
            await websocket.close(code=4000)
        return

    query_type = data.get("query_type", "").strip().lower()
    target = data.get("target", "").strip()
    request_id = str(uuid.uuid4())

    async def send(msg_type: str, payload: dict):
        if websocket.client_state == WebSocketState.CONNECTED:
            await websocket.send_json({"type": msg_type, **payload})

    if query_type not in SUPPORTED_QUERY_TYPES:
        await send("error", {"message": "Unsupported query type"})
        await websocket.close()
        return

    if not target:
        await send("error", {"message": "Target address cannot be empty"})
        await websocket.close()
        return

    try:
        _check_forbidden_patterns(target)
        target = validate_ip_or_prefix(target)
    except Exception:
        await send("error", {"message": "Invalid or forbidden target address"})
        await websocket.close()
        return

    acl = AclChecker(settings.ACL_CONFIG_PATH)
    acl_err = acl.check_target(target)
    if acl_err:
        await send("error", {"message": acl_err})
        await websocket.close()
        return

    match = find_device_for_query(query_type)
    if not match:
        await send("error", {"message": f"No device available for {query_type.replace('_', ' ')} queries"})
        await websocket.close()
        return

    device_id, device = match
    platform = device["platform"]
    ip_version = get_ip_version(target)
    use_local = platform == "local"

    if use_local:
        if not is_local_command_allowed(query_type):
            await send("error", {"message": "This query type is not supported locally"})
            await websocket.close()
            return
        cmd_args = build_local_command(query_type, target, ip_version)
        if not cmd_args:
            await send("error", {"message": "Failed to build local command"})
            await websocket.close()
            return
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
            await send("error", {"message": "This query type is not supported"})
            await websocket.close()
            return
        if not _is_command_allowed(command, platform):
            await send("error", {"message": "Security: command not allowed"})
            await websocket.close()
            return

    await send("status", {
        "request_id": request_id,
        "device": device.get("name", device_id),
        "query_type": query_type,
        "target": target,
        "message": "Running query..." if use_local else "Connecting to device...",
    })

    queue: asyncio.Queue = asyncio.Queue()
    start = time.monotonic()

    if use_local:
        timeout = PING_TIMEOUT if query_type == "ping" else TRACEROUTE_TIMEOUT
        task = asyncio.create_task(stream_local_command(cmd_args, queue, timeout))
        try:
            while True:
                try:
                    msg_type, msg_data = await asyncio.wait_for(queue.get(), timeout=timeout)
                except asyncio.TimeoutError:
                    await send("error", {"message": "Query timed out"})
                    break
                if msg_type == "line":
                    await send("output", {"data": msg_data})
                elif msg_type == "done":
                    elapsed = round((time.monotonic() - start) * 1000)
                    await send("complete", {"response_time_ms": elapsed, "request_id": request_id})
                    break
                elif msg_type == "error":
                    await send("error", {"message": msg_data})
                    break
        finally:
            task.cancel()
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
        semaphore = _get_semaphore(device_id)
        async with semaphore:
            task = loop.run_in_executor(None, _stream_command, netmiko_params, command, queue, loop)
            try:
                while True:
                    try:
                        msg_type, msg_data = await asyncio.wait_for(
                            queue.get(), timeout=settings.SSH_COMMAND_TIMEOUT
                        )
                    except asyncio.TimeoutError:
                        await send("error", {"message": "Query timed out"})
                        break
                    if msg_type == "line":
                        await send("output", {"data": msg_data})
                    elif msg_type == "done":
                        elapsed = round((time.monotonic() - start) * 1000)
                        await send("complete", {"response_time_ms": elapsed, "request_id": request_id})
                        break
                    elif msg_type == "error":
                        await send("error", {"message": msg_data})
                        break
            finally:
                task.cancel()

    if websocket.client_state == WebSocketState.CONNECTED:
        await websocket.close()
