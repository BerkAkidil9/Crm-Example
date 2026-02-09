# Turkish → English Translation Summary (Excluding Migrations)

This file lists all Turkish content in the project **excluding migration files**. Use it as a reference when translating to English.

**Last updated:** February 2025 - Most translations have been completed.

---

## 1. HTML Templates (UI text)

| File | Turkish text | Suggested English | Status |
|-------|--------------|---------------------|--------|
| `organisors/templates/organisors/organisor_list.html` | `Ara` (label) | `Search` | ✅ Already English |
| `agents/templates/agents/agent_list.html` | `Ara` (label) | `Search` | ✅ Already English |
| `leads/templates/leads/lead_list.html` | `Ara` (label) | `Search` | ✅ Already English |

---

## 2. Python – Uygulama kodu (yorumlar / mesajlar)

| File | Line | Turkish | Suggested English |
|-------|-------|--------|---------------------|
| `ProductsAndStock/views.py` | 567 | `# Critical Alerts: sadece urun hala kritik durumdaysa say ve listele (duzelince dusar)` | `# Critical Alerts: only count/list product if still in critical state (drop when fixed)` |
| `ProductsAndStock/views.py` | 568 | `# Ayni urun birden fazla alert kaydi ile tekrar etmesin: urun basina bir tane (en guncel alert)` | `# Same product should not repeat with multiple alert records: one per product (latest alert)` |

---

## 3. Documentation (MD files)

### 3.1 `START_PROJECT.md` (was fully Turkish, now translated)
- **Başlık:** "Django CRM Projesi Başlatma Rehberi" → "Django CRM Project Startup Guide"
- "Projeyi Sıfırdan Başlatmak İçin Gerekli Komutlar" → "Required Commands to Start the Project from Scratch"
- "Terminal/PowerShell'i açın ve proje klasörüne gidin" → "Open Terminal/PowerShell and go to the project folder"
- "Django sunucusunu başlatın" → "Start the Django server"
- "Tarayıcınızda şu adrese gidin" → "Go to the following address in your browser"
- "Alternatif Komutlar (Eğer yukarıdaki çalışmazsa)" → "Alternative Commands (If the above does not work)"
- "Eğer Python modülü bulunamazsa" → "If Python module is not found"
- "Önce gerekli paketleri yükleyin" → "First install the required packages"
- "Sonra sunucuyu başlatın" → "Then start the server"
- "Eğer port meşgulse" → "If the port is in use"
- "Çalışan Python işlemlerini durdurun" → "Stop running Python processes"
- "Tek Komut ile Başlatma (Önerilen)" → "Start with Single Command (Recommended)"
- "Not:" → "Note:"
- "Sunucuyu durdurmak için terminal'de..." → "To stop the server, press..."
- "Proje ... adresinde çalışacak" → "The project will run at..."
- "Eğer hata alırsanız..." → "If you get an error..."

### 3.2 `test/README.md`
- "Test Sistemi" → "Test System"
- "Bu klasör tüm modüller için organize edilmiş test dosyalarını içerir." → "This folder contains organized test files for all modules."
- "Klasör Yapısı" → "Folder Structure"
- "Agent testleri" → "Agent tests"
- "Finans testleri" → "Finance tests"
- "Şifre sıfırlama testleri" → "Password reset tests"
- "Lead testleri" → "Lead tests"
- "Login testleri" → "Login tests"
- "Çalışan testler" / "Çalışmayan testler" → "Working tests" / "Broken tests"
- "Logout testleri" → "Logout tests"
- "Sipariş testleri" → "Order tests"
- "Organizatör testleri" → "Organisor tests"
- "Ürün ve stok testleri" → "Product and stock tests"
- "Kayıt testleri" → "Signup tests"
- "Test Çalıştırma" → "Running Tests"
- "YENİ!" → "NEW!"
- "Tüm logout testleri (33 test - %100 başarılı!)" → "All logout tests (33 tests - 100% success!)"
- "İnteraktif test runner" → "Interactive test runner"
- "Diğer Modül Testleri" → "Other Module Tests"
- Ve dosyadaki diğer tüm Türkçe cümleler.

