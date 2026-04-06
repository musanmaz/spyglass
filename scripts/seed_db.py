#!/usr/bin/env python3
"""Seed database with initial device data from config/devices.yaml."""

import asyncio
import yaml
from pathlib import Path


async def seed() -> None:
    config_path = Path(__file__).parent.parent / "config" / "devices.yaml"
    with open(config_path) as f:
        data = yaml.safe_load(f)

    print(f"Found {len(data.get('devices', []))} devices in config")
    for device in data.get("devices", []):
        print(f"  - {device['id']}: {device['name']} ({device['platform']})")

    print("Seed complete. Devices are loaded from YAML at runtime.")


if __name__ == "__main__":
    asyncio.run(seed())
