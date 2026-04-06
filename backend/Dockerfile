FROM python:3.11-slim AS base

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends openssh-client && \
    rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .

# Pre-install dependencies from pyproject.toml
RUN pip install --no-cache-dir \
    "fastapi>=0.110.0" \
    "uvicorn[standard]>=0.27.0" \
    "pydantic>=2.6.0" \
    "pydantic-settings>=2.1.0" \
    "sqlalchemy[asyncio]>=2.0.25" \
    "asyncpg>=0.29.0" \
    "alembic>=1.13.0" \
    "redis[hiredis]>=5.0.0" \
    "netmiko>=4.3.0" \
    "asyncssh>=2.14.0" \
    "pyyaml>=6.0.1" \
    "httpx>=0.27.0" \
    "python-multipart>=0.0.6" \
    "structlog>=24.1.0"

COPY . .

# --- Development ---
FROM base AS dev
RUN pip install --no-cache-dir pytest pytest-asyncio pytest-cov fakeredis ruff
ENV PYTHONPATH=/app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# --- Production ---
FROM base AS production
ENV PYTHONPATH=/app
RUN useradd -r -s /bin/false appuser && chown -R appuser:appuser /app
USER appuser
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
