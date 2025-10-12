# Test Sistemi

Bu klasör tüm modüller için organize edilmiş test dosyalarını içerir.

## 📁 Klasör Yapısı

```
test/
├── __init__.py
├── README.md
├── agents/                     # Agent testleri
├── finance/                    # Finans testleri
├── forget_password/            # Şifre sıfırlama testleri
├── leads/                      # Lead testleri
├── login/                      # Login testleri
│   ├── working/               # ✅ Çalışan testler
│   ├── broken_tests/          # ❌ Çalışmayan testler
│   ├── test_runner.py
│   └── README.md
├── logout/                     # 🆕 Logout testleri
│   ├── working/               # ✅ Çalışan testler (33 test)
│   ├── test_runner.py
│   ├── README.md
│   └── TEST_RESULTS.md
├── orders/                     # Sipariş testleri
├── organisors/                 # Organizatör testleri
├── products_and_stock/         # Ürün ve stok testleri
└── signup/                     # Kayıt testleri
```

## 🚀 Test Çalıştırma

### 🆕 Logout Testleri (YENİ!)
```bash
# Tüm logout testleri (33 test - %100 başarılı!)
python manage.py test test.logout.working

# Logout view testleri
python manage.py test test.logout.working.test_logout_views

# Logout entegrasyon testleri
python manage.py test test.logout.working.test_logout_integration

# İnteraktif test runner
python test/logout/test_runner.py
```

### Login Testleri
```bash
# Tüm login testleri
python manage.py test test.login.working

# Login view testleri
python manage.py test test.login.working.test_login_views

# Login authentication testleri
python manage.py test test.login.working.test_login_authentication
```

### Signup Testleri
```bash
# Tüm signup testleri
python manage.py test test.signup.working
```

### Diğer Modül Testleri
```bash
# Agents testleri
python manage.py test test.agents.working_tests

# Finance testleri
python manage.py test test.finance.working_tests

# Orders testleri
python manage.py test test.orders.working_tests

# Organisors testleri
python manage.py test test.organisors.working_tests

# Products and Stock testleri
python manage.py test test.products_and_stock.working_tests
```

## 📊 Test Durumu

### 🆕 Logout Testleri (YENİ!)
- **Status:** ✅ 33/33 test başarılı (%100)
- **Kapsam:** Views, entegrasyon, güvenlik, performans
- **Süre:** ~19 saniye
- **Dosyalar:** 
  - `test_logout_views.py` (19 test)
  - `test_logout_integration.py` (14 test)

### Login Testleri
- **Status:** ✅ Çalışan testler mevcut
- **Kapsam:** Views, forms, authentication, entegrasyon
- **Dosyalar:** 4 test dosyası

### Signup Testleri
- **Status:** ✅ Çalışan testler mevcut
- **Kapsam:** Views, forms, models, entegrasyon
- **Dosyalar:** 4 test dosyası

### Agents Testleri
- **Status:** ✅ Çalışan testler mevcut
- **Kapsam:** Views, forms, models, mixins, entegrasyon
- **Dosyalar:** 6 test dosyası

### Finance Testleri
- **Status:** ✅ Çalışan testler mevcut
- **Kapsam:** Views, forms, models, entegrasyon
- **Dosyalar:** 4 test dosyası

### Orders Testleri
- **Status:** ✅ Çalışan testler mevcut
- **Kapsam:** Views, forms, models, entegrasyon
- **Dosyalar:** 4 test dosyası

### Organisors Testleri
- **Status:** ✅ Çalışan testler mevcut
- **Kapsam:** Views, forms, models, mixins, entegrasyon
- **Dosyalar:** 5 test dosyası

### Products and Stock Testleri
- **Status:** ⚠️ Kısmi başarılı (working_tests + broken_tests)
- **Çalışan:** 5 test
- **Sorunlu:** 80+ test
- **Sorunlar:** UserProfile unique constraint, form validasyonları

## 🎯 Test Kapsamı Genel

### Authentication & Authorization
- ✅ Login (çoklu test dosyası)
- ✅ **Logout (33 test - YENİ!)**
- ✅ Signup (çoklu test dosyası)
- ✅ Forget Password (test dosyaları)
- ✅ Email Verification (login testlerinde kapsanmış)

### Core Modules
- ✅ Leads (5 test dosyası)
- ✅ Agents (6 test dosyası)
- ✅ Organisors (5 test dosyası)
- ✅ Orders (4 test dosyası)
- ✅ Finance (4 test dosyası)
- ⚠️ Products and Stock (kısmi)

### Test Türleri
- ✅ View testleri
- ✅ Form testleri
- ✅ Model testleri
- ✅ Authentication backend testleri
- ✅ Entegrasyon testleri
- ✅ Güvenlik testleri
- ✅ Performans testleri
- ✅ Mixin testleri

## 🆕 Yenilikler

### Logout Test Sistemi (12 Ekim 2025)
- 🎉 **33 test** başarıyla eklendi
- ✅ %100 test başarı oranı
- 📁 Organize klasör yapısı
- 📖 Detaylı dokümantasyon
- 🏃 İnteraktif test runner
- 🔒 Kapsamlı güvenlik testleri
- ⚡ Performans testleri
- 🔗 Entegrasyon testleri

### Özellikler
- Django LogoutView testi
- Session yönetimi testleri
- CSRF koruması testleri
- Session hijacking koruması
- Session fixation koruması
- Token invalidation testleri
- Çoklu session yönetimi
- Farklı kullanıcı tipleri (organizer, agent, superuser)
- Edge case senaryoları

## 🎯 Gelecek Planları

1. ✅ **Logout testleri eklendi** (TAMAMLANDI!)
2. **Diğer modüller için test genişletmeleri**
3. **Test coverage raporu ekle**
4. **CI/CD entegrasyonu**
5. **Performance benchmark testleri**

## 📝 Notlar

- Testler Django TestCase kullanır
- Her test bağımsız çalışır
- Test veritabanı otomatik oluşturulur ve silinir
- Mock kullanımı email gönderimi için
- Factory pattern kullanımı test verisi oluşturma için