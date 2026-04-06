# Security Audit Report

**Date:** 2026-03-28
**Scope:** Full-stack application (backend, frontend, infrastructure)
**Application:** Spyglass

---

## Summary

| Severity | Count | Fixed | Accepted Risk |
|----------|-------|-------|---------------|
| CRITICAL | 3     | 3     | 0             |
| HIGH     | 5     | 5     | 0             |
| MEDIUM   | 7     | 7     | 0             |
| LOW/INFO | 8+    | 2     | 6+            |

---

## CRITICAL Findings

### SEC-001: WebSocket Origin Validation Bypass

- **Severity:** CRITICAL
- **File:** `backend/app/api/v1/endpoints/ws_query.py` (L90-97)
- **Status:** FIXED

**Description:**
The WebSocket endpoint checked `if not (sec_fetch == "same-origin" or origin)` which accepted ANY truthy Origin header value. An attacker could connect from `https://evil.com` and the check would pass because the `origin` variable is a non-empty string.

**Before:**
```python
if not (sec_fetch == "same-origin" or origin):
    await websocket.close(code=4003, reason="Forbidden")
```

**Fix:**
- Replaced with strict Origin allowlist validation using `settings.ALLOWED_ORIGINS`
- Added proxy token validation via `X-API-Token` header on WS handshake
- Falls back to `Sec-Fetch-Site: same-origin` check only when token present

---

### SEC-002: WebSocket Not Protected by API Token Middleware

- **Severity:** CRITICAL
- **File:** `backend/app/api/middleware/api_token.py` (L19), `nginx/nginx.conf.template` (L129-142)
- **Status:** FIXED

**Description:**
`ApiTokenMiddleware` only checked paths starting with `/api/`. The WebSocket endpoint at `/ws/query` was completely outside this protection. The nginx template also did not forward `X-API-Token` for WebSocket connections.

**Fix:**
- Added `proxy_set_header X-API-Token` to nginx `/ws/` location block
- Added token validation in `ws_query.py` handshake before accepting connection
- Backend verifies the token using constant-time comparison (`hmac.compare_digest`)

---

### SEC-003: Plaintext SSH Credentials in devices.yaml

- **Severity:** CRITICAL
- **File:** `config/devices.yaml` (L6-7)
- **Status:** FIXED

**Description:**
Device SSH credentials (`username`/`password`) were stored in plaintext in the YAML config file. If the repository or container were compromised, credentials would be directly exposed.

**Fix:**
- Credentials now read from environment variables (`DEVICE_SSH_USERNAME`, `DEVICE_SSH_PASSWORD`)
- YAML file uses placeholder values as documentation
- `docker-compose.yml` and `.env` updated to supply credentials via env vars

---

## HIGH Findings

### SEC-004: X-Real-IP Header Accepted Without Proxy Validation

- **Severity:** HIGH
- **File:** `backend/app/api/middleware/trusted_proxy.py` (L31-38)
- **Status:** FIXED

**Description:**
The `get_client_ip()` function unconditionally trusted the `X-Real-IP` header from any client, regardless of whether the connecting IP was a trusted proxy. An attacker could spoof their IP to bypass rate limiting and logging.

**Before:**
```python
x_real_ip = request.headers.get("x-real-ip")
if x_real_ip:
    real_ip = x_real_ip.strip()
    # Accepted from anyone
```

**Fix:**
- `X-Real-IP` is now only accepted when `request.client.host` is within the trusted proxy CIDR list

---

### SEC-005: Empty device_ids Allows Querying All Devices (DoS)

- **Severity:** HIGH
- **File:** `backend/app/api/v1/endpoints/query.py` (L20-22)
- **Status:** FIXED

**Description:**
When `device_ids` was empty or omitted, the endpoint queried ALL configured devices in parallel, consuming SSH connections and potentially causing denial of service.

**Fix:**
- Empty `device_ids` now defaults to only the first device
- Enforced `MAX_DEVICES_PER_QUERY` limit from settings

---

### SEC-006: Overly Broad Command Regex in device_connector

- **Severity:** HIGH
- **File:** `backend/app/services/device_connector.py` (L12-84)
- **Status:** FIXED

**Description:**
Command allowlist patterns used `\S+` which matches any non-whitespace character including `;`, `|`, `&`, etc. While forbidden pattern checks catch most injection, device-specific interpreter syntax could potentially be exploited.

