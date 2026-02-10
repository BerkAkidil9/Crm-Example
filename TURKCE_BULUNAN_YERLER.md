# Projedeki Tüm Türkçe Kısımlar (Migrations Hariç)

Bu dosya, İngilizceye çeviri yapmanız için projede **migration dosyaları hariç** bulunan tüm Türkçe metinleri listeler.

**✅ Çeviri tamamlandı (Şubat 2025):** Tüm test dosyalarındaki (test/logout, test/login, test/forget_password, test/products_and_stock/broken_tests) Türkçe yorumlar ve docstring'ler İngilizceye çevrildi. README ve TEST_RESULTS.md zaten İngilizceydi.

---

## 1. Test dosyaları (Python – yorumlar ve docstring’ler)

### test/logout/working/test_logout_integration.py
- Satır 16: `# Django ayarlarını yükle` → "Load Django settings"
- Satır 50: `# Organisor oluştur` → "Create organisor"
- Satır 55: `# 1. Login sayfasına git` → "1. Go to login page"
- Satır 59: `# 2. Login form gönder` → "2. Submit login form"
- Satır 67: `# 3. Kullanıcı giriş yapmış mı kontrol et` → "3. Check if user is logged in"
- Satır 70: `# 4. Korumalı sayfaya erişim testi` → "4. Protected page access test"
- Satır 82: `# 7. Logout sonrası korumalı sayfaya erişim engellenmeli` → "7. Access to protected page after logout should be denied"
- Satır 88: `# 1. İlk login` → "1. First login"
- Satır 109: `# 4. Korumalı sayfaya erişim` → "4. Protected page access"
- Satır 143: `# Session'a özel veriler ekle` → "Add custom data to session"
- Satır 157: `# Tüm session verileri temizlenmeli` → "All session data should be cleared"
- Satır 164: `# İki farklı client (farklı tarayıcıları simüle eder)` → "Two different clients (simulate different browsers)"
- Satır 172: `# Her iki client giriş yapmış olmalı` → "Both clients should be logged in"
- Satır 181: `# Client2 hala giriş yapmış olmalı (farklı session)` → "Client2 should still be logged in (different session)"
- Satır 184: `# Client2 korumalı sayfaya erişebilmeli` → "Client2 should be able to access protected page"
- Satır 188: `# Client1 korumalı sayfaya erişememeli` → "Client1 should not access protected page"
- Satır 200: `# Landing page'e redirect olmalı` → "Should redirect to landing page"
- Satır 208: `# Landing page template kullanılmalı` → "Landing page template should be used"
- Satır 217: `# Şifre değiştir (password change view yerine direkt değiştir)` → "Change password (change directly instead of password change view)"
- Satır 226: `# Eski şifre ile login denemesi başarısız olmalı` → "Login attempt with old password should fail"
- Satır 231: `# Form hataları ile geri döner` → "Returns with form errors"
- Satır 234: `# Yeni şifre ile login başarılı olmalı` → "Login with new password should succeed"
- Satır 244–245: `# Bu test, eğer remember me özelliği eklenirse güncellenebilir` / `# Şu anda remember me özelliği olmadığı için basit test` → "This test can be updated if remember me is added" / "Simple test since there is no remember me feature"
- Satır 273: `# Logout başarılı olmalı` → "Logout should succeed"
- Satır 277: `# Ortalama logout süresi 0.5 saniyeden az olmalı` → "Average logout time should be less than 0.5 seconds"
- Satır 283: `# Organizer ile tam akış` → "Full flow with organiser"
- Satır 307: `# Agent ile tam akış` → "Full flow with agent"
- Satır 327: `# Superuser ile tam akış` → "Full flow with superuser"
- Satır 359: `# Organisor oluştur` → "Create organisor"
- Satır 371: `# Korumalı sayfaya erişim (başarılı)` → "Protected page access (success)"
- Satır 378: `# Eski session bilgileri ile korumalı sayfaya erişim denemesi` → "Attempt to access protected page with old session data"
- Satır 382: `# Session temizlenmiş olmalı` → "Session should be cleared"
- Satır 412: `# Tüm hassas veriler temizlenmeli` → "All sensitive data should be cleared"
- Satır 426–427: `# Login sonrası session key değişmeli` / `# Bu test session fixation saldırısına karşı koruma sağlar` → "Session key should change after login" / "This test protects against session fixation"
- Satır 434: `# Django logout sonrası session flush eder` → "Django flushes session after logout"
- Satır 440: `print("Logout Entegrasyon Testleri Başlatılıyor...")` → `print("Starting Logout Integration Tests...")`
- Satır 443: `# Test çalıştırma` → "Run tests"

