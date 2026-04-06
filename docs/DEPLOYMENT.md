# Yayin Alma (Deployment)

Bu belge, Spyglass platformunun uretim ortamina alinma surecini adim adim aciklar.

---

## 1. On Kosullar

| Arac | Minimum Surum | Aciklama |
|---|---|---|
| Docker | 24.0+ | Konteyner calisma zamani |
| Docker Compose | 2.20+ | Coklu konteyner yonetimi |
| Python 3.11+ | (opsiyonel) | `generate_secret.py` betigi icin |

Sunucu gereksinimleri:

- 2+ CPU cekirdegi
- 4 GB+ RAM
- 20 GB+ disk alani
- 80 ve 443 portlarinin dis agdan erisilebilir olmasi

## 2. Ortam Degiskenleri

`.env.example` dosyasini `.env` olarak kopyalayin ve asagidaki degerleri guncelleyin:

```bash
cp .env.example .env
```

Zorunlu degisiklikler:

```ini
# Guclu, rastgele bir deger olusturun
SECRET_KEY=<python3 scripts/generate_secret.py ciktisi>

# PostgreSQL sifresi
DB_PASSWORD=<guclu-sifre>

# Redis sifresi
REDIS_PASSWORD=<guclu-sifre>

# Uretim alan adi
CORS_ORIGINS=["https://lg.example.com"]

# Swagger kapal kalsin
ENABLE_DOCS=false
```

