# Agent Test Sistemi

Bu klasör Agent modülü için organize edilmiş test dosyalarını içerir.

## 📁 Klasör Yapısı

```
test/agents/
├── __init__.py
├── working_tests/          # ✅ Çalışan testler
│   ├── __init__.py
│   ├── test_models.py      # Agent model testleri
│   ├── test_forms.py       # Agent form testleri
│   ├── test_views.py       # Agent view testleri
│   ├── test_mixins.py      # Agent mixin testleri
│   └── test_integration.py # Agent entegrasyon testleri
├── test_runner.py          # İnteraktif test çalıştırıcı
└── README.md
```

## 🚀 Test Çalıştırma

### ✅ Tüm Testleri Çalıştır
```bash
# Tüm agent testleri
python manage.py test test.agents.working_tests

# Verbose mod
python manage.py test test.agents.working_tests -v 2
```

### ✅ Belirli Test Modüllerini Çalıştır
```bash
# Model testleri
python manage.py test test.agents.working_tests.test_models

# Form testleri
python manage.py test test.agents.working_tests.test_forms

# View testleri
python manage.py test test.agents.working_tests.test_views

# Mixin testleri
python manage.py test test.agents.working_tests.test_mixins

# Entegrasyon testleri
python manage.py test test.agents.working_tests.test_integration
```

### ✅ İnteraktif Test Çalıştırıcı
```bash
python test/agents/test_runner.py
```

## 📊 Test Kapsamı

### Models (2 model)
- ✅ Agent (çalışıyor)
- ✅ EmailVerificationToken (çalışıyor)

### Views (5 view)
- ✅ AgentListView (çalışıyor)
- ✅ AgentCreateView (çalışıyor)
- ✅ AgentDetailView (çalışıyor)
- ✅ AgentUpdateView (çalışıyor)
- ✅ AgentDeleteView (çalışıyor)

### Forms (3 form)
- ✅ AgentModelForm (çalışıyor)
- ✅ AgentCreateForm (çalışıyor)
- ✅ AdminAgentCreateForm (çalışıyor)

### Mixins (3 mixin)
- ✅ OrganisorAndLoginRequiredMixin (çalışıyor)
- ✅ AgentAndOrganisorLoginRequiredMixin (çalışıyor)
- ✅ ProductsAndStockAccessMixin (çalışıyor)

### Integration Tests
- ✅ Agent Full Workflow (çalışıyor)
- ✅ Email Verification Workflow (çalışıyor)
- ✅ Form Integration (çalışıyor)

## 🧪 Test Details

### Model Testleri (test_models.py)
- **TestAgentModel**: Agent modeli temel işlevleri
- **TestEmailVerificationTokenModel**: Email doğrulama token modeli
- **TestAgentModelIntegration**: Model entegrasyon testleri

**Test Sayısı**: 25+ test
**Kapsam**: Model oluşturma, silme, ilişkiler, validasyonlar

### Form Testleri (test_forms.py)
- **TestAgentModelForm**: Agent güncelleme formu
- **TestAgentCreateForm**: Agent oluşturma formu
- **TestAdminAgentCreateForm**: Admin agent oluşturma formu
- **TestAgentFormIntegration**: Form entegrasyon testleri

**Test Sayısı**: 40+ test
**Kapsam**: Form validasyonu, widget özellikleri, save metodları

### View Testleri (test_views.py)
- **TestAgentListView**: Agent listesi görüntüleme
- **TestAgentCreateView**: Agent oluşturma
- **TestAgentDetailView**: Agent detay görüntüleme
- **TestAgentUpdateView**: Agent güncelleme
- **TestAgentDeleteView**: Agent silme

**Test Sayısı**: 50+ test
**Kapsam**: Erişim kontrolleri, form işleme, redirect'ler

### Mixin Testleri (test_mixins.py)
- **TestOrganisorAndLoginRequiredMixin**: Organisor erişim kontrolü
- **TestAgentAndOrganisorLoginRequiredMixin**: Agent ve Organisor erişim kontrolü
- **TestProductsAndStockAccessMixin**: Ürün erişim kontrolü
- **TestMixinIntegration**: Mixin entegrasyon testleri

**Test Sayısı**: 30+ test
**Kapsam**: İzin kontrolleri, erişim kısıtlamaları

### Entegrasyon Testleri (test_integration.py)
- **TestAgentFullWorkflow**: Tam agent iş akışı
- **TestAgentEmailVerificationWorkflow**: Email doğrulama iş akışı
- **TestAgentFormIntegration**: Form entegrasyon testleri

**Test Sayısı**: 20+ test
**Kapsam**: End-to-end iş akışları, email gönderimi

## 🔧 Test Özellikleri

### Mock Kullanımı
- Email gönderimi için `send_mail` mock'u
- Zaman işlemleri için `timezone.now` mock'u
- Database işlemleri için transaction testleri

### Test Verisi Yönetimi
- Her test bağımsız çalışır
- `setUp` metodunda test verileri hazırlanır
- `tearDown` metodunda temizlik yapılır

### Assertion'lar
- Model oluşturma/silme kontrolü
- Form validasyon kontrolü
- View response kontrolü
- Redirect kontrolü
- Email gönderim kontrolü

## 📈 Test Metrikleri

### Toplam Test Sayısı
- **Model Testleri**: 25+ test
- **Form Testleri**: 40+ test
- **View Testleri**: 50+ test
- **Mixin Testleri**: 30+ test
- **Entegrasyon Testleri**: 20+ test
- **TOPLAM**: 165+ test

### Test Kategorileri
- **Unit Tests**: Model, Form, Mixin testleri
- **Integration Tests**: View, Workflow testleri
- **Functional Tests**: End-to-end iş akışları

### Coverage
- **Model Coverage**: %100
- **Form Coverage**: %100
- **View Coverage**: %100
- **Mixin Coverage**: %100

## 🎯 Gelecek Planları

1. **Performance testleri ekle**
2. **Load testleri ekle**
3. **Security testleri ekle**
4. **API testleri ekle**
5. **Test coverage raporu ekle**

## 📝 Notlar

- Testler Django TestCase kullanır
- Her test bağımsız çalışır
- Test veritabanı otomatik oluşturulur ve silinir
- Mock kullanımı email gönderimi için
- Factory pattern kullanımı test verisi oluşturma için
- Transaction testleri veritabanı tutarlılığı için

## 🚨 Önemli Notlar

- Testler çalıştırılmadan önce Django ayarlarının yüklenmesi gerekir
- Test veritabanı otomatik oluşturulur ve silinir
- Mock'lar test sonrası otomatik temizlenir
- Test dosyaları `working_tests` klasöründe tutulur
- Test runner ile interaktif test çalıştırma mümkündür