### test/logout/working/test_logout_views.py
- Satır 2–3: `Logout Viewları Test Dosyası` / `Bu dosya logout ile ilgili tüm viewları test eder.` → "Logout Views Test File" / "This file tests all views related to logout."
- Satır 16: `# Django ayarlarını yükle` → "Load Django settings"
- Satır 55: `# Önce giriş yap` → "Log in first"
- Satır 58: `# Session kontrolü - giriş yapmış olmalı` → "Session check - should be logged in"
- Satır 64: `# Redirect olmalı` → "Should redirect"
- Satır 73: `# Önce giriş yap` → "Log in first"
- Satır 76: `# Session kontrolü - giriş yapmış olmalı` → "Session check - should be logged in"
- Satır 79: `# GET ile logout yap (Django LogoutView GET'i desteklemez, 405 döner)` → "Logout via GET (Django LogoutView does not support GET, returns 405)"
- Satır 82: `# Method not allowed olmalı (Django LogoutView sadece POST destekler)` → "Should be method not allowed (Django LogoutView only supports POST)"
- Satır 85: `# Session hala aktif olmalı (logout olmadı)` → "Session should still be active (did not logout)"
- Satır 90: `# Session kontrolü - giriş yapmamış olmalı` → "Session check - should not be logged in"
- Satır 93: `# Logout yap (giriş yapmamış olsa bile)` → "Perform logout (even if not logged in)"
- Satır 96: `# Redirect olmalı` → "Should redirect"
- Satır 100: `# Session hala boş olmalı` → "Session should still be empty"
- Satır 105: `# Önce giriş yap` → "Log in first"
- Satır 111: `# LOGOUT_REDIRECT_URL'ye redirect olmalı (settings.py'de '/' olarak tanımlı)` → "Should redirect to LOGOUT_REDIRECT_URL (defined as '/' in settings.py)"
- Satır 117: `# Önce giriş yap` → "Log in first"
- Satır 137: `# Önce giriş yap` → "Log in first"
- Satır 140: `# Korumalı sayfaya erişim (giriş yapmış)` → "Protected page access (logged in)"
- Satır 147: `# Logout sonrası korumalı sayfaya erişim engellenmeli` → "Access to protected page after logout should be denied"
- Satır 153: `# Önce giriş yap` → "Log in first"
- Satır 156: `# İlk logout` → "First logout"
- Satır 161: `# İkinci logout (zaten logout olmuş)` → "Second logout (already logged out)"
- Satır 166: `# Üçüncü logout (hala logout)` → "Third logout (still logged out)"
- Satır 173: `# Önce giriş yap` → "Log in first"
- Satır 185: `# Önce giriş yap` → "Log in first"
- Satır 192: `# Redirect URL next parametresine göre değişebilir` → "Redirect URL may vary by next parameter"
- Satır 203: `# Agent kullanıcı oluştur` → "Create agent user"
- Satır 241: `# Superuser ile giriş yap` → "Log in as superuser"
- Satır 252: `# Önce giriş yap` → "Log in first"
- Satır 255: `# Session'a özel veri ekle` → "Add custom data to session"
- Satır 266: `# Session flush edilir, tüm veriler temizlenir` → "Session is flushed, all data is cleared"
- Satır 277: `# Her iki client ile giriş yap` → "Log in with both clients"
- Satır 281: `# Her iki client giriş yapmış olmalı` → "Both clients should be logged in"
- Satır 290: `# Client2 hala giriş yapmış olmalı (farklı session)` → "Client2 should still be logged in (different session)"
- Satır 295: `# Logout URL'i doğru mu` → "Is logout URL correct"
- Satır 301: `# Önce giriş yap` → "Log in first"
- Satır 304: `# AJAX isteği ile logout` → "Logout via AJAX request"
- Satır 310: `# Redirect olmalı` → "Should redirect"
- Satır 353–354: `# Yeni session oluşturulmalı (session key değişmeli)` / `# Django logout sonrası session flush eder` → "New session should be created (session key should change)" / "Django flushes session after logout"
- Satır 363: `# Önce giriş yap` → "Log in first"
- Satır 372: `# Eski session ile korumalı sayfaya erişim denemesi` → "Attempt to access protected page with old session"
- Satır 375: `# Erişim engellenmeli (redirect to login)` → "Access should be denied (redirect to login)"
- Satır 380: `# Önce giriş yap` → "Log in first"
- Satır 395: `# Önce giriş yap` → "Log in first"
- Satır 401–403: `# Cache-Control header'ları kontrol et` / `# Django LogoutView otomatik cache kontrolü eklemez` / `# Ancak logout sonrası sayfalar cache'lenmemeli` → "Check Cache-Control headers" / "Django LogoutView does not add cache control automatically" / "But pages should not be cached after logout"
- Satır 408: `print("Logout View Testleri Başlatılıyor...")` → `print("Starting Logout View Tests...")`
- Satır 411: `# Test çalıştırma` → "Run tests"