### 3.3 `test/orders/README.md`
- "Bu klasör Orders modülü için organize edilmiş test dosyalarını içerir." → "This folder contains organized test files for the Orders module."
- "Klasör Yapısı" → "Folder Structure"
- "Çalışan testler" → "Working tests"
- "Test Çalıştırma" → "Running Tests"
- "Test Kapsamı" → "Test Coverage"
- "Özel Test Özellikleri" → "Custom Test Features"
- "Stok geri yükleme testleri" → "Stock restoration tests"
- "Yetersiz stok kontrolü testleri" → "Insufficient stock check tests"
- "Stok hareket kayıt testleri" → "Stock movement record tests"
- "Test İstatistikleri" → "Test Statistics"
- "Toplam Test Sayısı" → "Total Test Count"
- Ve diğer Türkçe ifadeler.

### 3.4 `test/login/README.md`
- "Bu klasör login ile ilgili tüm test dosyalarını içerir." → "This folder contains all test files related to login."
- "Klasör Yapısı" → "Folder Structure"
- "Test Çalıştırma" → "Running Tests"
- "Çalışan Testler" → "Working Tests"
- "Test Kapsamı" → "Test Coverage"
- "Test Özellikleri" → "Test Features"
- "Geçerli veri testi" / "Geçersiz veri testi" → "Valid data test" / "Invalid data test"
- "Username ile giriş testi" → "Login with username test"
- "Email ile giriş testi" → "Login with email test"
- Ve diğer tüm Türkçe metinler.

### 3.5 `test/leads/README.md`
- "Bu klasör Leads modülü için organize edilmiş test dosyalarını içerir." → "This folder contains organized test files for the Leads module."
- "Test çalıştırıcı" → "Test runner"
- "Komut Satırından" → "From command line"
- "Tüm testler" → "All tests"
- "Hızlı testler" → "Quick tests"
- "Test kapsamını göster" → "Show test coverage"
- "Test Türleri" → "Test Types"
- "Model oluşturma ve kaydetme" → "Model creation and saving"
- "Form başlatma ve alan kontrolü" → "Form initialization and field check"
- "Form validasyonu (geçerli/geçersiz veri)" → "Form validation (valid/invalid data)"
- "Test Verisi Yönetimi" → "Test Data Management"
- "Test Başarısız Olursa" → "If Test Fails"
- "Yaygın Sorunlar" → "Common Issues"
- "Gelecek Planları" → "Future Plans"
- Ve dosyadaki diğer Türkçe ifadeler.

### 3.6 `test/forget_password/README.md`
- "Bu klasör forget password (şifre sıfırlama) modülü için..." → "This folder contains organized test files for the forget password module."
- "Test çalıştırıcı" → "Test runner"
- "Tüm Testleri Çalıştır" → "Run All Tests"
- "Belirli Test Dosyalarını Çalıştır" → "Run Specific Test Files"
- "Belirli Test Sınıflarını Çalıştır" → "Run Specific Test Classes"
- "Belirli Test Metodlarını Çalıştır" → "Run Specific Test Methods"
- "Test Kapsamı" → "Test Coverage"
- "Geçerli email ile POST testi" → "POST test with valid email"
- "Şifre uyumsuzluğu testi" → "Password mismatch test"
- "Zayıf şifre testi" → "Weak password test"
- Ve diğer tüm Türkçe metinler.

### 3.7 `test/logout/TEST_RESULTS.md`
- Tamamı Türkçe açıklamalı (başlıklar, test isimleri, kategoriler, öneriler, öğrenilen dersler vb.). Tüm bu metinler İngilizceye çevrilebilir.

### 3.8 `test/logout/SUMMARY.md` (formerly OZET.md)
- File renamed to SUMMARY.md; content was already in English.

### 3.9 `test/organisors/README.md`
- Türkçe kısımlar (varsa) benzer şekilde "Test Coverage", "Running Tests" vb. İngilizce karşılıklara çevrilebilir.

