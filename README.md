# Spyglass

[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React 18](https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=white)](https://react.dev/)
[![TypeScript 5](https://img.shields.io/badge/TypeScript-5-3178C6?logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Redis 7+](https://img.shields.io/badge/Redis-7%2B-DC382D?logo=redis&logoColor=white)](https://redis.io/)
[![Demo](https://img.shields.io/badge/Live_Demo-▶_Try_it-blueviolet)](https://spyglass.mehmet.tech)

> **[Live Demo](https://spyglass.mehmet.tech)** — Fully functional demo connected to [Route Views](http://www.routeviews.org/) (University of Oregon) public route server. Try a BGP Route lookup!

A modern, web-based network looking glass for ISPs and network operators. Run BGP route, ping, and traceroute queries across your network infrastructure from a clean, responsive UI.

## Features

**Query Types**

- **BGP Route** — IPv4/IPv6 routing table lookup
- **BGP Community** — Filter routes by community value
- **BGP AS Path** — Route lookup by AS path regex
- **Ping** — ICMP ping test (5 packets)
- **Traceroute** — Path tracing

**Supported Platforms (13)**

| Platform | Identifier |
|---|---|
| Cisco IOS-XR | `cisco_iosxr` |
| Juniper Junos | `juniper_junos` |
| Cisco IOS | `cisco_ios` |
| Cisco NX-OS | `cisco_nxos` |
| Arista EOS | `arista_eos` |
| Huawei VRP | `huawei_vrp` |
| Nokia SR OS | `nokia_sros` |
| MikroTik | `mikrotik` |
| FRRouting | `frrouting` |
| BIRD | `bird` |
| OpenBGPD | `openbgpd` |
| VyOS | `vyos` |
| TNSR | `tnsr` |

**Security & Performance**

- 3-tier rate limiting (frontend debounce, Nginx `limit_req`, Redis sliding window)
- Input validation and sanitization (RFC-compliant IP/prefix checks)
- Command whitelist to prevent injection
- X-Forwarded-For spoofing protection
- Security headers (HSTS, CSP, X-Frame-Options, and more)
- Real-time streaming output via WebSocket and SSE

## Quick Start

### Prerequisites

- Docker and Docker Compose
- (Optional) Python 3.11+ — for generating a secret key

### Development

```bash
# Clone the repository
git clone <repo-url> && cd lg

# Run the setup script
bash scripts/setup.sh
```

The script creates a `.env` file, starts all services, and runs database migrations.

- Frontend: http://localhost:5173
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/api/docs

### Production

```bash
cp .env.example .env
# Update DB_PASSWORD, REDIS_PASSWORD, and SECRET_KEY in .env
# Copy SSL certificates to nginx/ssl/

docker compose up -d --build
docker compose exec backend alembic upgrade head
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|---|---|---|
| `ENVIRONMENT` | `production` | Runtime environment (`production` / `development`) |
| `APP_NAME` | `Spyglass` | Application display name |
| `ORG_NAME` | `Your Organization` | Organization name shown in the UI and API |
| `PRIMARY_ASN` | `65000` | Your primary AS number |
| `SITE_URL` | `https://lg.example.com` | Public URL of the looking glass |
| `SECRET_KEY` | — | Application secret key |
| `ENABLE_DOCS` | `false` | Enable Swagger/ReDoc UI |
| `DB_PASSWORD` | — | PostgreSQL password |
| `DATABASE_URL` | — | Async PostgreSQL connection string |
| `REDIS_PASSWORD` | — | Redis password |
| `REDIS_URL` | — | Redis connection string |
| `CORS_ORIGINS` | `["https://lg.example.com"]` | Allowed CORS origins (JSON array) |
| `RATE_LIMIT_QUERY` | `20` | Query endpoint: requests per window |
| `RATE_LIMIT_QUERY_WINDOW` | `60` | Query endpoint: window duration (seconds) |
| `RATE_LIMIT_GENERAL` | `60` | General API: requests per window |
| `RATE_LIMIT_GENERAL_WINDOW` | `60` | General API: window duration (seconds) |
| `SSH_TIMEOUT` | `10` | SSH connection timeout (seconds) |
| `SSH_COMMAND_TIMEOUT` | `30` | SSH command execution timeout (seconds) |
| `CACHE_TTL` | `120` | Query cache duration (seconds) |

### `config/devices.yaml`

Defines the network devices available for queries. Each device specifies an `id`, `name`, `host`, `platform`, location info, and network parameters (ASN, source IP).

```yaml
devices:
  - id: route-server-01
    name: "Route-Server-01"
    host: "10.0.1.1"
    platform: cisco_iosxr
    location:
      city: "New York"
      facility: "Equinix NY5"
    network:
      asn: 65000
      ipv4_source: "198.51.100.1"
```

### `config/commands.yaml`

Contains command templates for each platform and query type. Uses `{target}`, `{source_ipv4}`, `{source_ipv6}` placeholders.

### `config/acl.yaml`

Defines denied IP prefixes (private networks, loopback, multicast, etc.) and prefix length limits.

## Directory Structure

```
lg/
├── backend/              # FastAPI application
│   ├── app/
│   │   ├── api/          # Endpoints and middleware
│   │   ├── core/         # Logging, SSH, security
│   │   ├── models/       # SQLAlchemy models
│   │   ├── schemas/      # Pydantic schemas
│   │   ├── services/     # Business logic
│   │   ├── config.py     # Application settings
│   │   └── main.py       # FastAPI app factory
│   ├── alembic/          # Database migrations
│   ├── tests/            # Pytest tests
│   ├── Dockerfile
│   └── pyproject.toml
├── frontend/             # React + TypeScript SPA
│   ├── src/
│   │   ├── components/   # UI components
│   │   ├── store/        # Zustand state management
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── Dockerfile
│   └── package.json
├── config/               # YAML configuration files
│   ├── devices.yaml      # Device definitions
│   ├── commands.yaml     # Per-platform command templates
│   └── acl.yaml          # Access control list
├── nginx/
│   ├── nginx.conf        # Reverse proxy configuration
│   └── ssl/              # TLS certificates (not in git)
├── scripts/
│   ├── setup.sh          # Development setup script
│   ├── generate_secret.py
│   └── seed_db.py
├── docs/                 # Additional documentation
├── docker-compose.yml    # Production Docker Compose
├── docker-compose.dev.yml# Development Docker Compose
├── Makefile              # Shortcut commands
├── .env.example          # Example environment variables
└── .gitignore
```

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/v1/query` | Execute a network query |
| `GET` | `/api/v1/devices` | List available devices |
| `GET` | `/api/v1/health` | System health check |
| `GET` | `/api/v1/info` | Application and AS info |

For detailed API documentation, see [docs/API.md](docs/API.md).

## Makefile Commands

```bash
make dev          # Start development environment
make prod         # Start production environment
make down         # Stop all services
make logs         # Follow production logs
make migrate      # Run database migrations
make seed         # Load sample data
make test         # Run all tests
make lint         # Run lint checks
make clean        # Stop services, remove volumes and cache
```

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11+, FastAPI, SQLAlchemy 2, Alembic, asyncssh/Netmiko |
| Frontend | React 18, TypeScript 5, Tailwind CSS, Zustand |
| Database | PostgreSQL 15 |
| Cache / Rate Limit | Redis 7 |
| Reverse Proxy | Nginx |
| Containerization | Docker, Docker Compose |

## Documentation

- [Security](docs/SECURITY.md)
- [Deployment](docs/DEPLOYMENT.md)
- [API Reference](docs/API.md)
- [Rate Limiting](docs/RATE_LIMITING.md)

## License

See [LICENSE](LICENSE).
