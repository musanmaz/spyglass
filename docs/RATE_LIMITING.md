# Hiz Sinirlandirma (Rate Limiting)

Bu belge, Spyglass platformundaki 3 katmanli hiz sinirlandirma mimarisini detayli olarak aciklar.

---

## Genel Bakis

Platform, kosturmali (cascading) 3 katmanli bir hiz sinirlandirma mimarisi kullanir. Her katman bir oncekinin gecirdigi istekleri filtreler:

```
Kullanici Tarayicisi
       |
  [Katman 0: Frontend]     -- Debounce, cooldown, lockout
       |
  [Katman 1: Nginx]        -- limit_req_zone, limit_conn_zone
       |
  [Katman 2: Uygulama]     -- Redis sliding window
       |
  [Backend Is Mantigi]
```

Bu yaklasimin avantajlari:

- Gereksiz istekler daha istemci tarafinda engellenir (sunucu yukunu azaltir).
- Nginx katmani, uygulamaya ulasmadan once ag seviyesinde koruma saglar.
- Redis katmani, birden fazla backend instansinda tutarli sinirlandirma saglar.
- Her katmanin basarisiz olmasi durumunda sonraki katman yedek gorevi gorur.

---

## Katman 0: Frontend

Frontend (React) tarafinda uygulanan istemci bazli koruma mekanizmalari.

### Parametreler

| Parametre | Deger | Kaynak |
|---|---|---|
| `max_requests` | 10 | `config/settings.yaml` -> `rate_limit.frontend.max_requests` |
| `window_seconds` | 60 | `config/settings.yaml` -> `rate_limit.frontend.window_seconds` |
| `cooldown_seconds` | 5 | `config/settings.yaml` -> `rate_limit.frontend.cooldown_seconds` |

### Mekanizmalar

**Debounce**: Kullanici sorgu formunu gonderdikten sonra `cooldown_seconds` suresi boyunca yeni istek gonderilemez. Buton devre disi kalir ve geri sayim gosterilir.

**Istek Sayaci**: `window_seconds` suresi icinde yapilan istek sayisi izlenir. `max_requests` siniri asildidinda kullaniciya uyari gosterilir ve yeni istek engellenir.

**Lockout**: Tekrarli sinir asilimlarinda kullanici arabirimi gecici olarak kilitlenir. Bu durum yalnizca tarayici tarafinda uygulanir ve tarayici yeniden yuklendiginde sifirlanir.

Bu katman bir guvenlik mekanizmasi degildir; kullanici deneyimini iyilestirmeye ve gereksiz istekleri azaltmaya yoneliktir.

---

## Katman 1: Nginx

Nginx `limit_req` ve `limit_conn` modulleri ile ag seviyesinde IP bazli sinirlandirma.

### Zone Tanimlari

```nginx
limit_req_zone $binary_remote_addr zone=api_query:10m rate=30r/m;
limit_req_zone $binary_remote_addr zone=api_general:10m rate=60r/m;
limit_req_zone $binary_remote_addr zone=static:10m rate=120r/m;
limit_conn_zone $binary_remote_addr zone=conn_limit:10m;
```

| Zone | Oran | Burst | Uygulama Alani |
|---|---|---|---|
| `api_query` | 30 istek/dakika | 5 | `/api/v1/query` endpointi |
| `api_general` | 60 istek/dakika | 10 | `/api/*` (query haric) |
| `static` | 120 istek/dakika | 30 | `/` (statik dosyalar) |
| `conn_limit` | 10 esanli baglanti | -- | Tum sunucu |

### Burst ve Nodelay

`burst` parametresi, ani trafik artislarinda belirtilen sayida ek istege izin verir. `nodelay` ile bu istekler bekletilmeden hemen islenir. Burst kapasitesi doldugunda ek istekler `429 Too Many Requests` ile reddedilir.

### XFF Cozumleme

```nginx
set_real_ip_from 10.0.0.0/8;
set_real_ip_from 172.16.0.0/12;
set_real_ip_from 192.168.0.0/16;
real_ip_header X-Forwarded-For;
real_ip_recursive on;
```

- Yalnizca ic ag bloklari guvenilir proxy olarak tanimlidir.
- `real_ip_recursive on` ile proxy zincirindeki ilk guvenilmez IP, gercek istemci IP'si olarak belirlenir.
- Dis kaynaklardan gelen sahte XFF basiklari dikkate alinmaz.
- Rate limiting `$binary_remote_addr` degiskenine (cozumlenmis gercek IP) uygulanir.

### HTTP Durum Kodlari

```nginx
limit_req_status 429;
limit_conn_status 429;
```

Sinir asiminda standart `429 Too Many Requests` donulur.

---

## Katman 2: Redis Sliding Window (Uygulama Katmani)

FastAPI middleware olarak calisan, Redis uzerinde kayan pencere (sliding window) algoritmasi kullanan hiz sinirlandirma.

### Parametreler

