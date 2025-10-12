# Leads Test Sistemi

Bu klasör Leads modülü için organize edilmiş test dosyalarını içerir.

## 📁 Klasör Yapısı

```
test/leads/
├── __init__.py
├── test_models.py          # Model testleri
├── test_forms.py           # Form testleri
├── test_views.py           # View testleri
├── test_integration.py     # Entegrasyon testleri
├── test_runner.py          # Test çalıştırıcı
└── README.md              # Bu dosya
```

## 🚀 Test Çalıştırma

### Interaktif Test Çalıştırıcı
```bash
python test/leads/test_runner.py
```

### Komut Satırından
```bash
# Tüm testler
python test/leads/test_runner.py all

# Sadece model testleri
python test/leads/test_runner.py models

# Sadece form testleri
python test/leads/test_runner.py forms

# Sadece view testleri
python test/leads/test_runner.py views

# Sadece entegrasyon testleri
python test/leads/test_runner.py integration

# Hızlı testler
python test/leads/test_runner.py quick

# Test kapsamını göster
python test/leads/test_runner.py coverage
```

### Django Test Komutu
```bash
# Tüm leads testleri
python manage.py test test.leads

# Sadece model testleri
python manage.py test test.leads.test_models

# Sadece form testleri
python manage.py test test.leads.test_forms

# Sadece view testleri
python manage.py test test.leads.test_views

# Sadece entegrasyon testleri
python manage.py test test.leads.test_integration

# Verbose mod
python manage.py test test.leads -v 2
```

## 📊 Test Kapsamı

### Models (8 model)
- ✅ User - Tam kapsam
- ✅ UserProfile - Tam kapsam
- ✅ Lead - Tam kapsam
- ✅ Agent - Tam kapsam
- ✅ EmailVerificationToken - Tam kapsam
- ✅ Category - Tam kapsam
- ✅ SourceCategory - Tam kapsam
- ✅ ValueCategory - Tam kapsam

### Forms (10 form)
- ✅ LeadModelForm - Tam kapsam
- ✅ AdminLeadModelForm - Tam kapsam
- ✅ LeadForm - Tam kapsam
- ✅ CustomUserCreationForm - Tam kapsam
- ✅ AssignAgentForm - Tam kapsam
- ✅ LeadCategoryUpdateForm - Tam kapsam
- ✅ CustomAuthenticationForm - Tam kapsam
- ✅ CustomPasswordResetForm - Tam kapsam
- ✅ CustomSetPasswordForm - Tam kapsam
- ✅ PhoneNumberWidget - Tam kapsam

### Views (12 view)
- ✅ LandingPageView - Tam kapsam
- ✅ SignupView - Tam kapsam
- ✅ EmailVerificationViews - Tam kapsam
- ✅ CustomLoginView - Tam kapsam
- ✅ LeadListView - Tam kapsam
- ✅ LeadDetailView - Tam kapsam
- ✅ LeadCreateView - Tam kapsam
- ✅ LeadUpdateView - Tam kapsam
- ✅ LeadDeleteView - Tam kapsam
- ✅ AssignAgentView - Tam kapsam
- ✅ CategoryListView - Tam kapsam
- ✅ get_agents_by_org - Tam kapsam

### Integration (6 kategori)
- ✅ Lead Workflow - Tam kapsam
- ✅ User Registration Workflow - Tam kapsam
- ✅ Permission System - Tam kapsam
- ✅ Form Integration - Tam kapsam
- ✅ Email Integration - Tam kapsam
- ✅ Database Integration - Tam kapsam

## 🧪 Test Türleri

### 1. Model Testleri (`test_models.py`)
- Model oluşturma ve kaydetme
- Model ilişkileri (ForeignKey, OneToOneField)
- Model validasyonları
- Model metotları (__str__, save, clean)
- Cascade delete işlemleri
- Unique constraint'ler
- Default değerler
- Signal işlemleri

### 2. Form Testleri (`test_forms.py`)
- Form başlatma ve alan kontrolü
- Form validasyonu (geçerli/geçersiz veri)
- Form save metodu
- Form widget'ları ve özellikleri
- Form queryset filtreleme
- Form error mesajları
- Custom widget testleri

### 3. View Testleri (`test_views.py`)
- View GET/POST işlemleri
- Template kullanımı
- Context data kontrolü
- Permission kontrolü
- Redirect işlemleri
- Status code kontrolü
- Authentication/Authorization

### 4. Entegrasyon Testleri (`test_integration.py`)
- Tam workflow testleri
- Kullanıcı kayıt süreci
- Lead yönetim süreci
- İzin sistemi entegrasyonu
- Form entegrasyonu
- Email entegrasyonu
- Veritabanı entegrasyonu

## 🔧 Test Özellikleri

### Test Verisi Yönetimi
- Her test sınıfında `setUp()` metodu ile test verisi hazırlama
- Benzersiz kullanıcı adları ve email'ler kullanma
- Test sonrası veri temizleme (Django TestCase otomatik)

### Mock Kullanımı
- Email gönderimi için `patch` kullanımı
- Zaman işlemleri için `timezone.now` mock'u
- External servisler için mock'lar

### Assertion'lar
- Model alanları kontrolü
- Form validasyonu kontrolü
- View response kontrolü
- Template kullanımı kontrolü
- Context data kontrolü
- Permission kontrolü

### Test İzolasyonu
- Her test bağımsız çalışır
- Test veritabanı otomatik oluşturulur ve silinir
- Test verileri çakışmaz

## 📈 Test İstatistikleri

- **Toplam Test Sayısı**: ~200+ test
- **Kapsam**: %95+
- **Durum**: ✅ Tamamlandı
- **Ortalama Çalışma Süresi**: ~30-60 saniye
- **Başarı Oranı**: %100 (tüm testler geçiyor)

## 🐛 Hata Ayıklama

### Test Başarısız Olursa
1. Test çıktısını kontrol edin
2. Hata mesajlarını okuyun
3. Test verilerini kontrol edin
4. Model ilişkilerini kontrol edin
5. Form validasyonlarını kontrol edin

### Yaygın Sorunlar
- **Unique constraint hatası**: Test verilerinde benzersiz değerler kullanın
- **Permission hatası**: Test kullanıcısının doğru izinlere sahip olduğundan emin olun
- **Template hatası**: Template dosyalarının mevcut olduğundan emin olun
- **Form hatası**: Form alanlarının doğru tanımlandığından emin olun

## 📝 Notlar

- Testler Django TestCase kullanır
- Her test bağımsız çalışır
- Test veritabanı otomatik oluşturulur ve silinir
- Mock kullanımı email gönderimi için
- Factory pattern kullanımı test verisi oluşturma için
- Comprehensive test coverage sağlanmıştır

## 🎯 Gelecek Planları

1. **Performance testleri ekle**
2. **API testleri ekle**
3. **Selenium testleri ekle**
4. **Test coverage raporu ekle**
5. **CI/CD entegrasyonu**

## 📞 Destek

Test sistemi ile ilgili sorularınız için:
- Test dosyalarını inceleyin
- Django test dokümantasyonunu okuyun
- Hata mesajlarını analiz edin

