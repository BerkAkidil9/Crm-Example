# CRM repository için kanıta dayalı CV metrik analizi

Bu belge, Full-Stack veya Backend Software Engineer CV'sinde kullanılabilecek repository bulgularını, ölçüm sınırlarını ve İngilizce bullet önerilerini saklar. En güçlü kanıtlar 8 Django uygulaması, 3 operasyonel rol, organizasyon kapsamlı erişim, sipariş–stok otomasyonu ve izole yerel çalıştırmada geçen 1.197 testtir. Aynı çalıştırmada %79,14 satır ve %61,39 branch kapsamı ölçülmüştür. Üretim etkisi veya performans iyileşmesi yüzdesi doğrulanmamıştır.

| Bilgi | Değer |
|---|---|
| İnceleme ve ölçüm tarihi | 30 Eylül 2026 |
| İncelenen commit | `20d197814e6491b0360f941e994d8be114b0bafd` |
| Commit tarihi | 29 Temmuz 2026 |
| Hedef | Full-Stack / Backend Software Engineer CV'si |
| Kanıt arşivi | [cv-evidence/2026-09-30](cv-evidence/2026-09-30/) |
| Değişiklik sınırı | Analiz sırasında kaynak kod, testler ve deployment yapılandırması değiştirilmedi |

Bu bir tarihli ölçüm kaydıdır. Yeni commit'lerde metrikleri otomatik olarak geçerli kabul etmeyin. Kaynak bağlantıları repository içindeki dosyalara gider; belirtilen satırlar incelenen commit'e aittir. Arşivdeki mutlak dosya yolları ve geçici dizinler ölçümün tarihsel kaydı olarak korunmuştur. Belgedeki göreli kanıt bağlantıları `/private/tmp` dizinine bağımlı değildir.

## A Yeni ölçülen sonuçlar

| Metric | Değer | Ne ifade ediyor | Repository veya ölçüm kanıtı | Impact/Scope | CV değeri | Neden |
|---|---|---|---|---|---|---|
| Test tanımı ve keşfi | 1.197 tanım; 1.197 keşfedilen test; 50 test dosyası | AST sayımı Django keşfiyle örtüşüyor | [Envanter](cv-evidence/2026-09-30/inventory.json), [keşif listesi](cv-evidence/2026-09-30/discovery.json) | Test kapsamının büyüklüğü | Orta | Sayı tek başına test kalitesini göstermiyor |
| Test sonucu | 1.197 çalıştırılan ve başarılı; 0 failure, 0 error, 0 skip | Mevcut test paketi izole ortamda tamamlandı | [Sonuçlar](cv-evidence/2026-09-30/results.json), [tam log](cv-evidence/2026-09-30/test.log) | Ölçülmüş doğrulama | Yüksek | Başarı, statik sayımdan bağımsız doğrulandı |
| Satır kapsamı | %79,14; 3.874 / 4.895 çalıştırılabilir satır | Kapsamdaki Python kodunun çalıştırılan kısmı | [Coverage JSON](cv-evidence/2026-09-30/coverage.json) | Ölçülmüş test kapsamı | Yüksek | Payda ve kapsam açık |
| Branch kapsamı | %61,39; 846 / 1.378 dal | Koşullu yürütme yollarının çalıştırılan kısmı | [Coverage JSON](cv-evidence/2026-09-30/coverage.json) | Ölçülmüş test kapsamı | Yüksek | Satır kapsamının göstermediği eksikleri gösteriyor |
| Yerel süre kontrolleri | 4 performans testi ve 1 zamanlama farkı testi geçti | Testlerdeki süre eşikleri bu çalıştırmada sağlandı | [Sonuç özeti](cv-evidence/2026-09-30/summary.json) | Yerel eşik doğrulaması | Düşük | Üretim benchmark'ı veya iyileşme ölçümü değil |

### Ölçüm ortamı ve kapsamı

