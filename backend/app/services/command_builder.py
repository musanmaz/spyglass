from pathlib import Path
from typing import Dict, Optional
import yaml

class CommandBuilder:
    def __init__(self, config_path: str = "config/commands.yaml"):
        self._commands: Dict = {}
        self._load_config(config_path)

    def _load_config(self, config_path: str) -> None:
        path = Path(config_path)
        if not path.exists():
            return
        with open(path) as f:
            self._commands = yaml.safe_load(f).get("platforms", {})

    def build(self, platform: str, query_type: str, target: str, ip_version: int = 4, source_ipv4: str = "", source_ipv6: str = "") -> Optional[str]:
        platform_cmds = self._commands.get(platform, {})
        type_cmds = platform_cmds.get(query_type, {})
        
        version_key = "ipv6" if ip_version == 6 else "ipv4"
        template = type_cmds.get(version_key) or type_cmds.get("ipv4")
        
        if not template:
            return None

        cmd = template.format(
            target=target,
            source_ipv4=source_ipv4,
            source_ipv6=source_ipv6,
        )

        import re
        cmd = re.sub(r'\s+source\s+(?=\s|$)', ' ', cmd)
        cmd = re.sub(r'\s{2,}', ' ', cmd).strip()
        return cmd

    def get_supported_queries(self, platform: str) -> list[str]:
        return list(self._commands.get(platform, {}).keys())
