# Finance Test Sistemi

Bu klasör Finance modülü için organize edilmiş test dosyalarını içerir.

## 📁 Klasör Yapısı

```
test/finance/
├── __init__.py
├── working_tests/          # ✅ Çalışan testler
│   ├── __init__.py
│   ├── test_models.py      # Model testleri
│   ├── test_views.py       # View testleri
│   ├── test_forms.py       # Form testleri
│   └── test_integration.py # Entegrasyon testleri
├── test_runner.py          # İnteraktif test çalıştırıcı
└── README.md
```

## 🚀 Test Çalıştırma

### ✅ Tüm Testler
```bash
# Tüm finance testleri
python manage.py test test.finance.working_tests

# Verbose mod
python manage.py test test.finance.working_tests -v 2

# Test runner kullanarak
python test/finance/test_runner.py --module all
```

### 📊 Modül Bazında Testler
```bash
# Model testleri
python manage.py test test.finance.working_tests.test_models
python test/finance/test_runner.py --module models

# View testleri
python manage.py test test.finance.working_tests.test_views
python test/finance/test_runner.py --module views

# Form testleri
python manage.py test test.finance.working_tests.test_forms
python test/finance/test_runner.py --module forms

# Entegrasyon testleri
python manage.py test test.finance.working_tests.test_integration
python test/finance/test_runner.py --module integration
```

## 📊 Test Kapsamı

### Models (1 model)
- ✅ OrderFinanceReport (çalışıyor)
  - Model oluşturma
  - String representation
  - Default değerler
  - OneToOneField ilişkisi
  - Unique constraint
  - Cascade delete
  - Float precision
  - Edge cases

### Views (1 view)
- ✅ FinancialReportView (çalışıyor)
  - GET request
  - POST request (valid/invalid)
  - Date range filtering
  - Template rendering
  - Context data
  - Aggregation
  - Edge cases

### Forms (1 form)
- ✅ DateRangeForm (çalışıyor)
  - Valid data
  - Invalid data
  - Date validation
  - Clean method
  - Widget configuration
  - Error messages
  - Edge cases

### Integration Tests
- ✅ Finance-Orders entegrasyonu
- ✅ Finance-Products entegrasyonu
- ✅ Finance-Views entegrasyonu
- ✅ Veri tutarlılığı
- ✅ Cascade operations
- ✅ Date filtering
- ✅ Organisation filtering

## 🎯 Test Details

### OrderFinanceReport Model Testleri (15 test)
1. **Model Creation Tests**
   - OrderFinanceReport oluşturma
   - String representation
   - Default report_date
   - Manual report_date

2. **Field Tests**
   - Earned amount (positive, zero, negative)
   - Float precision
   - Large amounts

3. **Relationship Tests**
   - OneToOneField with orders
   - Unique constraint
   - Cascade delete

4. **Integration Tests**
   - Multiple orders
   - Date filtering
   - Organisation filtering
   - Aggregation

### FinancialReportView Tests (15 test)
1. **GET Request Tests**
   - Template rendering
   - Context data
   - Form display

2. **POST Request Tests**
   - Valid dates
   - Invalid dates
   - Date range filtering
   - Empty results

3. **Template Tests**
   - With reports
   - Empty results
   - Data display

4. **Edge Cases**
   - No orders
   - Orders without finance reports
   - Zero/negative amounts

### DateRangeForm Tests (20 test)
1. **Validation Tests**
   - Valid data
   - Invalid data
   - Date format errors
   - Missing fields

2. **Date Logic Tests**
   - Same dates
   - End date before start date
   - Future dates
   - Past dates

3. **Form Configuration Tests**
   - Widget years range
   - Field types
   - Required fields
   - Labels

4. **Edge Cases**
   - Extreme date ranges
   - Leap year dates
   - Year boundaries
   - None values

### Integration Tests (15 test)
1. **Finance-Orders Integration**
   - Order creation with finance report
   - Order cancellation impact
   - Order deletion cascade
   - Multiple orders aggregation

2. **Finance-Products Integration**
   - Profit calculation
   - Multiple products profit
   - Stock movement integration

3. **Finance-Views Integration**
   - Full workflow
   - Form integration

4. **Data Consistency**
   - Data integrity
   - Unique constraints

## 📈 Test İstatistikleri

### Toplam Test Sayısı: 65 test
- **Model Tests:** 15 test
- **View Tests:** 15 test  
- **Form Tests:** 20 test
- **Integration Tests:** 15 test

### Test Kategorileri
- **Unit Tests:** 50 test
- **Integration Tests:** 15 test

### Kapsanan Modüller
- ✅ OrderFinanceReport model
- ✅ FinancialReportView
- ✅ DateRangeForm
- ✅ Finance-Orders entegrasyonu
- ✅ Finance-Products entegrasyonu
- ✅ Finance-Views entegrasyonu

## 🔧 Test Özellikleri

### Test Setup
- Her test bağımsız çalışır
- Test veritabanı otomatik oluşturulur ve silinir
- Mock kullanımı gerektiğinde
- Factory pattern test verisi oluşturma için

### Test Data
- Organisor kullanıcıları
- UserProfile'lar
- Lead'ler
- Kategoriler ve ürünler
- Order'lar ve OrderProduct'lar
- Finance report'lar

### Assertions
- Model field validations
- View response codes
- Template content
- Form validation
- Database queries
- Data relationships

## 🎯 Gelecek Planları

1. **Performance Tests** - Büyük veri setleri ile test
2. **Security Tests** - Authorization ve authentication
3. **API Tests** - REST API endpoint'leri
4. **Load Tests** - Yüksek trafik senaryoları
5. **Coverage Reports** - Test coverage analizi

## 📝 Notlar

- Testler Django TestCase kullanır
- Her test bağımsız çalışır
- Test veritabanı otomatik oluşturulur ve silinir
- Mock kullanımı email gönderimi için
- Factory pattern kullanımı test verisi oluşturma için
- Integration testler modüller arası etkileşimi test eder
- Edge case testler sınır durumları kapsar
