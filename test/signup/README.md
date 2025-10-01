# Signup Test Sistemi

Bu klasör signup (kayıt olma) modülü için organize edilmiş test dosyalarını içerir.

## 📁 Klasör Yapısı

```
test/signup/
├── __init__.py
├── working_tests/              # ✅ Çalışan testler
│   ├── __init__.py
│   ├── test_signup_forms.py    # Form testleri
│   ├── test_signup_views.py    # View testleri
│   ├── test_signup_models.py   # Model testleri
│   └── test_signup_integration.py  # Entegrasyon testleri
├── test_runner.py              # İnteraktif test çalıştırıcı
└── README.md                   # Bu dosya
```

## 🚀 Test Çalıştırma

### ✅ Çalışan Testler

#### Tüm Testleri Çalıştır
```bash
# Tüm signup testlerini çalıştır
python test/signup/test_runner.py all

# Veya Django manage.py ile
python manage.py test test.signup.working_tests
```

#### Belirli Test Kategorilerini Çalıştır
```bash
# Sadece form testleri
python test/signup/test_runner.py forms

# Sadece view testleri  
python test/signup/test_runner.py views

# Sadece model testleri
python manage.py test test.signup.working_tests.test_signup_models

# Sadece entegrasyon testleri
python test/signup/test_runner.py integration
```

#### İnteraktif Test Çalıştırıcı
```bash
python test/signup/test_runner.py interactive
```

#### Django Test Komutları
```bash
# Verbose mod ile
python manage.py test test.signup.working_tests -v 2

# Belirli bir test sınıfını çalıştır
python manage.py test test.signup.working_tests.test_signup_forms.TestCustomUserCreationForm

# Belirli bir test metodunu çalıştır
python manage.py test test.signup.working_tests.test_signup_forms.TestCustomUserCreationForm.test_form_valid_data
```

## 📊 Test Kapsamı

### 🧪 Form Testleri (test_signup_forms.py)
- **Dosya:** `working_tests/test_signup_forms.py`
- **Test Sınıfları:** 3 sınıf
- **Toplam Test:** ~25 test
- **Kapsam:** CustomUserCreationForm, form validasyonları, widget özellikleri

#### Test Edilen Özellikler:
- ✅ Form başlatma ve alan varlığı
- ✅ Geçerli veri ile form testi
- ✅ Zorunlu alanlar validasyonu
- ✅ Email benzersizlik kontrolü
- ✅ Telefon numarası benzersizlik kontrolü
- ✅ Kullanıcı adı benzersizlik kontrolü
- ✅ Şifre validasyonu
- ✅ Widget özellikleri (placeholder, CSS sınıfları)
- ✅ Form save metodu
- ✅ Clean metodları
- ✅ Form entegrasyon testleri

### 🌐 View Testleri (test_signup_views.py)
- **Dosya:** `working_tests/test_signup_views.py`
- **Test Sınıfları:** 6 sınıf
- **Toplam Test:** ~35 test
- **Kapsam:** SignupView, EmailVerificationView, view entegrasyonları

#### Test Edilen Özellikler:
- ✅ SignupView GET/POST istekleri
- ✅ Geçerli veri ile signup
- ✅ Geçersiz veri ile signup
- ✅ Çakışan verilerle signup
- ✅ Email gönderimi (mock)
- ✅ Template kullanımı
- ✅ EmailVerificationSentView
- ✅ EmailVerificationView (başarılı/başarısız)
- ✅ EmailVerificationFailedView
- ✅ Token validasyonu (geçerli/geçersiz/süresi dolmuş/kullanılmış)
- ✅ Tam signup akışı entegrasyonu

### 🗄️ Model Testleri (test_signup_models.py)
- **Dosya:** `working_tests/test_signup_models.py`
- **Test Sınıfları:** 5 sınıf
- **Toplam Test:** ~30 test
- **Kapsam:** User, UserProfile, EmailVerificationToken, Organisor modelleri

#### Test Edilen Özellikler:
- ✅ User modeli oluşturma ve özellikler
- ✅ User benzersizlik kısıtlamaları
- ✅ UserProfile modeli ve ilişkileri
- ✅ EmailVerificationToken modeli
- ✅ Token süre kontrolü (24 saat)
- ✅ Organisor modeli ve ilişkileri
- ✅ Model cascade delete işlemleri
- ✅ Model veri bütünlüğü
- ✅ Model validasyonları

### 🔗 Entegrasyon Testleri (test_signup_integration.py)
- **Dosya:** `working_tests/test_signup_integration.py`
- **Test Sınıfları:** 6 sınıf
- **Toplam Test:** ~20 test
- **Kapsam:** Tam signup akışı, model ilişkileri, form-view entegrasyonu