- Python **3.12.14**, Django **5.0.7**, coverage.py **7.16.2**, SQLite **3.53.1**, macOS ARM64 kullanıldı. [Ortam kaydı](cv-evidence/2026-09-30/environment.json).
- Deployment dosyası Python **3.12.3** tanımlar. Ölçüm aynı minor sürümün mevcut patch sürümüyle yapıldı; deployment ortamıyla birebir aynı değildir. Kaynak: [render.yaml](../render.yaml), satır 15–16.
- Bağımlılıklar [requirements.txt](../requirements.txt) üzerinden kuruldu. Sabitlenmemiş bağımlılıkların o gün çözümlenen sürümleri [dependencies.txt](cv-evidence/2026-09-30/dependencies.txt) içinde saklandı.
- Bellek içi SQLite, yerel bellek e-posta backend'i ve geçici medya dizini kullanıldı. Gerçek Gmail, Cloudflare R2 ve üretim veritabanına bağlanılmadı. [Geçici ayarlar](cv-evidence/2026-09-30/original-harness/audit_settings.py).
- Parola hash ayarları değiştirilmedi. `DEBUG=True` ile yüklenen ayarlar ve projenin kendi test modu kullanıldı. Test modu rate limiting'i kapatır; dolayısıyla bu çalıştırma rate-limit veya üretim HTTPS davranışını doğrulamaz. Kaynak: [settings.py](../djcrm/settings.py), satır 176–184 ve 366–380.
- Coverage kapsamı **8 yerel uygulama ve `djcrm` paketindeki 86 Python dosyasıdır**. Testler, migration'lar ve üçüncü taraf kodu hariç; yönetim komutları ve proje yapılandırma kodu dahildir. HTML/JavaScript kapsamı ölçülmedi. [Coverage yapılandırması](cv-evidence/2026-09-30/original-harness/coverage.ini).
- Tam test süresi **108,416 saniyedir**. Bu süre uygulama yanıt süresi değildir.

[Standart coverage raporundaki](cv-evidence/2026-09-30/coverage.txt) **%75,24**, satır ve branch sonuçlarının birleşimidir; satır kapsamı diye kullanılmamalıdır. Formüller: satır kapsamı `3874 / 4895 × 100`, branch kapsamı `846 / 1378 × 100`, birleşik kapsam `(3874 + 846) / (4895 + 1378) × 100`.

### Çalıştırma kaydı

Ölçümde kullanılan komut:

```bash
/private/tmp/crm-cv-venv/bin/python -B /private/tmp/crm-cv-audit/run.py \
  > /private/tmp/crm-cv-audit/test.log 2>&1
```

[Ölçüm betiği](cv-evidence/2026-09-30/original-harness/run.py), `test --noinput --verbosity=2 --testrunner=audit_runner.Runner` komutunu coverage altında yürütür. [Runner](cv-evidence/2026-09-30/original-harness/audit_runner.py) test kimliklerini ve sonuçları kaydeder; test beklentilerini değiştirmez.

İlk çalıştırmada geçici betik `test` argümanını global `sys.argv` içine aktarmadığı için projenin testlere özel rate-limit ayarı devreye girmedi. Bu ön çalışma 607 testten sonra durduruldu; 20 failure içeren [ilk log](cv-evidence/2026-09-30/initial-harness-run/test.log) saklandı. Yalnızca ölçüm betiği düzeltildi. A bölümündeki sonuçlar, düzeltmeden sonra tamamlanan tek tam çalıştırmaya aittir; ön çalışma coverage'a veya başarı toplamına katılmadı.

Arşivdeki betikler orijinal çalışma yollarını içerir ve taşınabilir bir test komutu olarak tasarlanmamıştır. Yeniden ölçümde yeni bir geçici ortam kurun, repository/çıktı yollarını ve commit bilgisini uyarlayın, yerel veritabanı/e-posta/medya izolasyonunu koruyun. `.env` dosyası sonradan eklenmişse ayarların ortam değişkenlerini tekrar yüklediğini dikkate alın. Yeni sonucu ayrı tarihli bir dizinde saklayın; bu tarihsel kaydı üzerine yazarak güncellemeyin.

## B Doğrulanmış teknik kapsam