**Before:**
```python
r"^ping \S+",
r"^traceroute \S+",
```

**Fix:**
- Replaced `\S+` with strict IP/prefix regex: `[0-9a-fA-F:.\/]+`
- Added `$` anchors to prevent trailing injection
- Source/count parameters also constrained to safe character sets

---

### SEC-007: Frontend Submit Without Validation

- **Severity:** HIGH
- **File:** `frontend/src/components/query/QueryForm.tsx` (L15-18)
- **Status:** FIXED

**Description:**
The `handleSubmit` function only checked if the target was non-empty, but did not call `isValidTarget()`. Users could submit malformed targets that would only be caught by backend validation.

**Fix:**
- Added `isValidTarget(target, queryType)` check in `canSubmit` logic
- Invalid targets now blocked before WebSocket connection is opened

---

### SEC-008: docker-compose.dev.yml Exposes Ports to All Interfaces

- **Severity:** HIGH
- **File:** `docker-compose.dev.yml` (L12, L44, L54)
- **Status:** FIXED

**Description:**
Database (PostgreSQL), cache (Redis), and frontend dev server ports were mapped to `0.0.0.0` (all interfaces), making them accessible from the network with weak hardcoded passwords.

**Fix:**
- All dev port mappings now bind to `127.0.0.1` only

---

## MEDIUM Findings

### SEC-009: Internal Error Messages Leaked to Users

- **Severity:** MEDIUM
- **Files:**
  - `backend/app/api/v1/endpoints/ws_query.py` (L73-74, L140-141)
  - `backend/app/api/v1/endpoints/stream.py` (L76-78, L100-102)
  - `backend/app/services/device_connector.py` (L143-144)
- **Status:** FIXED

**Description:**
SSH/Netmiko exception messages were passed directly to users via `str(e)`. These could reveal internal hostnames, IP addresses, authentication failures, or stack traces.

**Fix:**
- All user-facing error messages replaced with generic text
- Original exception details logged server-side only

---

### SEC-010: ACL Checker Fails Open When Config Missing

- **Severity:** MEDIUM
- **File:** `backend/app/services/acl_checker.py` (L15-18)
- **Status:** FIXED

**Description:**
If `acl.yaml` was missing or unreadable, the ACL checker silently initialized with empty deny lists, allowing all targets.

**Fix:**
- Missing ACL config now logs a warning and defaults to deny-all mode
- Invalid YAML entries also logged instead of silently ignored

---

### SEC-011: IPv6 Normalization Bypass in ACL Checker

- **Severity:** MEDIUM
- **File:** `backend/app/services/acl_checker.py` (L35-37)
- **Status:** FIXED

**Description:**
`denied_hosts` was compared using string equality. Different representations of the same IPv6 address (e.g., `::1` vs `0:0:0:0:0:0:0:1`) would not match.

**Fix:**
- Host comparison now uses `ipaddress.ip_address()` for normalization before comparison

---

### SEC-012: Request ID Unlimited Length (Log Injection)

- **Severity:** MEDIUM
- **File:** `backend/app/api/middleware/request_id.py` (L9)
- **Status:** FIXED

**Description:**
Client-supplied `X-Request-ID` was accepted without length or format validation. An attacker could send extremely long or crafted IDs to inject content into log files.

**Fix:**
- Request ID validated: max 128 chars, restricted to `[a-zA-Z0-9_-]` characters
- Invalid IDs replaced with server-generated UUID

---

### SEC-013: Stream Endpoint Missing query_type Allowlist

- **Severity:** MEDIUM
- **File:** `backend/app/api/v1/endpoints/stream.py` (L82-87)
- **Status:** FIXED

**Description:**
The HTTP streaming endpoint did not validate `query_type` against `SUPPORTED_QUERY_TYPES`. Unsupported types would pass through to the command builder, potentially producing unexpected behavior.

**Fix:**
- Added `SUPPORTED_QUERY_TYPES` check at the start of the handler
- Invalid query types rejected with an error stream response

---

### SEC-014: Security Error Messages Include User Input

- **Severity:** MEDIUM
- **File:** `backend/app/core/security.py` (L58-61)
- **Status:** FIXED

**Description:**
The `_check_forbidden_patterns` function included the full user input in the error message using `{value!r}`. This could help attackers enumerate which patterns are blocked.

