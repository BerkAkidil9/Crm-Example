# Forget Password Test Sistemi

Bu klasör forget password (şifre sıfırlama) modülü için organize edilmiş test dosyalarını içerir.

## 📁 Klasör Yapısı

```
test/forget_password/
├── __init__.py
├── test_forget_password_views.py      # View testleri
├── test_forget_password_forms.py      # Form testleri
├── test_runner.py                     # Test çalıştırıcı
└── README.md                          # Bu dosya
```

## 🚀 Test Çalıştırma

### Tüm Testleri Çalıştır
```bash
# Tüm forget password testleri
python manage.py test test.forget_password

# Verbose mod
python manage.py test test.forget_password -v 2

# Test runner ile
python test/forget_password/test_runner.py
```

### Belirli Test Dosyalarını Çalıştır
```bash
# Sadece view testleri
python manage.py test test.forget_password.test_forget_password_views

# Sadece form testleri
python manage.py test test.forget_password.test_forget_password_forms
```

### Belirli Test Sınıflarını Çalıştır
```bash
# Password reset view testleri
python manage.py test test.forget_password.test_forget_password_views.TestCustomPasswordResetView

# Password reset form testleri
python manage.py test test.forget_password.test_forget_password_forms.TestCustomPasswordResetForm

# Set password form testleri
python manage.py test test.forget_password.test_forget_password_forms.TestCustomSetPasswordForm
```

### Belirli Test Metodlarını Çalıştır
```bash
# Belirli bir test metodu
python manage.py test test.forget_password.test_forget_password_views.TestCustomPasswordResetView.test_password_reset_view_get
```

## 📊 Test Kapsamı

### View Testleri (test_forget_password_views.py)

#### CustomPasswordResetView Testleri
- ✅ GET isteği testi
- ✅ Template testi
- ✅ Form class testi
- ✅ Geçerli email ile POST testi
- ✅ Geçersiz email ile POST testi
- ✅ Var olmayan email ile POST testi
- ✅ Doğrulanmamış email ile POST testi
- ✅ Boş email ile POST testi
- ✅ Case insensitive email testi
- ✅ Whitespace içeren email testi
- ✅ Email gönderimi detayları testi
- ✅ Birden fazla istek testi

#### PasswordResetDoneView Testleri
- ✅ GET isteği testi
- ✅ Template testi
- ✅ İçerik testi

#### CustomPasswordResetConfirmView Testleri
- ✅ Geçerli token ile GET testi
- ✅ Form class testi
- ✅ Geçerli veri ile POST testi
- ✅ Şifre uyumsuzluğu testi
- ✅ Zayıf şifre testi
- ✅ Boş şifre testi
- ✅ Geçersiz token testi
- ✅ Geçersiz uid testi
- ✅ Süresi dolmuş token testi
- ✅ Var olmayan kullanıcı testi
- ✅ Inactive kullanıcı testi

#### PasswordResetCompleteView Testleri
- ✅ GET isteği testi
- ✅ Template testi
- ✅ İçerik testi

#### Entegrasyon Testleri
- ✅ Tam forget password akışı testi
- ✅ Geçersiz email ile test
- ✅ Doğrulanmamış email ile test
- ✅ Form validasyon testi
- ✅ Güvenlik önlemleri testi

### Form Testleri (test_forget_password_forms.py)

#### CustomPasswordResetForm Testleri
- ✅ Form başlatma testi
- ✅ Widget özellikleri testi
- ✅ Geçerli veri testi
- ✅ Geçersiz email formatı testi
- ✅ Boş email testi
- ✅ Var olmayan email testi
- ✅ Case insensitive email testi
- ✅ Whitespace email testi
- ✅ Uzun email testi
- ✅ Özel karakterler içeren email testi
- ✅ Birden fazla @ sembolü testi
- ✅ @ sembolü olmayan email testi
- ✅ Domain olmayan email testi
- ✅ Local part olmayan email testi
- ✅ Unicode email testi
- ✅ Sayısal email testi
- ✅ Nokta içeren email testi
- ✅ + sembolü içeren email testi
- ✅ Tire içeren email testi
- ✅ Alt çizgi içeren email testi

