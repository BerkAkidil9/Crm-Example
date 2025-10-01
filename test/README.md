# Test Sistemi

Bu klasör ProductsAndStock modülü için organize edilmiş test dosyalarını içerir.

## 📁 Klasör Yapısı

```
test/
├── __init__.py
├── products_and_stock/
│   ├── __init__.py
│   ├── working_tests/          # ✅ Çalışan testler
│   │   ├── __init__.py
│   │   └── simple_test.py
│   ├── broken_tests/           # ❌ Çalışmayan testler (düzeltilmesi gereken)
│   │   ├── __init__.py
│   │   ├── test_models.py
│   │   ├── test_views.py
│   │   ├── test_forms.py
│   │   └── test_integration.py
│   └── test_runner.py          # İnteraktif test çalıştırıcı
└── README.md
```

## 🚀 Test Çalıştırma

### ✅ Çalışan Testler
```bash
# Basit test (çalışan)
python manage.py test test.products_and_stock.working_tests.simple_test

# Verbose mod
python manage.py test test.products_and_stock.working_tests.simple_test -v 2
```

### ❌ Çalışmayan Testler (Düzeltilmesi Gereken)
```bash
# Model testleri (sorunlu)
python manage.py test test.products_and_stock.broken_tests.test_models

# View testleri (sorunlu)
python manage.py test test.products_and_stock.broken_tests.test_views

# Form testleri (sorunlu)
python manage.py test test.products_and_stock.broken_tests.test_forms

# Entegrasyon testleri (sorunlu)
python manage.py test test.products_and_stock.broken_tests.test_integration
```

## 📊 Test Durumu

### ✅ Çalışan Testler (5 test)
- **Dosya:** `working_tests/simple_test.py`
- **Durum:** 5/5 test başarılı
- **Kapsam:** Temel model testleri
- **Süre:** ~1 saniye

### ❌ Çalışmayan Testler (80+ test)
- **Dosya:** `broken_tests/` klasörü
- **Durum:** 53 hata, 1 başarısız
- **Sorunlar:** 
  - UserProfile unique constraint hatası
  - Form validasyon hataları
  - Model uyumsuzlukları

## 🔧 Sorunlar ve Çözümler

### 1. UserProfile Unique Constraint
**Sorun:** Aynı kullanıcı adıyla birden fazla UserProfile oluşturulmaya çalışılıyor
**Çözüm:** Her test sınıfında benzersiz kullanıcı adları kullanılmalı

### 2. Model Uyumsuzlukları
**Sorun:** Category modelinde `organisation` alanı yok
**Çözüm:** Test dosyalarında model yapısına uygun testler yazılmalı

### 3. Form Validasyon Hataları
**Sorun:** Form validasyon testlerinde yanlış assertion'lar
**Çözüm:** Form error mesajları doğru şekilde kontrol edilmeli

## 📈 Test Kapsamı

### Models (8 model)
- ✅ Category (çalışıyor)
- ✅ SubCategory (çalışıyor)
- ✅ ProductsAndStock (çalışıyor)
- ❌ StockMovement (sorunlu)
- ❌ PriceHistory (sorunlu)
- ❌ SalesStatistics (sorunlu)
- ❌ StockAlert (sorunlu)
- ❌ StockRecommendation (sorunlu)

### Views (7 view)
- ❌ ProductAndStockListView (sorunlu)
- ❌ ProductAndStockDetailView (sorunlu)
- ❌ ProductAndStockCreateView (sorunlu)
- ❌ ProductAndStockUpdateView (sorunlu)
- ❌ ProductAndStockDeleteView (sorunlu)
- ❌ BulkPriceUpdateView (sorunlu)
- ❌ SalesDashboardView (sorunlu)

### Forms (3 form)
- ❌ ProductAndStockModelForm (sorunlu)
- ❌ AdminProductAndStockModelForm (sorunlu)
- ❌ BulkPriceUpdateForm (sorunlu)

## 🎯 Gelecek Planları

1. **Çalışmayan testleri düzelt**
2. **Daha fazla çalışan test ekle**
3. **Diğer modüller için test klasörleri oluştur**
4. **Test coverage raporu ekle**

## 📝 Notlar

- Testler Django TestCase kullanır
- Her test bağımsız çalışır
- Test veritabanı otomatik oluşturulur ve silinir
- Mock kullanımı email gönderimi için
- Factory pattern kullanımı test verisi oluşturma için