Tum ortam degiskenleri icin bakiniz: [README.md ortam degiskenleri tablosu](../README.md#ortam-degiskenleri)

## 3. SSL Sertifika Kurulumu

Nginx, TLS sertifikalarini `nginx/ssl/` dizininden okur. Iki dosya gereklidir:

```
nginx/ssl/
├── fullchain.pem    # Tam sertifika zinciri
└── privkey.pem      # Ozel anahtar
```

**Let's Encrypt ile:**

```bash
# Certbot ile sertifika alin (DNS dogrulama veya standalone)
certbot certonly --standalone -d lg.example.com

# Sertifikalari kopyalayin
cp /etc/letsencrypt/live/lg.example.com/fullchain.pem nginx/ssl/
cp /etc/letsencrypt/live/lg.example.com/privkey.pem nginx/ssl/
chmod 600 nginx/ssl/privkey.pem
```

**Kurumsal sertifika ile:**

Sertifika saglayicinizdan aldginiz dosyalari ayni isimlerle `nginx/ssl/` altina kopyalayin. Ara sertifikalarin `fullchain.pem` icinde yer aldigindna emin olun.

Sertifika yenileme islemini cron veya systemd timer ile otomatiklestirmeniz onerilir.

## 4. Uretim Yayin Alma Adimlari

### 4.1. Servisleri Ayaga Kaldirma

```bash
# Imajlari derle ve servisleri baslat
docker compose up -d --build
```

Bu komut asagidaki servisleri baslatir:

| Servis | Aciklama | Port |
|---|---|---|
| `nginx` | Ters proxy, TLS sonlandirma, rate limiting | 80, 443 |
| `frontend` | React SPA (statik dosya sunucu) | (ic) |
| `backend` | FastAPI uygulama sunucusu | (ic) |
| `db` | PostgreSQL 15 veritabani | (ic) |
| `redis` | Redis 7 onbellek ve rate limit deposu | (ic) |

Yalnizca Nginx dis aga aciktir. Diger servisler Docker ic agi uzerinden iletisim kurar.

### 4.2. Veritabani Migrasyonu

```bash
docker compose exec backend alembic upgrade head
```

Bu komut Alembic migrasyonlarini uygulayarak veritabani semasini guncel hale getirir.

### 4.3. Dogrulama

```bash
# Saglik kontrolu
curl -s https://lg.example.com/api/v1/health | python3 -m json.tool

# Cihaz listesi
curl -s https://lg.example.com/api/v1/devices | python3 -m json.tool
```

### 4.4. Ornek Veri (Opsiyonel)

```bash
docker compose exec backend python scripts/seed_db.py
```

## 5. Ag Yapisi

```
                  Internet
                     |
               [Firewall :80,:443]
                     |
                  [Nginx]
                 /       \
        frontend ag     backend ag
           |            /    |    \
       [Frontend]  [Backend] [DB] [Redis]
```

- **frontend ag**: Nginx, Frontend ve Backend arasindaki iletisim.
- **backend ag**: Backend, PostgreSQL ve Redis arasindaki iletisim.
- Veritabani ve Redis, frontend agina bagli degildir.

## 6. Izleme ve Loglama

### Konteyner Loglari

```bash
# Tum servislerin loglarini takip et
docker compose logs -f

# Tek bir servisin loglarini gor
docker compose logs -f backend
docker compose logs -f nginx
```

### Nginx Erisim Loglari

Nginx, JSON formatinda yapilandirilmis erisim loglari uretir:

```json
{
  "time": "2025-01-15T10:30:00+03:00",
  "client_ip": "203.0.113.42",
  "method": "POST",
  "uri": "/api/v1/query",
  "status": 200,
  "request_time": 1.234,
  "request_id": "abc123"
}
```

Bu loglar `docker compose logs nginx` ile goruntulenebilir veya bir log toplama aracina (Fluentd, Filebeat, Vector vb.) yonlendirilebilir.

### Saglik Kontrolu

`/api/v1/health` endpointi izleme araclari (Prometheus, Zabbix, Uptime Kuma vb.) icin kullanilabilir. Nginx bu endpointe erisim logu yazmaz (`access_log off`).

## 7. Guncelleme

```bash
# Yeni kodu cekin
git pull origin main

# Imajlari yeniden derleyin ve servisleri yeniden baslatin
docker compose up -d --build

# Varsa yeni migrasyonlari uygulayain
docker compose exec backend alembic upgrade head
```

Sifir kesinti icin once yeni imajlari ayri bir sunucuda derleyip test edebilir, ardindan load balancer arkasinda kademeli gecis yapabilirsiniz.

## 8. Olceklendirme

### Yatay Olceklendirme

- **Backend**: Birden fazla backend konteyner calistirabilirsiniz. Nginx upstream blogu ile yuk dengeleme yapilabilir. Redis tabanli rate limiting sayesinde tum instanslar ayni siniri paylesir.
- **Frontend**: Statik dosya sunucusu oldugu icin CDN arkasina alinabilir.
- **Redis**: Tek instans genellikle yeterlidir. Yuksek trafikte Redis Sentinel veya Cluster kullanilabilir.
- **PostgreSQL**: Okuma agrlikli yukte read replica eklenebilir.

### Dikey Olceklendirme

- Redis icin `maxmemory` degeri docker-compose.yml icinde ayarlanabilir (varsayilan: 256 MB).
- Backend worker sayisi uvicorn yapilandirmasinda arttirilabilir.
- PostgreSQL icin `shared_buffers` ve `work_mem` ayarlari optimize edilebilir.

## 9. Yedekleme

### PostgreSQL Yedegi

```bash
# Manuel yedek
docker compose exec db pg_dump -U spyglass spyglass > backup_$(date +%Y%m%d).sql

# Geri yukleme
cat backup_20250115.sql | docker compose exec -T db psql -U spyglass spyglass
```

Duzensiz otomatik yedekleme icin cron gorevi olusturun.

### Yapilandirma Yedegi

`config/` dizini ve `.env` dosyasi kritik yapilandirma icerir. Bunlari guvenli bir yerde yedekleyin. `.env` dosyasini Git'e eklemeyin.

## 10. Sorun Giderme

| Sorun | Cozum |
|---|---|
| Servisler baslamiyor | `docker compose logs <servis>` ile hata loglarini kontrol edin |
| Veritabani baglanti hatasi | `DB_PASSWORD` degerinin `.env` ve PostgreSQL'de eslestigini dogrulayin |
| Redis baglanti hatasi | `REDIS_PASSWORD` degerinin `.env` ve redis komutunda eslestigini dogrulayin |
| 502 Bad Gateway | Backend'in basladigini dogrulayin: `docker compose ps` |
| SSL hatasi | `nginx/ssl/` altinda `fullchain.pem` ve `privkey.pem` bulundugunu kontrol edin |
| Migrasyon hatasi | `docker compose exec backend alembic history` ile migrasyon gecmisini kontrol edin |