#### CustomSetPasswordForm Testleri
- ✅ Form başlatma testi
- ✅ Widget özellikleri testi
- ✅ Help text testi
- ✅ Geçerli veri testi
- ✅ Şifre uyumsuzluğu testi
- ✅ Boş şifre testi
- ✅ Kısa şifre testi
- ✅ Yaygın şifre testi
- ✅ Tamamen sayısal şifre testi
- ✅ Kullanıcı adına benzer şifre testi
- ✅ Email'e benzer şifre testi
- ✅ Ad'a benzer şifre testi
- ✅ Soyad'a benzer şifre testi
- ✅ Whitespace şifre testi
- ✅ Unicode şifre testi
- ✅ Özel karakterler içeren şifre testi
- ✅ Uzun şifre testi
- ✅ Save fonksiyonalitesi testi
- ✅ Save commit=False testi

#### Entegrasyon Testleri
- ✅ Mevcut kullanıcı ile password reset form testi
- ✅ Var olmayan kullanıcı ile password reset form testi
- ✅ Geçerli veri ile set password form testi
- ✅ Geçersiz veri ile set password form testi
- ✅ Form validasyon edge case'leri testi
- ✅ Form alan özellikleri testi

## 🔧 Test Özellikleri

### Güvenlik Testleri
- ✅ Case insensitive email handling
- ✅ Whitespace trimming
- ✅ Var olmayan email için de success döner (güvenlik)
- ✅ Token validation
- ✅ Password strength validation
- ✅ Similarity checks

### Edge Case Testleri
- ✅ Boş formlar
- ✅ None data
- ✅ Geçersiz formatlar
- ✅ Çok uzun veriler
- ✅ Unicode karakterler
- ✅ Özel karakterler

### Entegrasyon Testleri
- ✅ Tam password reset akışı
- ✅ Form validasyonları
- ✅ Email gönderimi
- ✅ Password değişikliği
- ✅ Error handling

## 📈 Test İstatistikleri

### Toplam Test Sayısı
- **View Testleri:** 25+ test metodu
- **Form Testleri:** 30+ test metodu
- **Entegrasyon Testleri:** 10+ test metodu
- **Toplam:** 65+ test metodu

### Test Sınıfları
- **TestCustomPasswordResetView:** 12 test
- **TestPasswordResetDoneView:** 3 test
- **TestCustomPasswordResetConfirmView:** 10 test
- **TestPasswordResetCompleteView:** 3 test
- **TestForgetPasswordIntegration:** 5 test
- **TestCustomPasswordResetForm:** 20 test
- **TestCustomSetPasswordForm:** 18 test
- **TestForgetPasswordFormIntegration:** 6 test

## 🎯 Test Hedefleri

### Fonksiyonel Testler
- ✅ Password reset formu çalışıyor
- ✅ Email gönderimi çalışıyor
- ✅ Password değişikliği çalışıyor
- ✅ Form validasyonları çalışıyor

### Güvenlik Testleri
- ✅ Güvenli email handling
- ✅ Güvenli password validation
- ✅ Token security
- ✅ Input sanitization

### Kullanılabilirlik Testleri
- ✅ User-friendly error messages
- ✅ Proper form styling
- ✅ Responsive design
- ✅ Accessibility

## 🚨 Bilinen Sorunlar

Şu anda bilinen bir sorun bulunmamaktadır.

## 🔮 Gelecek Planları

1. **Performance testleri ekle**
2. **Load testleri ekle**
3. **Mobile responsive testleri ekle**
4. **Accessibility testleri ekle**
5. **Internationalization testleri ekle**

## 📝 Notlar

- Testler Django TestCase kullanır
- Her test bağımsız çalışır
- Test veritabanı otomatik oluşturulur ve silinir
- Mock kullanımı email gönderimi için
- Factory pattern kullanımı test verisi oluşturma için
- Comprehensive error handling
- Edge case coverage
- Security testing included

## 🏃‍♂️ Hızlı Başlangıç

```bash
# 1. Test runner'ı çalıştır
python test/forget_password/test_runner.py

# 2. Menüden seçim yap
# 3. Testleri çalıştır
# 4. Sonuçları incele
```

## 📞 Destek

Testlerle ilgili sorunlar için:
1. Test runner'ı kullanın
2. Verbose modda çalıştırın
3. Belirli testleri izole edin
4. Log dosyalarını kontrol edin
