# Organisors Test Sistemi

Bu klasör organisors modülü için organize edilmiş test dosyalarını içerir.

## 📁 Klasör Yapısı

```
test/organisors/
├── __init__.py
├── working_tests/          # ✅ Çalışan testler
│   ├── __init__.py
│   ├── test_models.py      # Model testleri
│   ├── test_forms.py       # Form testleri
│   ├── test_views.py       # View testleri
│   ├── test_mixins.py      # Mixin testleri
│   └── test_integration.py # Entegrasyon testleri
├── test_runner.py          # İnteraktif test çalıştırıcı
└── README.md
```

## 🚀 Test Çalıştırma

### ✅ Tüm Testleri Çalıştır
```bash
# İnteraktif menü ile
python test/organisors/test_runner.py

# Doğrudan tüm testleri çalıştır
python test/organisors/test_runner.py all

# Django test komutu ile
python manage.py test test.organisors.working_tests
```

### 📋 Belirli Test Kategorilerini Çalıştır
```bash
# Model testleri
python test/organisors/test_runner.py models
python manage.py test test.organisors.working_tests.test_models

# Form testleri
python test/organisors/test_runner.py forms
python manage.py test test.organisors.working_tests.test_forms

# View testleri
python test/organisors/test_runner.py views
python manage.py test test.organisors.working_tests.test_views

# Mixin testleri
python test/organisors/test_runner.py mixins
python manage.py test test.organisors.working_tests.test_mixins

# Entegrasyon testleri
python test/organisors/test_runner.py integration
python manage.py test test.organisors.working_tests.test_integration
```

## 📊 Test Kapsamı

### Models (1 model)
- ✅ Organisor (çalışıyor)
  - Model oluşturma
  - String representation
  - İlişkiler (User, UserProfile)
  - Cascade silme
  - Unique constraints
  - Meta seçenekleri

### Views (5 view)
- ✅ OrganisorListView (çalışıyor)
- ✅ OrganisorCreateView (çalışıyor)
- ✅ OrganisorDetailView (çalışıyor)
- ✅ OrganisorUpdateView (çalışıyor)
- ✅ OrganisorDeleteView (çalışıyor)

### Forms (2 form)
- ✅ OrganisorModelForm (çalışıyor)
- ✅ OrganisorCreateForm (çalışıyor)

### Mixins (3 mixin)
- ✅ AdminOnlyMixin (çalışıyor)
- ✅ OrganisorAndAdminMixin (çalışıyor)
- ✅ SelfProfileOnlyMixin (çalışıyor)

### Integration Tests
- ✅ Tam organisor yaşam döngüsü
- ✅ İzin sistemi
- ✅ Form validasyonu
- ✅ Model ilişkileri
- ✅ Email doğrulama
- ✅ Toplu işlemler
- ✅ Hata yönetimi

## 🎯 Test Özellikleri

### Model Testleri
- **Organisor Model**: Temel CRUD işlemleri, ilişkiler, kısıtlamalar
- **İlişki Testleri**: User-Organisor, Organisation-Organisor
- **Cascade Silme**: User/Organisation silinince Organisor da silinir
- **Unique Constraints**: OneToOneField kısıtlamaları
- **Edge Cases**: Sınır durumları ve hata senaryoları

### Form Testleri
- **OrganisorModelForm**: Güncelleme formu validasyonları
- **OrganisorCreateForm**: Oluşturma formu validasyonları
- **Field Validation**: Email, username, phone number benzersizlik
- **Password Validation**: Şifre eşleşme ve güvenlik kuralları
- **Widget Attributes**: CSS sınıfları ve placeholder'lar
- **Clean Methods**: Özel validasyon metodları

### View Testleri
- **Permission System**: Admin, Organisor, Agent erişim kontrolleri
- **CRUD Operations**: Create, Read, Update, Delete işlemleri
- **Template Rendering**: Doğru template'lerin kullanılması
- **Form Handling**: GET/POST istekleri ve validasyon
- **Redirect Logic**: Başarılı işlemler sonrası yönlendirmeler
- **Error Handling**: 404, 403 hataları ve form hataları