### test/login/working/test_login_views.py
- Satır 123: `# Kullanıcı giriş yapmamış mı` → "User is not logged in"
- Satır 137, 151, 165: aynı yorum
- Satır 190: `# Önce giriş yap` → "Log in first"
- Satır 193: `# Login sayfasına git` → "Go to login page"
- Satır 206: `# Landing page'e redirect olmalı` → "Should redirect to landing page"
- Satır 212: `# Geçersiz email formatı` → "Invalid email format"
- Satır 221: `# Çok uzun username` → "Username too long"
- Satır 223: `# Çok uzun username` (yorum) → "Username too long"
- Satır 232: `# CSRF token olmadan POST isteği` → "POST request without CSRF token"
- Satır 244: `# Bu test, eğer remember me özelliği eklenirse güncellenebilir` → "This test can be updated if remember me is added"
- Satır 257: `# Büyük harflerle` → "In uppercase"
- Satır 317, 321, 329: `# 1. Login sayfasına git` vb. → "1. Go to login page" etc.
- Satır 356: `# Önce giriş yap` → "Log in first"
- Satır 365: `# Tekrar giriş yap` → "Log in again"
- Satır 375: `print("Login View Testleri Başlatılıyor...")` → `print("Starting Login View Tests...")`
- Satır 378: `# Test çalıştırma` → "Run tests"

### test/login/working/test_login_forms.py
- Satır 118: `# Yanlış password` → "Wrong password"
- Satır 219: `# Büyük harflerle` → "In uppercase"
- Satır 227: `# Büyük harflerle` → "In uppercase"
- Satır 241: `"""Form hata mesajları testi"""` → `"""Form error messages test"""`
- Satır 295: `# Unicode karakterler içeren username` → "Username containing Unicode characters"
- Satır 297: `'username': 'tëstüsér'` → (test verisi, karakterler kasıtlı; açıklama İngilizce yapılabilir)

### test/login/working/test_login_authentication.py
- Satır 295: `# Inactive kullanıcı` → "Inactive user"

### test/forget_password/test_forget_password_forms.py
- Satır 468–469, 474–475: `'pässwörd123!'` → (şifre test verisi; özel karakter testi için kalabilir, docstring’ler çevrilebilir)
- Dosyada başka Türkçe docstring’ler varsa (örn. "Form şifre uyumsuzluğu testi") İngilizceye çevrilebilir.

