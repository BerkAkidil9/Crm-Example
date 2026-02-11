# Profil Fotoğrafları ve Medya Dosyaları (Production)

## Neden online'da fotoğraflar görünmüyor?

Projeyi Render (veya benzeri bir PaaS) üzerinde çalıştırdığınızda:

1. **Geçici dosya sistemi**: Sunucunun diski **ephemeral**'dır. Yüklenen dosyalar `media/` klasörüne yazılır ama uygulama yeniden deploy edildiğinde veya container yeniden başlatıldığında bu disk sıfırlanır; tüm yüklenen fotoğraflar silinir.
2. **Veritabanı vs dosya**: Veritabanında profil fotoğrafı yolu (örn. `profile_images/abc.jpg`) kayıtlı kalır ama dosya sunucuda artık yoktur. Bu yüzden sayfada resim isteği 404 döner ve kırık resim/boş alan görünür.

Yerelde çalışmasının sebebi: `media/` klasörü bilgisayarınızda kalıcıdır; deploy olmadığı için dosyalar silinmez.

## Yapılan iyileştirme (şablon fallback)

Organisor, agent ve lead listesi/detay şablonlarına **resim yüklenemezse** (404 vb.) otomatik olarak varsayılan avatar ikonu gösteren bir fallback eklendi. Böylece sunucuda dosya olmasa bile sayfa kırık resim göstermez; yuvarlak placeholder ikon görünür.

## Kalıcı çözüm: Bulut depolama

Profil fotoğraflarının production'da kalıcı olması için yüklenen dosyaları **bulut depolamaya** (AWS S3, Cloudinary, Backblaze B2 vb.) yönlendirmeniz gerekir.

### Örnek: Django + AWS S3

1. `django-storages` ve `boto3` kurun:
   ```bash
   pip install django-storages boto3
   ```

2. `settings.py` içinde production için:
   ```python
   # Production: use S3 for media files
   if not DEBUG:
       DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
       AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
       AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
       AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')
       AWS_S3_REGION_NAME = os.getenv('AWS_S3_REGION_NAME', 'eu-central-1')
       AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
       MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'
   ```

3. Render (veya hosting) ortam değişkenlerine `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_STORAGE_BUCKET_NAME` ekleyin. S3 bucket CORS ve public read (veya signed URL) ayarlarını yapın.

Böylece yeni yüklenen tüm profil/lead fotoğrafları S3’e gider ve deploy sonrası da kalıcı olur.

### Alternatif: Cloudinary

Cloudinary da `django-storages` ile kullanılabilir; ücretsiz kotası uygun olabilir. Dokümantasyon: [Cloudinary + Django](https://cloudinary.com/documentation/django_integration).