| Metric | Değer | Ne ifade ediyor | Repository kanıtı | Impact/Scope | CV değeri | Neden |
|---|---|---|---|---|---|---|
| İş modülleri | 8 yerel Django uygulaması | İşlevsel CRM kapsamı | [settings.py](../djcrm/settings.py), satır 80–88 | Teknik kapsam | Yüksek | Modüler backend tasarımı |
| Veri modeli | 23 somut model | Uygulamaya ait kayıtlı model sınıfları | [Çalışma zamanı envanteri](cv-evidence/2026-09-30/runtime-inventory.json) | Teknik kapsam | Orta | Veri modelleme büyüklüğü; kullanım ölçeği değil |
| URL desenleri | 60; 46 uygulama ve 14 ortak/proje yolu | Son URL desenleri | [URL envanteri](cv-evidence/2026-09-30/runtime-inventory.json), [ana URL dosyası](../djcrm/urls.py), satır 9–32 | Teknik kapsam | Orta | Web uygulaması kapsamı; REST API sayısı değil |
| Erişim modeli | 3 operasyonel rol | Administrator, Organisor, Agent | [mixins.py](../agents/mixins.py), satır 7–83; [lead filtreleri](../leads/views.py), satır 222–232 | Teknik kapsam | Yüksek | RBAC ve organizasyon kapsamlı erişim |
| Yönetim komutları | 10 implementasyon; bunun 3'ü zamanlanabilir bildirim komutu | Kurulum, bakım, örnek veri, hatırlatmalar | [Dosya ve satır envanteri](cv-evidence/2026-09-30/inventory.json) | Teknik kapsam | Yüksek | İşleviyle birlikte güçlü bir backend kapsamı |
| Cron yapılandırması | Repository'de tanımlı cron servisi 0 | Zamanlama belgelenmiş fakat deployment'a eklenmemiş | [render.yaml](../render.yaml); [README](../README.md), satır 208–231 | Config sınırı | CV metriği değil | Üretimde çalışan zamanlama iddiasını desteklemiyor |
| Harici servisler | Gmail API ve Cloudflare R2 | E-posta backend'i ve medya depolama bağlantısı | [settings.py](../djcrm/settings.py), satır 228–298 ve 307–322; [storage.py](../djcrm/storage.py), satır 10–16 | Entegrasyon kapsamı | Yüksek | Backend entegrasyonu; üretim kullanım kanıtı değil |
| Aktivite kaydı | 6 nesne türü, 21 tanımlı aksiyon | Organisor, agent, product, order, lead ve task kayıtları | [activity_log/models.py](../activity_log/models.py), satır 9–63 | Tanımlı kapsam | Orta | İzlenebilirlik özelliği; gerçekleşen olay sayısı değil |

Model sayımı migration'lardan yapılmadı. AST sayımı Django model registry'siyle doğrulandı; uygulamaya ait somut modeller sayıldı. URL sayımından `include` bağlantıları, otomatik admin yolları ve geliştirme statik/medya yolları çıkarıldı. [Statik envanter](cv-evidence/2026-09-30/inventory.json) dosya/satırları, [çalışma zamanı envanteri](cv-evidence/2026-09-30/runtime-inventory.json) model ve URL isimlerini içerir.

### Modül ve model envanteri

| Uygulama | Somut modeller | URL | Başarılı test |
|---|---|---:|---:|
| `leads` | 8: User, UserProfile, Category, SourceCategory, ValueCategory, Lead, Agent, EmailVerificationToken | 11 | 482 |
| `agents` | 0; Agent modeli `leads` içinde | 5 | 112 |
| `organisors` | 1: Organisor | 5 | 110 |
| `ProductsAndStock` | 8: Category, SubCategory, ProductsAndStock, StockMovement, PriceHistory, SalesStatistics, StockAlert, StockRecommendation | 9 | 164 |
| `orders` | 2: orders, OrderProduct | 6 | 100 |
| `finance` | 1: OrderFinanceReport | 1 | 79 |
| `tasks` | 2: Task, Notification | 8 | 112 |
| `activity_log` | 1: ActivityLog | 1 | 38 |
| Toplam | 23 | 46 uygulama yolu | 1.197 |

Ortak 14 yol bu tablodaki 46'ya eklenir. Test dağılımı [results.json](cv-evidence/2026-09-30/results.json), sayım özeti [counts.json](cv-evidence/2026-09-30/counts.json) içindedir. Aynı adlı Category sınıfları farklı uygulamalara ait ayrı modellerdir.

### İş akışları ve sınırları

**Multi-tenancy ve erişim:** Ortak veritabanında `UserProfile` üzerinden organizasyon ilişkileri ve queryset filtreleri kullanılır. Admin erişimi organizasyonlar arasıdır; lead ve görev erişimi rol/atama kapsamına göre daraltılır. Ayrı tenant veritabanı veya şeması yoktur. Kaynaklar: [leads/models.py](../leads/models.py), satır 37–83; [leads/views.py](../leads/views.py), satır 361–386; [tasks/views.py](../tasks/views.py), satır 16–30. Bu uygulama düzeyindeki kontroller, tüm yollar için eksiksiz izolasyon veya güvenlik denetimi kanıtı sayılmaz.