### Mixin Testleri
- **AdminOnlyMixin**: Sadece admin kullanıcıları erişebilir
- **OrganisorAndAdminMixin**: Admin ve organisor kullanıcıları erişebilir
- **SelfProfileOnlyMixin**: Kullanıcılar sadece kendi profillerini erişebilir
- **Permission Hierarchy**: Admin > Organisor > Agent > Anonymous
- **Edge Cases**: Var olmayan kayıtlar, yetkisiz erişim

### Entegrasyon Testleri
- **Complete Lifecycle**: Tam organisor yaşam döngüsü
- **Permission Integration**: Tüm view'ların izin sistemi
- **Form Integration**: Form validasyonu ve hata yönetimi
- **Model Integration**: Model ilişkileri ve cascade işlemler
- **Email Integration**: Email doğrulama ve gönderimi
- **Bulk Operations**: Toplu oluşturma ve silme işlemleri

## 🔧 Test Verileri

### Kullanıcı Tipleri
- **Admin User**: ID=1 veya username='berk' (tüm işlemler)
- **Organisor User**: is_organisor=True (sınırlı işlemler)
- **Agent User**: is_agent=True (hiçbir işlem)
- **Anonymous User**: Giriş yapmamış (redirect)

### Test Verileri
- **Benzersiz Kullanıcılar**: Her test için unique username/email
- **Gerçekçi Veriler**: Türk telefon numaraları, tarihler
- **Edge Cases**: Geçersiz veriler, sınır durumları
- **Mock Objects**: Email gönderimi için mock kullanımı

## 📈 Test Metrikleri

### Test Sayıları
- **Model Tests**: ~20 test
- **Form Tests**: ~30 test
- **View Tests**: ~50 test
- **Mixin Tests**: ~25 test
- **Integration Tests**: ~15 test
- **Toplam**: ~140 test

### Test Kategorileri
- **Unit Tests**: Bireysel bileşen testleri
- **Integration Tests**: Bileşenler arası etkileşim
- **Permission Tests**: Yetki ve erişim kontrolleri
- **Validation Tests**: Form ve model validasyonları
- **Error Handling Tests**: Hata senaryoları

## 🎨 Test Stili

### Naming Convention
- **Test Classes**: `Test[ComponentName][TestType]`
- **Test Methods**: `test_[specific_functionality]`
- **Setup Methods**: `setUp()` - test verilerini hazırlar
- **Helper Methods**: `_helper_method_name()`

### Test Structure
```python
class TestComponentName(TestCase):
    def setUp(self):
        """Test verilerini hazırla"""
        # Test verileri oluştur
    
    def test_specific_functionality(self):
        """Spesifik işlevsellik testi"""
        # Test adımları
        # Assertion'lar
```

### Assertion Patterns
- **Status Codes**: `self.assertEqual(response.status_code, 200)`
- **Redirects**: `self.assertRedirects(response, expected_url)`
- **Template Usage**: `self.assertTemplateUsed(response, 'template.html')`
- **Content**: `self.assertContains(response, 'expected_text')`
- **Database**: `self.assertTrue(Model.objects.filter(...).exists())`

## 🚨 Hata Yönetimi

### Test Hataları
- **Import Errors**: Django setup ve model import'ları
- **Database Errors**: Test veritabanı oluşturma
- **Permission Errors**: Yetki kontrolleri
- **Validation Errors**: Form ve model validasyonları

### Debug Bilgileri
- **Verbose Output**: `-v 2` ile detaylı çıktı
- **Error Messages**: Hata mesajları ve stack trace
- **Test Names**: Hangi testin başarısız olduğu
- **Assertion Details**: Beklenen vs gerçek değerler

## 📝 Notlar

- Testler Django TestCase kullanır
- Her test bağımsız çalışır
- Test veritabanı otomatik oluşturulur ve silinir
- Mock kullanımı email gönderimi için
- Factory pattern kullanımı test verisi oluşturma için
- CSRF token'lar test ortamında otomatik işlenir

## 🔄 Güncelleme Notları

### v1.0.0 (İlk Sürüm)
- Temel model, form, view testleri
- Mixin testleri
- Entegrasyon testleri
- Test runner ve dokümantasyon

### Gelecek Planları
- Performance testleri
- Load testleri
- API testleri (eğer API eklenirse)
- Test coverage raporu
- Automated testing pipeline