**Before:**
```python
raise SecurityError(f"Forbidden character or command detected: {value!r}")
```

**Fix:**
- Error message is now generic without echoing the input
- Input details logged server-side for debugging

---

### SEC-015: Production Startup with Default Tokens

- **Severity:** MEDIUM
- **File:** `backend/app/config.py`, `backend/app/main.py`
- **Status:** FIXED

**Description:**
The application could start in production mode with default/placeholder values for `SECRET_KEY` and `API_PROXY_TOKEN`, leaving the system unprotected.

**Fix:**
- Startup check added in `create_app()`: if `ENVIRONMENT == "production"` and tokens contain `"change-me"`, the application raises a `RuntimeError` and refuses to start

---

## LOW / INFO Findings

### SEC-016: HSTS Header in All Environments

- **Severity:** LOW
- **File:** `backend/app/api/middleware/security_headers.py` (L13)
- **Status:** ACCEPTED RISK

**Description:**
`Strict-Transport-Security` header is set in development too, which can cause browser issues with local HTTP.

**Note:** Accepted since dev environment uses Docker networking and doesn't serve directly to browsers.

---

### SEC-017: Health Endpoint Information Disclosure

- **Severity:** LOW
- **File:** `backend/app/api/v1/endpoints/health.py`
- **Status:** ACCEPTED RISK

**Description:**
Health endpoint exposes device count and Redis connectivity status to unauthenticated users.

**Note:** Standard for monitoring integration. Considered acceptable for a looking glass service.

---

### SEC-018: Client-Side Rate Limiter Is UX Only

- **Severity:** INFO
- **File:** `frontend/src/lib/rateLimiter.ts`
- **Status:** ACCEPTED RISK

**Description:**
The frontend rate limiter runs in the browser and can be trivially bypassed. Rate limiting enforcement is server-side.

**Note:** Client-side limiter exists for UX purposes only. Backend enforcement is the security boundary.

---

### SEC-019: Third-Party IP Detection (ipify)

- **Severity:** LOW
- **File:** `frontend/src/components/query/TargetInput.tsx` (L28-31)
- **Status:** ACCEPTED RISK

**Description:**
"My IP" button sends user's IP to `api.ipify.org`. Privacy-conscious users may object.

**Note:** Common practice for looking glass services. Alternative would be a backend endpoint using the proxy-resolved client IP.

---

### SEC-020: Global Toast Events

- **Severity:** LOW
- **File:** `frontend/src/components/ui/Toast.tsx`
- **Status:** ACCEPTED RISK

**Description:**
Custom events (`show-toast`, `rate-limit-exceeded`) on `window` can be triggered by browser extensions or injected scripts.

**Note:** No security impact; purely UX. CSP headers mitigate injection risk.

---

### SEC-021: Weak IPv4 Regex in Frontend Validator

- **Severity:** LOW
- **File:** `frontend/src/lib/validators.ts` (L1)
- **Status:** ACCEPTED RISK

**Description:**
Frontend IPv4 regex doesn't enforce valid octet ranges (0-255). `999.999.999.999` would pass client-side validation.

**Note:** Backend performs strict validation using Python's `ipaddress` module. Frontend validation is UX only.

---

### SEC-022: Cookie Session Race Condition

- **Severity:** LOW
- **File:** `backend/app/api/middleware/cookie_session.py` (L91-113)
- **Status:** ACCEPTED RISK

**Description:**
Session validation (`hgetall` + usage check + `hincrby`) is not atomic. Under high concurrency, `max_uses` could be slightly exceeded.

**Note:** Cookie session middleware is a secondary defense layer. Rate limiting is the primary control.

---

### SEC-023: Nginx set_real_ip_from Uses Broad RFC1918 Ranges

- **Severity:** LOW
- **File:** `nginx/nginx.conf.template` (L14-16)
- **Status:** ACCEPTED RISK

**Description:**
All RFC1918 private ranges are trusted for `set_real_ip_from`. In a shared hosting environment, another container could spoof source IPs.

**Note:** Acceptable for dedicated Docker infrastructure. Should be narrowed to specific LB/proxy CIDRs in shared environments.

---

## Remediation Timeline

All CRITICAL and HIGH findings were fixed immediately. MEDIUM findings were fixed in the same session. LOW/INFO findings were documented and accepted where the risk-benefit trade-off justified it.