**Sipariş, stok ve finans:** Sipariş kalemi oluşturma stok düşürür; iptal akışı stok iadesi ve hareket kaydı üretir. Sipariş oluşturma finans raporuna bağlanır. Kaynaklar: [orders/models.py](../orders/models.py), satır 45–122; [orders/views.py](../orders/views.py), satır 283–306. Stok azaltma ve iade testleri: [test_signals.py](../orders/tests/test_signals.py), satır 61–149. Eşzamanlılık güvenliği veya idempotency garantisi doğrulanmadı: stok azaltma Python seviyesinde okuma–değiştirme–kaydetme kullanır; iptal sinyali iptal durumundaki her kayıtta çalışabilir.

**Finans ve arayüz:** Finans ekranı tarih aralığı, sipariş oluşturma/teslim tarihi, organizasyon ve agent filtreleriyle gelir, maliyet ve kâr hesaplar. Django şablonları, Tailwind, Chart.js ve Flatpickr kullanılır. Kaynaklar: [finance/views.py](../finance/views.py), satır 29–71 ve 115–150; [base.html](../templates/base.html), satır 11; [product_charts.html](../ProductsAndStock/templates/ProductsAndStock/product_charts.html), satır 101; [financial_report.html](../finance/templates/finance/financial_report.html), satır 222–232. Bu kapsam tarayıcı veya erişilebilirlik test sonucu değildir.

**Doğrulama ve güvenlik:** Görsel yüklemede MIME, içerik imzası ve 5 MiB sınırı; form bazlı benzersizlik, tarih ve stok kontrolleri bulunur. Login 5 POST/dakika/IP, signup ve password reset 3 POST/dakika/IP olarak tanımlanmıştır. Kaynaklar: [leads/forms.py](../leads/forms.py), satır 13–40; [leads/views.py](../leads/views.py), satır 25, 39 ve 110; [orders/forms.py](../orders/forms.py), satır 18–23 ve 56–63; [tasks/forms.py](../tasks/forms.py), satır 44–49. Bunlar kod/config davranışıdır; saldırı önleme başarısı ölçümü değildir.

### Yönetim komutları

`__init__.py` hariç 13 komut dosyasının 10'u `Command` sınıfı ve `handle` implementasyonu içerir. `clean_duplicate_categories.py`, `final_cleanup.py` ve `force_clean_duplicates.py` yalnızca boşluk içerir; işlevsel sayıya katılmaz. Dosya/satır kanıtı: [inventory.json](cv-evidence/2026-09-30/inventory.json), `commands` alanı.

| Amaç | Komutlar |
|---|---|
| Zamanlanabilir bildirimler | `check_task_deadlines`, `check_order_day`, `check_lead_no_order` |
| Kurulum ve örnek veri | `create_categories`, `create_sample_products`, `update_products_for_dashboard`, `create_default_categories` |
| Bakım | `update_product_descriptions_english`, `reassign_products_to_organisor` |
| Geliştirme ve test verisi | `create_fake_notifications` |

Görev hatırlatmaları varsayılan olarak **1 ve 3 gün öncesi**, sipariş hatırlatması **teslim günü**, lead hatırlatması **30 günlük siparişsizlik** koşullarını işler. Kaynaklar: [check_task_deadlines.py](../tasks/management/commands/check_task_deadlines.py), satır 17–44; [check_order_day.py](../tasks/management/commands/check_order_day.py), satır 24–32; [check_lead_no_order.py](../tasks/management/commands/check_lead_no_order.py), satır 28–52. Bu eşikler iş kurallarıdır; sağlanan zaman tasarrufu değildir. Çalışan üretim cron geçmişi doğrulanmadı.

## C Yanıltıcı veya zayıf CV metrikleri

| İfade veya metrik | Neden kullanılmamalı |
|---|---|
| 60 REST API endpoints | Sayım HTML/form yollarını da içerir. Doğru terim application URL patterns; işlevsel kapsamı anlatmak CV için daha değerlidir. |
| 13 management commands | 3 dosya boş; işlevsel implementasyon sayısı 10. |
| 1.197 tests and 100% coverage | Başarılı test oranı ile coverage farklıdır. Ölçülen oranlar %79,14 satır ve %61,39 branch. |
| %X faster veya %Y less manual work | Önce/sonra ölçümü ve operasyon kaydı yok. |
| Supports 50 users/products | Testteki örnek veri büyüklüğü kullanıcı veya veri kapasitesi değildir. |
| Production responses under 2 seconds | Ürün testi 50 ek ürünle yerel Django client üzerinde liste için <2 s, dashboard için <3 s kontrol eder. Üretim veya tarayıcı ölçümü değildir. |
| AI-powered inventory recommendations | Öneriler eşik kuralları ve sabit confidence değerleriyle üretilir; eğitilmiş model veya doğruluk değerlendirmesi yok. |
| Fully tested veya guaranteed isolation | Coverage eksiksiz değil; ayrıca bazı testlerde koşullu erken çıkışlar bulunur. |
| Dosya veya migration sayısıyla ürün etkisi | Kod hacmi kullanıcı değeri veya güvenilirlik sonucu değildir. |

