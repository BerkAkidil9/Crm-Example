# Orders App Test Sistemi

Bu klasör Orders modülü için organize edilmiş test dosyalarını içerir.

## 📁 Klasör Yapısı

```
test/orders/
├── __init__.py
├── working_tests/          # ✅ Çalışan testler
│   ├── __init__.py
│   ├── test_models.py
│   ├── test_views.py
│   ├── test_forms.py
│   └── test_integration.py
├── test_runner.py          # İnteraktif test çalıştırıcı
└── README.md
```

## 🚀 Test Çalıştırma

### ✅ Çalışan Testler
```bash
# Model testleri
python manage.py test test.orders.working_tests.test_models

# View testleri
python manage.py test test.orders.working_tests.test_views

# Form testleri
python manage.py test test.orders.working_tests.test_forms

# Entegrasyon testleri
python manage.py test test.orders.working_tests.test_integration

# Tüm orders testleri
python manage.py test test.orders.working_tests
```

## 📊 Test Kapsamı

### Models (2 model)
- ✅ orders (çalışıyor)
- ✅ OrderProduct (çalışıyor)

### Views (6 view)
- ✅ OrderListView (çalışıyor)
- ✅ OrderDetailView (çalışıyor)
- ✅ OrderCreateView (çalışıyor)
- ✅ OrderUpdateView (çalışıyor)
- ✅ OrderCancelView (çalışıyor)
- ✅ OrderDeleteView (çalışıyor)

### Forms (3 form)
- ✅ OrderModelForm (çalışıyor)
- ✅ OrderForm (çalışıyor)
- ✅ OrderProductFormSet (çalışıyor)

## 🔧 Özel Test Özellikleri

### Stock Management Testleri
- Otomatik stok azaltma testleri
- Stok geri yükleme testleri
- Yetersiz stok kontrolü testleri

### Signal Testleri
- OrderProduct oluşturma signal testleri
- Order iptal etme signal testleri
- Stok hareket kayıt testleri

### Finance Integration Testleri
- OrderFinanceReport oluşturma testleri
- Toplam fiyat hesaplama testleri

## 📈 Test İstatistikleri

- **Toplam Test Sayısı:** 45+ test
- **Model Testleri:** 15 test
- **View Testleri:** 20 test
- **Form Testleri:** 8 test
- **Entegrasyon Testleri:** 5 test

## 📝 Notlar

- Testler Django TestCase kullanır
- Her test bağımsız çalışır
- Test veritabanı otomatik oluşturulur ve silinir
- Mock kullanımı email gönderimi için
- Factory pattern kullanımı test verisi oluşturma için
- Signal testleri için TransactionTestCase kullanılır