#### Test Edilen Özellikler:
- ✅ Tam signup ve doğrulama akışı
- ✅ Geçersiz verilerle signup akışı
- ✅ Çakışan verilerle signup akışı
- ✅ Email doğrulama akışları (başarılı/başarısız)
- ✅ Model ilişkileri ve cascade işlemler
- ✅ Form ve view entegrasyonu
- ✅ Veri tutarlılığı kontrolü

## 📈 Test İstatistikleri

### ✅ Toplam Test Sayısı: ~110 test
- **Form Testleri:** ~25 test
- **View Testleri:** ~35 test  
- **Model Testleri:** ~30 test
- **Entegrasyon Testleri:** ~20 test

### 🎯 Test Kapsamı
- **Modeller:** User, UserProfile, EmailVerificationToken, Organisor
- **Viewlar:** SignupView, EmailVerificationView, EmailVerificationSentView, EmailVerificationFailedView
- **Formlar:** CustomUserCreationForm
- **URL'ler:** signup, verify-email, verify-email-sent, verify-email-failed
- **Template'ler:** signup.html, verify_email_sent.html, verify_email_failed.html

## 🔧 Test Özellikleri

### Mock Kullanımı
- Email gönderimi için `unittest.mock.patch` kullanılır
- Gerçek email gönderimi yapılmaz, sadece mock kontrol edilir

### Test Verisi
- Her test benzersiz kullanıcı adları kullanır
- Test verileri gerçekçi ve geçerli formatta
- Test sonrası temizlik otomatik yapılır

### Hata Senaryoları
- Geçersiz email formatları
- Çakışan kullanıcı adları/emailler
- Şifre uyumsuzlukları
- Eksik zorunlu alanlar
- Süresi dolmuş/kullanılmış tokenlar

## 🎯 Test Edilen Signup Akışı

1. **Signup Sayfası** → Form gösterimi
2. **Form Gönderimi** → Veri validasyonu
3. **Kullanıcı Oluşturma** → User, UserProfile, Organisor oluşturma
4. **Email Token** → EmailVerificationToken oluşturma
5. **Email Gönderimi** → Doğrulama linki gönderimi
6. **Email Doğrulama** → Token ile email doğrulama
7. **Login Yönlendirme** → Başarılı doğrulama sonrası

## 🚨 Dikkat Edilecek Noktalar

### Test Çalıştırma
- Django ayarları doğru yüklenmeli
- Test veritabanı kullanılır (gerçek veri etkilenmez)
- Mock kullanımı email testlerinde önemli

### Test Verileri
- Her test benzersiz kullanıcı adları kullanır
- Telefon numaraları ve email adresleri de benzersiz olmalı
- Test sonrası temizlik Django tarafından otomatik yapılır

### Mock Kullanımı
- Email gönderimi testlerinde `@patch('leads.views.send_mail')` kullanılır
- Mock'un çağrıldığı ve doğru parametrelerle çağrıldığı kontrol edilir

## 📝 Test Geliştirme

### Yeni Test Ekleme
1. Uygun test dosyasını seç (forms/views/models/integration)
2. Mevcut test sınıfına yeni metod ekle veya yeni sınıf oluştur
3. Test metodunu `test_` ile başlat
4. Assertion'ları ekle
5. Test'i çalıştır ve doğrula

### Test Best Practices
- Her test bağımsız olmalı
- Test verileri gerçekçi olmalı
- Mock kullanımı gerekli yerlerde yapılmalı
- Hata senaryoları da test edilmeli
- Test isimleri açıklayıcı olmalı

## 🔍 Sorun Giderme

### Yaygın Hatalar
1. **UserProfile unique constraint hatası:** Benzersiz kullanıcı adları kullanın
2. **Email gönderimi hatası:** Mock kullanımını kontrol edin
3. **Token süresi hatası:** Test verilerini güncelleyin
4. **Form validasyon hatası:** Test verilerini kontrol edin

### Debug İpuçları
- `-v 2` parametresi ile verbose çıktı alın
- Belirli testleri tek tek çalıştırın
- Test verilerini kontrol edin
- Mock kullanımını doğrulayın

## 📚 Kaynaklar

- [Django Testing Documentation](https://docs.djangoproject.com/en/stable/topics/testing/)
- [Python unittest Documentation](https://docs.python.org/3/library/unittest.html)
- [Django TestCase Documentation](https://docs.djangoproject.com/en/stable/topics/testing/tools/#django.test.TestCase)