Performans testlerinin kaynakları: [ürün testi](../ProductsAndStock/tests/test_integration.py), satır 465–500; [login testi](../leads/tests/test_login_integration.py), satır 390–406; [authentication testi](../leads/tests/test_login_authentication.py), satır 456–488; [logout testi](../leads/tests/test_logout_integration.py), satır 252–275. Zamanlama farkı testi aynı [authentication dosyasında](../leads/tests/test_login_authentication.py), satır 225–251'dir. Bu testler geçti; ölçülen tekil süre değerleri loglanmadığından ayrıca bir latency metriği üretilmedi.

Test kalitesi sınırına örnek: [agent lifecycle testi](../agents/tests/test_integration.py), satır 46–50, kullanıcı oluşturulmadığında erken `return` ile başarılı sonuç verebilir. Başarı toplamı bunu bir skip olarak saymaz. Öneri sisteminin kural tabanlı olduğunun kaynağı: [ProductsAndStock/models.py](../ProductsAndStock/models.py), satır 397–429.

## D Mevcut CV bullet içeriklerinin değerlendirilmesi

Orijinal dört bullet analiz konuşmasında paylaşılmadığı için birebir cümle değerlendirmesi yapılmadı. Aşağıdaki tablo, analiz planında belirtilen içerik gruplarına uygulanabilecek düzeltmeleri saklar; orijinal metinlerin alıntısı değildir.

| İçerik grubu | Korunabilecek ifade | İddia sınırı |
|---|---|---|
| Multi-tenancy, organization isolation, RBAC | Multi-tenant Django CRM with organization-scoped access and three user roles | Complete isolation, zero data leakage veya veritabanı seviyesinde izolasyon eklenmemeli |
| Stok otomasyonu ve rol kapsamlı erişim | Sipariş oluşturma/iptalinde stok güncelleme, hareket kaydı, organizasyon ve atama filtreleri | Ölçülmemiş hata azalması, hızlanma ve garantili stok tutarlılığı çıkarılmalı |
| Yönetim komutları, Gmail API ve R2 | 10 komut; bunun içinde 3 zamanlanabilir hatırlatma komutu; Gmail/R2 entegrasyonu | 13 çalışan komut, üretimde çalışan cron veya servis SLA'sı yazılmamalı |
| Django testing | 1.197 başarılı test; %79,14 satır ve %61,39 branch kapsamı | Yerel SQLite sonucu PostgreSQL, tarayıcı E2E veya üretim doğrulaması olarak sunulmamalı |

## E İngilizce CV bullet önerileri

Bu ifadeler repository'nin teknik kapsamını anlatır. Kişisel CV'de katkı fiillerini kendi yaptığınız işle eşleştirin; repository incelemesi tek başına bireysel yazarlığı kanıtlamaz.

1. **Built a multi-tenant Django CRM spanning 8 business modules, with organization-scoped data access and role-based workflows for administrators, organizers, and agents.**

   Dayanak: [settings.py](../djcrm/settings.py), satır 80–88; [agents/mixins.py](../agents/mixins.py), satır 7–83; [leads/views.py](../leads/views.py), satır 222–232.

2. **Implemented signal-driven inventory updates for order creation and cancellation, with stock movement tracking, price history, and threshold-based stock alerts.**

   Dayanak: [orders/models.py](../orders/models.py), satır 97–122; [ProductsAndStock/models.py](../ProductsAndStock/models.py), satır 281–395.

3. **Developed 10 Django management commands for setup, maintenance, and notifications, including 3 schedulable workflows for task deadlines, order delivery dates, and inactive leads.**

   Dayanak: [Komut envanteri](cv-evidence/2026-09-30/inventory.json); [README](../README.md), satır 225–231. “Schedulable” ifadesi üretimde çalıştığı iddiasını içermez.

4. **Integrated Gmail API email delivery and Cloudflare R2 media storage, including an application media proxy with ownership-based access checks.**

   Dayanak: [settings.py](../djcrm/settings.py), satır 228–298 ve 307–322; [storage.py](../djcrm/storage.py), satır 10–16; [views.py](../djcrm/views.py), satır 22–75.

