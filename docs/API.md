# API Referansi

Spyglass API dokumantasyonu.

---

## Genel Bilgiler

| Bilgi | Deger |
|---|---|
| Base URL | `https://lg.example.com/api/v1` |
| Protokol | HTTPS (TLS 1.2+) |
| Icerik Tipi | `application/json` |
| Kimlik Dogrulama | Yok (herkese acik API) |
| Rate Limiting | IP bazli, 3 katmanli |

## Endpointler

### POST /api/v1/query

Belirtilen cihaz(lar) uzerinde ag sorgusu calistirir.

**Istek Govdesi:**

```json
{
  "query_type": "bgp_route",
  "target": "1.1.1.0/24",
  "address_family": "ipv4",
  "device_ids": ["route-server-01"]
}
```

| Alan | Tip | Zorunlu | Aciklama |
|---|---|---|---|
| `query_type` | string | Evet | Sorgu turu: `bgp_route`, `bgp_community`, `bgp_aspath`, `ping`, `traceroute` |
| `target` | string | Evet | Sorgu hedefi (IP, prefix, community, AS path regex) |
| `address_family` | string | Hayir | `ipv4` (varsayilan) veya `ipv6` |
| `device_ids` | string[] | Evet | Sorgulanacak cihaz ID listesi (en fazla 5) |

**Basarili Yanit (200):**

```json
{
  "query_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "query_type": "bgp_route",
  "target": "1.1.1.0/24",
  "address_family": "ipv4",
  "timestamp": "2025-01-15T10:30:00Z",
  "results": [
    {
      "device_id": "route-server-01",
      "device_name": "Route-Server-01",
      "status": "success",
      "output": "BGP routing table entry for 1.1.1.0/24\n  Paths: (3 available)...",
      "execution_time_ms": 1234,
      "cached": false
    }
  ]
}
```

**Sorgu Turu Ornekleri:**

BGP Route:
```json
{ "query_type": "bgp_route", "target": "8.8.8.0/24", "device_ids": ["route-server-01"] }
```

BGP Community:
```json
{ "query_type": "bgp_community", "target": "65000:100", "device_ids": ["route-server-01"] }
```

BGP AS Path:
```json
{ "query_type": "bgp_aspath", "target": "^65000_", "device_ids": ["route-server-01"] }
```

Ping:
```json
{ "query_type": "ping", "target": "1.1.1.1", "device_ids": ["route-server-01"] }
```

Traceroute:
```json
{ "query_type": "traceroute", "target": "8.8.8.8", "device_ids": ["route-server-01"] }
```

---

### GET /api/v1/devices

Sorgu yapilabilecek cihazlarin listesini dondurur.

**Yanit (200):**

```json
{
  "devices": [
    {
      "id": "route-server-01",
      "name": "Route-Server-01",
      "platform": "cisco_iosxr",
      "location": {
        "city": "Istanbul",
        "country": "TR",
        "facility": "Equinix IS1",
        "coordinates": [41.0082, 28.9784]
      },
      "network": {
        "asn": 65000,
        "as_name": "Example Net"
      },
      "supported_queries": ["bgp_route", "bgp_community", "bgp_aspath", "ping", "traceroute"]
    }
  ]
}
```

---

### GET /api/v1/health

Sistem saglik kontrolu. Izleme araclari tarafindan kullanilabilir.

**Yanit (200):**

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "services": {
    "database": "ok",
    "redis": "ok"
  }
}
```

---

### GET /api/v1/info

Uygulama ve organizasyon bilgilerini dondurur.

**Yanit (200):**

```json
{
  "name": "Spyglass",
  "organization": "Your Organization",
  "primary_asn": 65000,
  "site_url": "https://lg.example.com",
  "peeringdb_url": "https://www.peeringdb.com/asn/65000",
  "supported_query_types": [
    { "id": "bgp_route", "name": "BGP Route" },
    { "id": "bgp_community", "name": "BGP Community" },
    { "id": "bgp_aspath", "name": "BGP AS Path" },
    { "id": "ping", "name": "Ping" },
    { "id": "traceroute", "name": "Traceroute" }
  ]
}
```

---

## Hata Yanitlari

Tum hata yanitlari ayni formati kullanir:

```json
{
  "detail": {
    "error": "<hata_kodu>",
    "message": "<aciklama>"
  }
}
```

### Hata Kodlari

| HTTP Kodu | Hata | Aciklama |
|---|---|---|
| `422` | `validation_error` | Girdi dogrulama hatasi. Gecersiz IP, prefix, community formati veya eksik zorunlu alan. |
| `429` | `rate_limit_exceeded` | Hiz siniri asildi. `Retry-After` basligindaki sureyi bekleyin. |
| `403` | `forbidden` | Yasakli hedef adresi (ozel ag, loopback vb.) veya erisim engeli. |
| `408` | `query_timeout` | Sorgu zaman asimina ugradi. Cihaza baglanti kurulamadi veya komut suresi doldu. |
| `500` | `internal_error` | Beklenmeyen sunucu hatasi. Loglar incelenmelidir. |

### Hata Ornekleri

**422 -- Dogrulama Hatasi:**
```json
{
  "detail": {
    "error": "validation_error",
    "message": "Gecersiz IPv4 adresi",
    "field": "target"
  }
}
```

**429 -- Hiz Siniri:**
```json
{
  "detail": {
    "error": "rate_limit_exceeded",
    "message": "Cok fazla istek. 42 saniye sonra tekrar deneyin."
  }
}
```

**403 -- Yasakli Adres:**
```json
{
  "detail": {
    "error": "forbidden",
    "message": "Hedef adres yasakli bir prefix icerisinde"
  }
}
```

---

## Rate Limiting Basiklari

Tum API yanitlarinda asagidaki basliklar bulunur:

| Baslik | Aciklama |
|---|---|
| `X-RateLimit-Limit` | Zaman penceresindeki toplam istek hakki |
| `X-RateLimit-Remaining` | Kalan istek hakki |
| `X-RateLimit-Reset` | Sinirin sifirlanacagi Unix timestamp |
| `Retry-After` | (yalnizca 429) Yeniden deneme icin beklenmesi gereken sure (saniye) |

---

## curl Ornekleri

**BGP Route Sorgusu:**

```bash
curl -X POST https://lg.example.com/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{
    "query_type": "bgp_route",
    "target": "1.1.1.0/24",
    "address_family": "ipv4",
    "device_ids": ["route-server-01"]
  }'
```

**Cihaz Listesi:**

```bash
curl -s https://lg.example.com/api/v1/devices | python3 -m json.tool
```

**Saglik Kontrolu:**

```bash
curl -s https://lg.example.com/api/v1/health
```

**Ping Sorgusu:**

```bash
curl -X POST https://lg.example.com/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{
    "query_type": "ping",
    "target": "8.8.8.8",
    "device_ids": ["route-server-01"]
  }'
```

**Traceroute Sorgusu (IPv6):**

```bash
curl -X POST https://lg.example.com/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{
    "query_type": "traceroute",
    "target": "2001:4860:4860::8888",
    "address_family": "ipv6",
    "device_ids": ["route-server-01"]
  }'
```

---

## Gelistirme Ortami

Gelistirme ortaminda Swagger UI ve ReDoc arayuzleri aktiftir:

- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc
- OpenAPI JSON: http://localhost:8000/api/openapi.json

Uretim ortaminda bu arayuzler varsayilan olarak kapalidir (`ENABLE_DOCS=false`).
