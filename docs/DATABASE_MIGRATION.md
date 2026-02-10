# Veritabanı: SQLite’dan PostgreSQL’e Geçiş

Bu proje varsayılan olarak SQLite kullanır. Production veya gerçek bir veritabanı için PostgreSQL kullanabilirsiniz.

## 1. PostgreSQL kurulumu

- **Windows:** [PostgreSQL indir](https://www.postgresql.org/download/windows/) veya Chocolatey: `choco install postgresql`
- **macOS:** `brew install postgresql` ve `brew services start postgresql`
- **Linux:** `sudo apt install postgresql postgresql-contrib` (Ubuntu/Debian)

Sunucuda veya Docker ile de çalıştırabilirsiniz.

## 2. Veritabanı ve kullanıcı oluşturma

PostgreSQL’e bağlanıp (ör. `psql -U postgres`):

```sql
CREATE USER djcrm_user WITH PASSWORD 'güçlü_bir_şifre';
CREATE DATABASE djcrm OWNER djcrm_user;
GRANT ALL PRIVILEGES ON DATABASE djcrm TO djcrm_user;
\q
```

## 3. Ortam değişkenleri (.env)

Proje kökünde `.env` dosyası oluşturun (veya `.env.example`’ı kopyalayıp düzenleyin):

```env
DB_ENGINE=django.db.backends.postgresql
DB_NAME=djcrm
DB_USER=djcrm_user
DB_PASSWORD=güçlü_bir_şifre
DB_HOST=localhost
DB_PORT=5432
DB_SSL=false
```

Uzak sunucu kullanıyorsanız `DB_HOST` ve gerekirse `DB_SSL=true` yapın.

## 4. Bağımlılık ve migration

```powershell
pip install -r requirements.txt
python manage.py migrate
```

İlk kez PostgreSQL kullanıyorsanız bu yeterli; tablolar sıfırdan oluşur.

## 5. Mevcut SQLite verisini taşıma (isteğe bağlı)

SQLite’daki veriyi PostgreSQL’e taşımak için:

1. **Yedek al (SQLite ile çalışırken):**
   ```powershell
   # .env'de DB_* değişkenlerini kaldırın veya yorumlayın (SQLite kullanılsın)
   python manage.py dumpdata --natural-foreign --natural-primary -e contenttypes -e auth.Permission -o backup.json
   ```

2. **PostgreSQL’i ayarlayıp migrate et:**
   ```powershell
   # .env'e DB_ENGINE ve DB_* değişkenlerini ekleyin
   python manage.py migrate
   ```

3. **Veriyi yükle:**
   ```powershell
   python manage.py loaddata backup.json
   ```

`dumpdata`/`loaddata` bazen sıra ve foreign key nedeniyle hata verebilir; gerekirse uygulama bazlı (örn. `--exclude auth.Permission`) veya parça parça yedek alıp yükleyebilirsiniz.

## 6. Tekrar SQLite kullanmak

`.env` dosyasındaki `DB_ENGINE` ve diğer `DB_*` satırlarını silin veya yorum satırı yapın. Uygulama tekrar `db.sqlite3` kullanacaktır.