5. **Validated CRM functionality with 1,197 passing Django tests, measuring 79.1% line coverage and 61.4% branch coverage in an isolated SQLite test run.**

   Dayanak: [Test sonuçları](cv-evidence/2026-09-30/results.json), [coverage](cv-evidence/2026-09-30/coverage.json), [ölçüm kapsamı](cv-evidence/2026-09-30/original-harness/coverage.ini).

## F Doğrulanamayan metrikler

- Gerçek kullanıcı/organizasyon sayısı, aktif kullanım, trafik, eşzamanlı kullanıcı kapasitesi ve throughput.
- Üretim p50/p95/p99 gecikmesi, uptime, hata oranı ve yük altında stok tutarlılığı.
- Gelir artışı, iş gücü tasarrufu, dönüşüm oranı veya stok hatalarında azalma.
- Gerçek Gmail teslimatı, R2 üzerinden başarılı üretim yükleme/indirme ve çalışan cron geçmişi. R2 storage dosyası bu yerel ölçümde **%0 coverage** aldı; [coverage.txt](cv-evidence/2026-09-30/coverage.txt).
- PostgreSQL üzerinde test sonucu. Projenin test ayarı veritabanını SQLite'a çevirir; [settings.py](../djcrm/settings.py), satır 176–183.
- Lighthouse, erişilebilirlik denetimi, tarayıcı E2E, frontend bundle/build performansı ve cihaz/tarayıcı uyumluluk matrisi.
- Çok dilli ürün desteği. İngilizce arayüz ayarları ve telefon ülke kodları çok dilli arayüz kanıtı değildir; [settings.py](../djcrm/settings.py), satır 209.
- Deployment sırasında otomatik test/CI güvencesi. Build script bağımlılık kurulumu, statik dosya toplama ve migration içerir; test adımı içermez. [build.sh](../build.sh), satır 7–18.

README ve entegrasyon dokümanları kurulum/kapsam kaynakları olarak kullanıldı; ölçüm raporu sayılmadı. Git geçmişinde README'nin son değişikliği 3 Mart 2026, Gmail/R2 dokümanlarının son değişikliği 25 Şubat 2026'dır. README'nin PostgreSQL varsayılanı anlatımı `.env.example` ile ilişkili olsa da ortam ayarı yokken kod SQLite'a düşer. Çelişen noktalarda mevcut kod esas alındı. Yerel demo SQL dosyası gerçek kullanıcı veya üretim kullanımı kanıtı sayılmadı. Canlı demo üzerinde yük testi yapılmadı.

## Kanıt arşivi ve yeniden kullanım

Arşiv, geçici ortam silinse de raporun doğrulanabilmesi için test sonucu, keşif listesi, coverage JSON/metin çıktısı, bağımlılık sürümleri, ortam bilgisi, envanter ve orijinal ölçüm betiklerini içerir. Sanal ortam, Python kurulumu, testte üretilen medya ve üretilmiş HTML coverage sayfaları kopyalanmadı.

- [summary.json](cv-evidence/2026-09-30/summary.json): Test, uygulama dağılımı, coverage ve süre kontrolü sonuçları.
- [inventory.json](cv-evidence/2026-09-30/inventory.json): Statik model/route/komut/test tanımları, dosya/satırlar ve incelenen kaynak dosyaların SHA-256 değerleri.
- [runtime-inventory.json](cv-evidence/2026-09-30/runtime-inventory.json): Django registry ve URL resolver ile doğrulanan isimler.
- [integrity.json](cv-evidence/2026-09-30/integrity.json): Analiz sonundaki kaynak bütünlüğü kontrolü; incelenen 278 takip edilen dosyada içerik değişikliği yoktu. Bu kontrol, sonradan eklenen bu belge ve arşivden önce yapıldı.
- [sha256.json](cv-evidence/2026-09-30/sha256.json): Arşivlenen 19 kanıt dosyasının içerik özetleri; manifest kendisini kapsamaz.

Sonraki kullanımda önce commit ve çalışma ağacını kontrol edin. Kod değişmişse ilgili sayımları ve tam test/coverage çalıştırmasını yenileyin. Önce/sonra iyileşme iddiası için aynı veri, donanım, ortam, ölçüm yöntemi ve karşılaştırma tabanı gerekir. Yeni bir test başarısını otomatik olarak üretim başarısı veya kullanıcı etkisine dönüştürmeyin.