### test/products_and_stock/broken_tests/test_views.py
- Satır 2–3: `ProductsAndStock Viewları Test Dosyası` / `Bu dosya ProductsAndStock modülündeki tüm viewları test eder.` → "ProductsAndStock Views Test File" / "This file tests all views in the ProductsAndStock module."
- Satır 16: `# Django ayarlarını yükle` → "Load Django settings"
- Satır 37: `# Kullanıcılar oluştur` → "Create users"
- Satır 74: `# Kategori ve alt kategori oluştur` → "Create category and subcategory"
- Satır 81: `# Ürünler oluştur` → "Create products"
- Satır 106: `# Agent için aynı organisation'dan ürün` → "Product from same organisation for agent"
- Satır 120: `"""Anonim kullanıcı erişim testi"""` → `"""Anonymous user access test"""`
- Satır 125: `"""Admin kullanıcı erişim testi"""` → `"""Admin user access test"""`
- Satır 133: `"""Organisor kullanıcı erişim testi"""` → `"""Organisor user access test"""`
- Satır 141: `"""Agent kullanıcı erişim testi"""` → `"""Agent user access test"""`
- Satır 145: `# Agent'ın kendi ürünü` → "Agent's own product"
- Satır 180: `# 3 ürün var` → "3 products"
- Satır 182: `# Doğru hesaplama` → "Correct calculation"
- Satır 229: `# Stok hareketi ve fiyat geçmişi oluştur` → "Create stock movement and price history"
- Satır 251, 258, 268: Anonim/Admin/Organisor erişim testi docstring’leri
- Satır 287: `# Stok hareketleri ve fiyat geçmişi kontrolü` → "Stock movements and price history check"
- Satır 325, 330, 337, 344, 368: GET/POST test docstring’leri
- Satır 364: `# Ürün oluşturuldu mu kontrol et` → "Check if product was created"
- Satır 387: aynı
- Satır 392: `"""Geçersiz veri ile POST isteği testi"""` → `"""POST request with invalid data test"""`
- Satır 396: `# Boş isim` → "Empty name"
- Satır 407: `# Form hataları ile geri döner` → "Returns with form errors"
- Satır 409: `# Ürün oluşturulmadı mı kontrol et` → "Check that product was not created"
- Satır 458, 465, 474, 483, 506, 512, 534: erişim/güncelleme test docstring’leri
- Satır 585, 592, 601, 613, 621: silme test docstring’leri
- Satır 643: `"""Geçerli kategori ID ile test"""` → `"""Test with valid category ID"""`
- Satır 659: `"""Geçersiz kategori ID ile test"""` → `"""Test with invalid category ID"""`
- Satır 711: `# Test ürünleri oluştur` → "Create test products"
- Satır 737, 742, 749: erişim ve toplu güncelleme docstring’leri
- Satır 749: `"""Yüzde artış ile toplu fiyat güncelleme testi"""` → `"""Bulk price update test with percentage increase"""`
- Satır 762: `# Fiyatlar güncellendi mi kontrol et` → "Check if prices were updated"
- Satır 772: `# Fiyat geçmişi oluşturuldu mu kontrol et` → "Check if price history was created"
- Satır 777: `"""Sabit miktar artış ile toplu fiyat güncelleme testi"""` → `"""Bulk price update test with fixed amount increase"""`
- Satır 790, 798, 811, 819: ilgili docstring ve yorumlar
- Satır 833: `# Sadece seçili kategorideki ürünler güncellendi mi kontrol et` → "Check that only products in selected category were updated"
- Satır 876: `# Test ürünleri oluştur` → "Create test products"
- Satır 901: `# Stok uyarısı oluştur` → "Create stock alert"
- Satır 910: `# Stok önerisi oluştur` → "Create stock recommendation"
- Satır 921, 926, 933: erişim test docstring’leri
- Satır 957: `# Değerleri kontrol et` → "Check values"
- Satır 965: `print("ProductsAndStock Viewları Testleri Başlatılıyor...")` → `print("Starting ProductsAndStock View Tests...")`
- Satır 968: `# Test çalıştırma` → "Run tests"

### test/products_and_stock/broken_tests/test_forms.py
- Satır 120: `# Farklı kategoride alt kategori oluştur` → "Create subcategory in different category"
- Satır 306: aynı yorum

