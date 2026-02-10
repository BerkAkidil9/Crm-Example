# Adım Adım: Veritabanı ve .env Kullanımı

## Seçenek A: SQLite ile devam (şu anki gibi, ekstra bir şey yapma)

1. **`.env` dosyan zaten var** – Email, SECRET_KEY vs. dolu.
2. **DB ile ilgili hiçbir şey yazma** – Proje otomatik `db.sqlite3` kullanır.
3. Projeyi her zamanki gibi çalıştır:  
   `python manage.py runserver`

Bu kadar. Başka bir adım yok.

---

## Seçenek B: PostgreSQL kullanmak istiyorsan

### Adım 1: PostgreSQL’i kur
- Windows: https://www.postgresql.org/download/windows/  
  veya: `winget install PostgreSQL.PostgreSQL`
- Kurulumda bir **postgres kullanıcı şifresi** belirle (not al).

### Adım 2: Veritabanı ve kullanıcı oluştur
- **pgAdmin** (PostgreSQL ile gelir) veya komut satırından:
  - Başlat menüsünden **SQL Shell (psql)** aç veya pgAdmin’de Query Tool aç.
- Şunu çalıştır (şifreyi kendin belirle):

```sql
CREATE USER djcrm_user WITH PASSWORD 'GucluSifre123';
CREATE DATABASE djcrm OWNER djcrm_user;
\q
```

### Adım 3: Proje bağımlılığını yükle
Proje klasöründe PowerShell/Terminal:

```powershell
pip install -r requirements.txt
```

### Adım 4: `.env` dosyasına PostgreSQL ayarlarını ekle
`.env` dosyasını aç. **En alta** şunları ekle (kendi şifreni yaz):

```env
DB_ENGINE=django.db.backends.postgresql
DB_NAME=djcrm
DB_USER=djcrm_user
DB_PASSWORD=GucluSifre123
DB_HOST=localhost
DB_PORT=5432
DB_SSL=false
```

Kaydet.

### Adım 5: Migration çalıştır
Aynı klasörde:

```powershell
python manage.py migrate
```

Tablolar PostgreSQL’de oluşur.

### Adım 6: (İsteğe bağlı) Eski SQLite verisini taşımak
Eski `db.sqlite3` içindeki veriyi taşımak istiyorsan:

1. **Önce** `.env` içindeki tüm `DB_*` satırlarını **sil veya # ile yorum yap** (geçici olarak SQLite’a dön).
2. Yedek al:
   ```powershell
   python manage.py dumpdata --natural-foreign --natural-primary -e contenttypes -e auth.Permission -o backup.json
   ```
3. **Sonra** `.env`’e `DB_*` satırlarını **tekrar ekle** (PostgreSQL’e dön).
4. Migration zaten yapıldıysa sadece veriyi yükle:
   ```powershell
   python manage.py loaddata backup.json
   ```

### Adım 7: Sunucuyu çalıştır
```powershell
python manage.py runserver
```

Tarayıcıda http://127.0.0.1:8000/ – artık PostgreSQL kullanıyorsun.

---

## Özet tablo

| Ne yapıyorsun?        | Yapman gereken |
|-----------------------|----------------|
| SQLite ile devam      | Hiçbir şey; projeyi çalıştır. |
| PostgreSQL’e geç      | 1) PostgreSQL kur → 2) DB + kullanıcı oluştur → 3) `pip install -r requirements.txt` → 4) `.env`’e DB_* ekle → 5) `migrate` → 6) İstersen veri taşı → 7) `runserver` |

## Not
- **`.env`** dosyasını asla GitHub’a atma (zaten .gitignore’da).
- **`.env.example`** repoda kalsın; içinde gerçek şifre olmasın.