### 3.10 `test/signup/README.md`
- Türkçe kısımlar (varsa) aynı terminoloji ile İngilizceye çevrilebilir.

---

## 4. Python – Test files (Turkish docstrings / comments)

The following files contained **Turkish docstrings** and **Turkish comment lines**. All have been translated to English (e.g. "Test verilerini hazırla" → "Set up test data", "Gerekli alanların varlığını kontrol et" → "Check presence of required fields").

| Location | Note |
|-------|-----|
| `test/leads/test_forms.py` | Çok sayıda Türkçe docstring ve yorum |
| `test/products_and_stock/working_tests/test_forms.py` | Türkçe docstring ve yorumlar |
| `test/products_and_stock/working_tests/test_integration.py` | Türkçe docstring ve yorumlar |
| `test/products_and_stock/working_tests/simple_test.py` | Türkçe yorum |
| `test/products_and_stock/working_tests/__init__.py` | "Çalışan testler - ProductsAndStock modülü" → "Working tests - ProductsAndStock module" |
| `test/products_and_stock/test_runner.py` | "Test modülünü import et", "BAŞARISIZ" vb. |
| `test/products_and_stock/broken_tests/test_forms.py` | Türkçe docstring ve yorumlar |
| `test/products_and_stock/broken_tests/test_views_simple.py` | Türkçe docstring ve yorumlar |
| `test/leads/test_integration.py` | "Email entegrasyon testleri" vb. |

Example translations:
- "Test verilerini hazırla" → "Set up test data"
- "Form başlatma testi" → "Form initialization test"
- "Geçerli veri ile form testi" → "Form test with valid data"
- "Gerekli alanların varlığını kontrol et" → "Check that required fields exist"
- "Kullanıcı izinleri iş akışı testi" → "User permissions workflow test"
- "Admin kullanıcı ... erişimi" → "Admin user ... access"
- "ProductsAndStock Formları Test Dosyası" → "ProductsAndStock Forms Test File"
- "Bu dosya ... tüm formları test eder." → "This file tests all forms in..."
- "Django ayarlarını yükle" → "Load Django settings"
- "Test çalıştırma" → "Run tests"
- "Testleri Başlatılıyor" → "Starting tests"
- "BAŞARISIZ" → "FAILED"

---

## 5. Summary table (excluding migrations)

| Category | Approx. file count | Priority |
|----------|--------------------------|---------|
| HTML (UI) | 3 | High (user-facing) |
| Python app (comment) | 1 (`ProductsAndStock/views.py`) | Medium |
| Documentation (MD) | 10+ | Medium |
| Test files (docstring/comment) | 9+ | Low (optional) |

---

## 6. Migration’lar hakkında

**Migrations are excluded.**  
Files such as `activity_log/migrations/0001_initial.py`, `tasks/migrations/0001_initial.py` contain Turkish `verbose_name` and choice texts (e.g. "Organisor oluşturuldu", "Başlık", "İçerik"). Changing these would generate new migrations or risk database incompatibility; use English only for **new** models/fields. Leave existing migration files untouched.

---

## 7. Completed translations (February 2025)

The following have been translated to English (migrations left unchanged as per section 6):

- **Application code:** `ProductsAndStock/forms.py` (comments)
- **Test runners:** `test/finance/test_runner.py`, `test/orders/test_runner.py`, `test/leads/test_runner.py` (all Turkish strings)
- **Orders tests:** `test/orders/working_tests/test_models.py`, `test_integration.py`, `test_views.py`, `test_forms.py` (docstrings and comments)
- **Finance tests:** `test/finance/working_tests/test_models.py`, `test_integration.py`, `test_forms.py` (docstrings and comments)
- **Organisors tests:** `test/organisors/working_tests/test_integration.py` (one comment)

Remaining (optional): test/leads/test_forms.py, test/login, test/forget_password, test/logout, test/products_and_stock, test/agents (runners and some comments), leads/management/commands, agents/mixins.py – may still contain Turkish docstrings/comments.

---

*This report was created via automatic scanning and review. Add any additional Turkish text you notice to this list.*
