import asyncio
import time
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional

from app.core.cache import CacheService
from app.core.exceptions import DeviceNotFoundError, TargetDeniedError
from app.services.acl_checker import AclChecker
from app.services.command_builder import CommandBuilder
from app.services.device_connector import execute_on_device
from app.services.validators import get_ip_version
from app.core.logging import get_logger

logger = get_logger("query_executor")


class QueryExecutor:
    def __init__(self, cache: CacheService, devices: Dict[str, dict], acl_checker: AclChecker, command_builder: CommandBuilder):
        self.cache = cache
        self.devices = devices
        self.acl = acl_checker
        self.cmd = command_builder

    async def execute(self, query_type: str, target: str, device_ids: List[str]) -> dict:
        request_id = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc).isoformat()

        denial = self.acl.check_target(target)
        if denial:
            raise TargetDeniedError(target)

        for did in device_ids:
            if did not in self.devices:
                raise DeviceNotFoundError(did)

        ip_version = get_ip_version(target)
        tasks = [
            self._execute_single(request_id, query_type, target, did, ip_version)
            for did in device_ids
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        processed = []
        for did, result in zip(device_ids, results):
            if isinstance(result, Exception):
                device = self.devices[did]
                processed.append({
                    "device_id": did,
                    "device_name": device.get("name", did),
                    "platform": device.get("platform", ""),
                    "location": device.get("location", {}),
                    "network": device.get("network", {}),
                    "status": "error",
                    "response_time_ms": 0,
                    "query_type": query_type,
                    "target": target,
                    "output": "",
                    "error": str(result),
                })
            else:
                processed.append(result)

        return {
            "request_id": request_id,
            "cached": any(r.get("cached", False) for r in processed if isinstance(r, dict)),
            "timestamp": timestamp,
            "results": processed,
        }

    async def _execute_single(self, request_id: str, query_type: str, target: str, device_id: str, ip_version: int) -> dict:
        device = self.devices[device_id]
        
        cached = await self.cache.get(query_type, target, device_id)
        if cached:
            cached["cached"] = True
            return cached

        source_ipv4 = device.get("network", {}).get("ipv4_source", "")
        source_ipv6 = device.get("network", {}).get("ipv6_source", "")

        command = self.cmd.build(
            platform=device["platform"],
            query_type=query_type,
            target=target,
            ip_version=ip_version,
            source_ipv4=source_ipv4,
            source_ipv6=source_ipv6,
        )

        if not command:
            return {
                "device_id": device_id,
                "device_name": device.get("name", device_id),
                "platform": device["platform"],
                "location": device.get("location", {}),
                "network": device.get("network", {}),
                "status": "error",
                "response_time_ms": 0,
                "query_type": query_type,
                "target": target,
                "output": "",
                "error": f"Query type ({query_type}) is not supported on platform ({device['platform']}).",
            }

        start = time.monotonic()
        output = await execute_on_device(command, device)
        elapsed = round((time.monotonic() - start) * 1000)

        result = {
            "device_id": device_id,
            "device_name": device.get("name", device_id),
            "platform": device["platform"],
            "location": device.get("location", {}),
            "network": device.get("network", {}),
            "status": "success",
            "response_time_ms": elapsed,
            "query_type": query_type,
            "target": target,
            "output": output,
            "cached": False,
        }

        await self.cache.set(query_type, target, device_id, result)
        return result
