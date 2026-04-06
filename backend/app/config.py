from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List


class Settings(BaseSettings):
    # App
    ENVIRONMENT: str = "production"
    SECRET_KEY: str = "change-me"
    APP_NAME: str = "Spyglass"
    APP_VERSION: str = "1.0.0"
    PRIMARY_ASN: int = 0
    ORG_NAME: str = ""
    WEBSITE_URL: str = ""
    PEERINGDB_URL: str = ""

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://spyglass:password@localhost:5432/spyglass"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Proxy Token (required for all API calls behind a reverse proxy)
    API_PROXY_TOKEN: str = "change-me-to-a-random-token"
    REQUIRE_API_TOKEN: bool = True

    # CORS (needed when frontend and backend are on different domains)
    CORS_ORIGINS: List[str] = []

    # Allowed WebSocket origins (e.g. ["https://lg.example.com"])
    ALLOWED_ORIGINS: List[str] = []

    # Session token
    SESSION_TOKEN_TTL: int = 600  # 10 minutes
    SESSION_TOKEN_MAX_USES: int = 30

    # Rate Limiting
    RATE_LIMIT_QUERY: int = 5
    RATE_LIMIT_QUERY_WINDOW: int = 60
    RATE_LIMIT_GENERAL: int = 30
    RATE_LIMIT_GENERAL_WINDOW: int = 60

    # SSH
    SSH_TIMEOUT: int = 10
    SSH_COMMAND_TIMEOUT: int = 30

    # Cache
    CACHE_TTL: int = 120

    # Query
    MAX_DEVICES_PER_QUERY: int = 5
    MAX_CONCURRENT_PER_IP: int = 3
    QUERY_TIMEOUT: int = 360

    # Device credentials (override YAML values)
    DEVICE_SSH_USERNAME: str = ""
    DEVICE_SSH_PASSWORD: str = ""

    # Config paths
    DEVICES_CONFIG_PATH: str = "config/devices.yaml"
    COMMANDS_CONFIG_PATH: str = "config/commands.yaml"
    ACL_CONFIG_PATH: str = "config/acl.yaml"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "case_sensitive": True}


settings = Settings()
