# Spyglass

[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React 18](https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=white)](https://react.dev/)
[![TypeScript 5](https://img.shields.io/badge/TypeScript-5-3178C6?logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Demo](https://img.shields.io/badge/Live_Demo-▶_Try_it-blueviolet)](https://spyglass.mehmet.tech)

> **[Live Demo](https://spyglass.mehmet.tech)** — BGP Route, Ping, and Traceroute

A modern, open-source network looking glass for ISPs and network operators. Connect your routers and let anyone run BGP route lookups, ping, and traceroute queries through a clean web UI.

## Features

- **BGP Route / Community / AS Path** — IPv4 and IPv6 routing table lookups
- **Ping** — ICMP echo from router or local server
- **Traceroute** — Hop-by-hop path tracing
- **13 router platforms** — Cisco IOS/IOS-XR/NX-OS, Juniper, Arista, Huawei, Nokia, MikroTik, FRRouting, BIRD, VyOS, and more
- **Local execution** — Optional `local` platform to run ping/traceroute directly on the Spyglass server
- **Real-time streaming** — Live output via WebSocket
- **Security hardened** — Command whitelist, input validation, rate limiting, security headers

## Quick Start

### 1. Clone and configure

```bash
git clone https://github.com/musanmaz/spyglass.git
cd spyglass

# Create environment file
cp .env.example .env
```

Edit `.env` and set at minimum:

```bash
SECRET_KEY=<random-secret>          # python3 -c "import secrets; print(secrets.token_urlsafe(48))"
DB_PASSWORD=<strong-password>
REDIS_PASSWORD=<strong-password>
ORG_NAME=Your ISP Name
PRIMARY_ASN=65000
SERVER_NAME=lg.example.com
```

### 2. Configure your devices

```bash
cp config/devices.yaml.example config/devices.yaml
```

Edit `config/devices.yaml` and add your routers:

```yaml
devices:
  # SSH router — all query types
  - id: core-01
    name: "Core Router — Istanbul"
    host: "10.0.1.1"
    platform: cisco_iosxr        # See supported platforms below
    protocol: ssh                # ssh or telnet
    username: "lookingglass"
    password: "secret"           # Or use DEVICE_SSH_PASSWORD env var
    location:
      city: "Istanbul"
      country: "TR"
      facility: "Equinix IS1"
    network:
      asn: 65000
      as_name: "My Network"
      ipv4_source: "198.51.100.1"
      ipv6_source: "2001:db8::1"
    ssh:
      port: 22
      timeout: 10

  # Restrict a device to specific query types
  - id: edge-01
    name: "Edge Router — Frankfurt"
    host: "10.0.2.1"
    platform: juniper_junos
    username: "lookingglass"
    password: "secret"
    location:
      city: "Frankfurt"
      country: "DE"
    network:
      asn: 65000
      as_name: "My Network"
      ipv4_source: "198.51.100.2"
    ssh:
      port: 22
      timeout: 10
    directives:              # Only allow these query types
      - bgp_route
      - bgp_community

  # Optional: run ping/traceroute from the Spyglass server itself
  - id: local
    name: "Istanbul (Local)"
    platform: local
    location:
      city: "Istanbul"
      country: "TR"
    network:
      asn: 65000
      as_name: "My Network"
    directives:
      - ping
      - traceroute
```

### 3. Start the services

```bash
docker compose up -d --build
docker compose exec backend alembic upgrade head
```

Your looking glass is now running at `https://lg.example.com` (after configuring Nginx/SSL).

## Supported Platforms

| Platform | `platform` value | SSH | Telnet |
|---|---|---|---|
| Cisco IOS-XR | `cisco_iosxr` | yes | yes |
| Cisco IOS | `cisco_ios` | yes | yes |
| Cisco NX-OS | `cisco_nxos` | yes | — |
| Juniper Junos | `juniper_junos` | yes | yes |
| Arista EOS | `arista_eos` | yes | — |
| Huawei VRP | `huawei_vrp` | yes | — |
| Nokia SR OS | `nokia_sros` | yes | — |
| MikroTik RouterOS | `mikrotik` | yes | — |
| FRRouting | `frrouting` | yes | — |
| BIRD | `bird` | yes | — |
| OpenBGPD | `openbgpd` | yes | — |
| VyOS | `vyos` | yes | — |
| TNSR | `tnsr` | yes | — |
| **Local Server** | `local` | — | — |

The `local` platform runs `ping` and `traceroute` as subprocess on the Spyglass server. Useful when your router doesn't support these commands or you want to add ping/traceroute without giving access to a router.

## Configuration Reference

### Environment Variables

See [`.env.example`](.env.example) for all available variables with descriptions.

Key settings:

| Variable | Description |
|---|---|
| `ORG_NAME` | Your organization name (shown in UI) |
| `PRIMARY_ASN` | Your AS number |
| `SECRET_KEY` | App secret — **must be changed** |
| `DB_PASSWORD` / `REDIS_PASSWORD` | Database credentials |
| `DEVICE_SSH_USERNAME` / `DEVICE_SSH_PASSWORD` | Global device credentials (overrides per-device) |
| `REQUIRE_API_TOKEN` | `true` (default) for same-origin deploy, `false` for split frontend/backend |
| `CORS_ORIGINS` | Allowed frontend origins as JSON array |

### Config Files

| File | Description |
|---|---|
| `config/devices.yaml` | Your device definitions (gitignored — copy from `.example`) |
| `config/commands.yaml` | Command templates per platform (rarely needs editing) |
| `config/acl.yaml` | Denied IP prefixes and prefix length limits |

### Router User Setup

Create a **read-only** user on your router for the looking glass:

**Cisco IOS-XR:**
```
username lookingglass
 group operator
 secret <password>
```

**Juniper Junos:**
```
set system login user lookingglass class read-only
set system login user lookingglass authentication plain-text-password
```

**Cisco IOS:**
```
username lookingglass privilege 1 secret <password>
```

> Use the minimum privilege level needed. The looking glass only runs `show`, `ping`, and `traceroute` commands — write access is **never** required.

## Development

```bash
# Start dev environment (hot reload)
docker compose -f docker-compose.dev.yml up -d

# Or use the setup script
bash scripts/setup.sh
```

- Frontend: http://localhost:5173
- Backend: http://localhost:8000

```bash
# Run tests
make test

# Lint
make lint
```

## Architecture

```
┌──────────────┐     WebSocket / SSE     ┌──────────────┐     SSH / Telnet    ┌────────────┐
│   Browser    │ ◄──────────────────────► │   Backend    │ ◄─────────────────► │  Router(s) │
│  (React)     │                          │  (FastAPI)   │                     └────────────┘
└──────────────┘                          │              │     subprocess      ┌────────────┐
                                          │              │ ◄─────────────────► │ ping / tr  │
                                          └──────┬───────┘                     └────────────┘
                                                 │
                                          ┌──────┴───────┐
                                          │  PostgreSQL   │
                                          │  Redis        │
                                          └──────────────┘
```

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11+, FastAPI, SQLAlchemy 2, Netmiko |
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

[MIT](LICENSE)
