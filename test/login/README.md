# Login Test Sistemi

Bu klasör login ile ilgili tüm test dosyalarını içerir.

## 📁 Klasör Yapısı

```
test/login/
├── __init__.py
├── README.md
├── test_runner.py
├── working/
│   ├── __init__.py
│   ├── test_login_views.py
│   ├── test_login_forms.py
│   ├── test_login_authentication.py
│   └── test_login_integration.py
└── broken_tests/
    ├── __init__.py
    └── test_login_views.py
```

## 🚀 Test Çalıştırma

### ✅ Çalışan Testler
```bash
# Login view testleri
python manage.py test test.login.working.test_login_views

# Login form testleri
python manage.py test test.login.working.test_login_forms

# Authentication backend testleri
python manage.py test test.login.working.test_login_authentication

# Login entegrasyon testleri
python manage.py test test.login.working.test_login_integration

# Tüm login testleri
python manage.py test test.login.working
```

## 📊 Test Kapsamı

### Views (1 view)
- ✅ CustomLoginView (test edilecek)

### Forms (1 form)
- ✅ CustomAuthenticationForm (test edilecek)

### Authentication Backend (1 backend)
- ✅ EmailOrUsernameModelBackend (test edilecek)

### Integration Tests
- ✅ Complete login flow (test edilecek)
- ✅ Email verification requirement (test edilecek)
- ✅ Redirect behavior (test edilecek)

## 🔧 Test Özellikleri

### Login View Testleri
- GET request testi
- POST request geçerli veri testi
- POST request geçersiz veri testi
- Template kullanımı testi
- Form class testi
- Redirect testi

### Login Form Testleri
- Form başlatma testi
- Geçerli veri testi
- Geçersiz veri testi
- Widget özellikleri testi
- Error mesajları testi

### Authentication Backend Testleri
- Username ile giriş testi
- Email ile giriş testi
- Geçersiz credentials testi
- Email doğrulanmamış kullanıcı testi
- User can authenticate testi

### Integration Testleri
- Tam login akışı testi
- Email doğrulama gereksinimi testi
- Redirect davranışı testi
- Session yönetimi testi

## 📝 Notlar

- Testler Django TestCase kullanır
- Her test bağımsız çalışır
- Test veritabanı otomatik oluşturulur ve silinir
- Mock kullanımı email gönderimi için
- Factory pattern kullanımı test verisi oluşturma için