| Parametre | Varsayilan | Ortam Degiskeni | Aciklama |
|---|---|---|---|
| Sorgu limiti | 20 | `RATE_LIMIT_QUERY` | `/api/v1/query` icin pencere basina istek siniri |
| Sorgu penceresi | 60 sn | `RATE_LIMIT_QUERY_WINDOW` | Sorgu siniri zaman penceresi |
| Genel limit | 60 | `RATE_LIMIT_GENERAL` | Diger endpointler icin pencere basina istek siniri |
| Genel pencere | 60 sn | `RATE_LIMIT_GENERAL_WINDOW` | Genel sinir zaman penceresi |

### Calisma Prensibi

1. Her istek geldiginde, istemci IP'si ve endpoint bilgisi ile bir Redis anahtari olusturulur.
2. Redis sorted set yapisinda, her istegin timestamp'i skor olarak saklanir.
3. Zaman penceresinin disinda kalan kayitlar temizlenir.
4. Mevcut pencere icindeki kayit sayisi sinir degerle karsilastirilir.
5. Sinir asilmissa `429` yaniti donulur; asilmamissa istek islenir ve yeni kayit eklenir.

**Avantajlari:**
- Birden fazla backend instansi arasinda merkezi sinirlandirma saglar.
- Kayan pencere, sabit pencereye kiyasla daha adil bir dagilim sunar.
- Redis TTL ile eski kayitlar otomatik temizlenir.

### Ek Sinirlar

| Parametre | Varsayilan | Aciklama |
|---|---|---|
| `MAX_CONCURRENT_PER_IP` | 3 | Bir IP'nin esanli olarak calistirabileceigi sorgu sayisi |
| `MAX_DEVICES_PER_QUERY` | 5 | Tek sorguda sorgulanabilecek cihaz sayisi |
| `QUERY_TIMEOUT` | 30 sn | Sorgu calistirma zaman asimi |

---

## Dondurulen HTTP Basiklari

Tum API yanitlarinda asagidaki basliklar yer alir:

| Baslik | Aciklama | Ornek |
|---|---|---|
| `X-RateLimit-Limit` | Pencere basina izin verilen toplam istek | `20` |
| `X-RateLimit-Remaining` | Pencere icinde kalan istek hakki | `15` |
| `X-RateLimit-Reset` | Sinirin sifirlanacagi Unix timestamp | `1705312260` |
| `Retry-After` | (yalnizca 429) Beklenmesi gereken sure (saniye) | `42` |

---

## Yapilandirma Ozeti

Tum katmanlarin parametreleri `config/settings.yaml` dosyasinda merkezi olarak tanimlidir:

```yaml
rate_limit:
  frontend:
    max_requests: 10
    window_seconds: 60
    cooldown_seconds: 5
  nginx:
    rate: "30r/m"
    burst: 5
  backend:
    query_limit: 20
    query_window: 60
    general_limit: 60
    general_window: 60
```

Backend parametreleri ayrica ortam degiskenleriyle ezilbilir (`RATE_LIMIT_QUERY`, `RATE_LIMIT_QUERY_WINDOW` vb.).

---

## Sorun Giderme

### "429 Too Many Requests" aliyorum

1. **Hangi katman reddediyor?**
   - Nginx reddediyorsa yanit govdesi Nginx varsayilan HTML sayfasidir.
   - Uygulama reddediyorsa yanit JSON formatindadir ve `X-RateLimit-*` basiklari icerir.

2. **Nginx loglarini kontrol edin:**
   ```bash
   docker compose logs nginx | grep "limiting requests"
   ```

3. **Redis'teki rate limit anahtarlarini kontrol edin:**
   ```bash
   docker compose exec redis redis-cli -a <sifre> KEYS "ratelimit:*"
   ```

4. **Belirli bir IP icin kalan istek hakkini gorun:**
   Yanittaki `X-RateLimit-Remaining` basligini kontrol edin.

### Sinirlar cok kisitlayici

- Nginx sinirlarini `nginx/nginx.conf` dosyasindaki `rate` ve `burst` degerlerini degistirerek ayarlayin.
- Backend sinirlarini `.env` dosyasindaki `RATE_LIMIT_QUERY` ve `RATE_LIMIT_GENERAL` degerlerini degistirerek ayarlayin.
- Frontend sinirlarini `config/settings.yaml` dosyasindaki `rate_limit.frontend` bolumunu degistirerek ayarlayin.
- Degisikliklerden sonra ilgili servisleri yeniden baslatin.

### Redis baglanti hatasi nedeniyle rate limiting calismiyor

Redis erisimezse backend `RateLimitMiddleware` hatayi loglar ve istegi geciren bir fallback davranisi uygulayabilir. Bu durumda Nginx katmani tek koruma noktasi olur. Redis'in calisir durumda oldugunu dogrulayin:

```bash
docker compose exec redis redis-cli -a <sifre> ping
# Beklenen yanit: PONG
```

### Yuk dengeleme ortaminda tutarsiz sinirlar

Birden fazla backend instansi calistiriyorsaniz, tum instanslarin ayni Redis sunucusuna baglandigindna emin olun. Redis merkezi depo gorevi gordugu icin tum instanslardaki sayaclar tutarli olacaktir.