---

## 2. Uygulama kodu (views, models, forms)

- **activity_log/models.py**, **tasks/models.py**, **leads/models.py**, **ProductsAndStock/models.py**, **organisors/models.py**, **agents**, **orders**, **finance**: Bu modüllerdeki **mevcut** model/form metinleri (verbose_name, help_text, choices) şu an İngilizce görünüyor. Eğer başka bir dalda veya dosyada Türkçe kalmışsa sadece orada çeviri yapın.
- **Views mesajları**: `leads/views.py`, `orders/views.py`, `ProductsAndStock/views.py` içindeki `messages.success` / `messages.error` metinleri tarandı; İngilizce.

---

## 3. HTML şablonları

- Türkçe karakter içeren kullanıcıya dönük metin **bulunamadı**. Audit’te geçen "Ara" etiketleri ilgili şablonlarda zaten "Search" olarak güncellenmiş.

---

## 4. Dokümantasyon (MD dosyaları)

### TURKISH_TO_ENGLISH_AUDIT.md
- Bu dosyanın kendisi Türkçe–İngilizce çeviri listesi; isterseniz tamamen İngilizce bir "Turkish to English audit" dokümanına dönüştürülebilir.

### START_PROJECT.md
- İçerik zaten İngilizce. Sadece yol örneklerinde geçen `REPOSITORıES` (Türkçe "ı") bir klasör adı; değiştirmeniz gerekmez.

### test/ altındaki README.md dosyaları
- **test/README.md**, **test/orders/README.md**, **test/login/README.md**, **test/leads/README.md**, **test/forget_password/README.md**, **test/organisors/README.md**, **test/signup/README.md**  
- Bu dosyalarda başlık, açıklama ve madde metinleri Türkçe olan tüm cümleler İngilizceye çevrilebilir. Örnekler:
  - "Test Sistemi" → "Test System"
  - "Klasör Yapısı" → "Folder Structure"
  - "Test Çalıştırma" → "Running Tests"
  - "Çalışan testler" / "Çalışmayan testler" → "Working tests" / "Broken tests"
  - "Şifre sıfırlama testleri" → "Password reset tests"
  - "Sipariş testleri" → "Order tests"
  - "Ürün ve stok testleri" → "Product and stock tests"
  - "Kayıt testleri" → "Signup tests"
  - Ve benzeri tüm ifadeler.

### test/logout/TEST_RESULTS.md ve test/logout/SUMMARY.md
- TEST_RESULTS.md tamamen Türkçe açıklamalıysa (başlıklar, test isimleri, kategoriler) hepsi İngilizceye çevrilebilir. SUMMARY.md zaten İngilizce olabilir; kontrol edip kalan Türkçe varsa çevrilebilir.

---

## 5. Özet tablo (migrations hariç)

| Kategori              | Dosya sayısı (yaklaşık) | Öncelik        |
|-----------------------|--------------------------|----------------|
| Test dosyaları (Py)   | 8                        | Orta (isteğe bağlı) |
| Dokümantasyon (MD)    | 10+                      | Orta           |
| HTML şablonları      | 0 (Türkçe yok)           | —              |
| Uygulama kodu (Py)    | 0 (Türkçe yok)           | —              |

---

## 6. Migration’lar hakkında

**Migration dosyaları bilerek dahil edilmedi.**  
`activity_log/migrations/0001_initial.py`, `tasks/migrations/0001_initial.py`, `leads/migrations/0020_user_age_user_gender.py` gibi dosyalarda Türkçe `verbose_name` veya choice metinleri olabilir. Bunları değiştirirseniz yeni migration üretir veya veritabanı uyumluluğunu etkileyebilir. Sadece **yeni** modeller/alanlar için İngilizce kullanın; mevcut migration’ları olduğu gibi bırakın.

---

Bu liste, projede migration’lar hariç tüm Türkçe kısımları tek yerde toplar. Çevirileri yaptıkça ilgili satırları kendi notlarınızla işaretleyebilir veya bu dosyayı güncelleyebilirsiniz.
