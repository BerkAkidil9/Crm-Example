# SQLite'tan PostgreSQL'e Geçiş (Veriyi Taşıyarak)

Projeyi online alacağın için veritabanını PostgreSQL'e taşı. Aşağıdaki adımları **sırayla** uygula; özellikle önce SQLite'tan yedek al, sonra PostgreSQL'i aç.

---

## Adım 1: SQLite'tan veri yedeği al (henüz .env'e DB ekleme)

Şu an proje SQLite kullanıyor. **.env dosyasında DB_ENGINE / DB_* satırları yoksa** olduğu gibi devam et. Varsa geçici olarak sil veya # ile yorum yap.

Proje klasöründe:

```powershell
python manage.py dumpdata --natural-foreign --natural-primary -e contenttypes -e auth.Permission -o backup.json
```

Bu komut `backup.json` dosyasını oluşturur. Proje kökünde göreceksin. **Bu dosyayı silme** – veri burada.

---

## Adım 2: PostgreSQL'i kur

- **Windows:** https://www.postgresql.org/download/windows/ veya `winget install PostgreSQL.PostgreSQL`
- Kurulumda **postgres** kullanıcısı için bir şifre belirle; not al.

Kurulum bitince PostgreSQL servisi çalışıyor olmalı.

---

## Adım 3: Veritabanı ve kullanıcı oluştur

- Başlat menüsünden **SQL Shell (psql)** aç veya **pgAdmin** ile Query Tool aç.
- `postgres` kullanıcısı ile bağlanıp şunu çalıştır (şifreyi kendin belirle):

```sql
CREATE USER djcrm_user WITH PASSWORD 'BurayaGucluSifreYaz';
CREATE DATABASE djcrm OWNER djcrm_user;
\q
```

---

## Adım 4: Bağımlılığı yükle

Proje klasöründe:

```powershell
pip install -r requirements.txt
```

---

## Adım 5: .env'e PostgreSQL ayarlarını ekle

`.env` dosyasını aç. **En alta** şunları ekle (kendi şifreni yaz):

```env
DB_ENGINE=django.db.backends.postgresql
DB_NAME=djcrm
DB_USER=djcrm_user
DB_PASSWORD=BurayaGucluSifreYaz
DB_HOST=localhost
DB_PORT=5432
DB_SSL=false
```

Kaydet. Bundan sonra proje PostgreSQL kullanacak.

---

## Adım 6: PostgreSQL'de tabloları oluştur

```powershell
python manage.py migrate
```

Tablolar PostgreSQL'de oluşur (henüz boş).

---

## Adım 7: Yedeği PostgreSQL'e yükle

```powershell
python manage.py loaddata backup.json
```

Eğer "contenttypes" veya sıra ile ilgili hata alırsan, şunu dene:

```powershell
python manage.py loaddata backup.json --ignorenonexistent
```

Veriler PostgreSQL'e geçmiş olur.

---

## Adım 8: Çalıştır ve kontrol et

```powershell
python manage.py runserver
```

Tarayıcıda http://127.0.0.1:8000/ aç; kullanıcılar, lead'ler, ürünler vs. görünüyorsa geçiş tamam.

---

## Özet (sıra önemli)

| Sıra | Ne yapıyorsun |
|------|----------------|
| 1 | SQLite ile `dumpdata` → `backup.json` oluşur |
| 2 | PostgreSQL kur |
| 3 | `djcrm` DB ve `djcrm_user` oluştur |
| 4 | `pip install -r requirements.txt` |
| 5 | `.env`'e DB_* ekle |
| 6 | `python manage.py migrate` |
| 7 | `python manage.py loaddata backup.json` |
| 8 | `runserver` ile test et |

---

## Projeyi online alırken

Sunucuda (Render, Railway, Heroku, VPS vb.) yine **PostgreSQL** kullanacaksın. Orada:

- Hosting'in verdiği **DATABASE_URL** veya **DB_HOST, DB_NAME, DB_USER, DB_PASSWORD** değerlerini alıp `.env` (veya platformun env ayarları) içine yazarsın.
- `DB_HOST` artık localhost değil, sunucunun verdiği adres olur; gerekirse `DB_SSL=true` eklenir.
- Kod tarafında ekstra bir şey yapmana gerek yok; sadece env değişkenlerini production değerleriyle doldurman yeterli.

`backup.json` içinde hassas veri olabilir; production'a **loaddata** ile sadece gerekirse ve güvenli şekilde kullan, dosyayı public repoya koyma.

---

## Production Ayarları (settings.py'de otomatik aktif olur)

`.env` dosyasında `DEBUG=False` yapıldığında aşağıdakiler otomatik aktif olur:

| Ayar | Açıklama |
|------|----------|
| `CONN_MAX_AGE=600` | DB bağlantıları 10 dk açık tutulur (performans) |
| `WhiteNoise` | Static dosyalar uygulama tarafından sunulur (nginx gerekmez) |
| `SECURE_SSL_REDIRECT` | HTTP istekleri HTTPS'e yönlendirilir |
| `SESSION_COOKIE_SECURE` | Cookie'ler sadece HTTPS üzerinden gönderilir |
| `SECURE_HSTS_*` | Tarayıcıya HTTPS zorunluluğu bildirilir |

### Production'da çalıştırma komutu

Development'ta `runserver` yerine, production'da **gunicorn** kullan:

```bash
gunicorn djcrm.wsgi:application --bind 0.0.0.0:8000 --workers 3
```

### Static dosyaları topla

Deployment öncesi static dosyaları topla:

```bash
python manage.py collectstatic --noinput
```

### Production .env örneği

```env
SECRET_KEY=cok-guclu-random-bir-key-buraya
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

DB_ENGINE=django.db.backends.postgresql
DB_NAME=djcrm
DB_USER=djcrm_user
DB_PASSWORD=guclu-sifre
DB_HOST=db-sunucu-adresi
DB_PORT=5432
DB_SSL=true
```
