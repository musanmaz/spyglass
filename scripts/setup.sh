#!/usr/bin/env bash
set -euo pipefail

echo "=== Spyglass — Setup ==="

if [ ! -f .env ]; then
    echo "Creating .env from .env.example..."
    cp .env.example .env
    SECRET_KEY=$(python3 scripts/generate_secret.py 2>/dev/null || python3 -c "import secrets; print(secrets.token_urlsafe(48))")
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' "s/change-me-generate-a-random-secret/$SECRET_KEY/" .env
    else
        sed -i "s/change-me-generate-a-random-secret/$SECRET_KEY/" .env
    fi
    echo "Generated SECRET_KEY in .env"
    echo "WARNING: Change DB_PASSWORD and REDIS_PASSWORD before production use!"
else
    echo ".env already exists, skipping."
fi

if [ ! -f config/devices.yaml ]; then
    echo ""
    echo "Creating config/devices.yaml from example..."
    cp config/devices.yaml.example config/devices.yaml
    echo "IMPORTANT: Edit config/devices.yaml and add your router(s)."
else
    echo "config/devices.yaml already exists, skipping."
fi

echo ""
echo "=== Starting services ==="
docker compose -f docker-compose.dev.yml up --build -d

echo ""
echo "=== Waiting for database ==="
sleep 5

echo ""
echo "=== Running migrations ==="
docker compose -f docker-compose.dev.yml exec backend alembic upgrade head

echo ""
echo "=== Setup complete ==="
echo "Frontend: http://localhost:5173"
echo "Backend:  http://localhost:8000"
echo "API Docs: http://localhost:8000/api/docs"
