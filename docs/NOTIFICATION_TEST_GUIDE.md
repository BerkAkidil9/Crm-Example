# Bildirim Test Rehberi

Notification'ların çalışıp çalışmadığını test etmek için hangi adımları izleyeceğiniz burada.

---

## 1. Anında tetiklenen bildirimler (uygulama içi aksiyon)

| Bildirim | Nasıl test edilir |
|----------|-------------------|
| **Yeni görev atandı** | Tasks → Create Task → Bir kullanıcıya atayın (kendiniz hariç). O kullanıcıyla giriş yapıp `/tasks/notifications/` bakın. |
| **Görev başka kullanıcıya atandı** | Bir görevi düzenleyip "Assigned To"yu başka kullanıcı yapın. Yeni atanan kullanıcının bildirim listesinde görünmeli. |
| **Sipariş oluşturuldu** | Orders → Create Order. Organizatör + (sipariş lead'e bağlıysa) agent bildirim alır. |
| **Stok uyarısı** | ProductsAndStock'ta stok uyarısı tetikleyecek bir durum oluşturun (örn. minimum stok altına düşen ürün). Organizatör bildirim alır. |
| **Lead'e agent atandı** | Leads → bir lead seç → Assign Agent. Atanan agent bildirim alır. |

---

## 2. Management command ile tetiklenen bildirimler

Bu komutlar **otomatik çalışmıyor**; test için terminalde elle çalıştırın.

### Görev bitiş tarihi (1 veya 3 gün kala)

- **Komut:** `python manage.py check_task_deadlines`
- **Ne yapar:** Bitiş tarihi **yarın** veya **3 gün sonra** olan, henüz tamamlanmamış (pending/in_progress) görevler için atanan kullanıcıya e-posta + bildirim oluşturur.
- **Test için:**
  1. Admin'den bir görev oluşturun; **end_date** = yarının tarihi veya 3 gün sonrası, status = pending veya in_progress.
  2. Terminalde: `python manage.py check_task_deadlines`
  3. Atanan kullanıcının e-postası ve `/tasks/notifications/` listesi kontrol.
- **Sadece listele, gönderme:** `python manage.py check_task_deadlines --dry-run`
- **Farklı günler (örn. 2 ve 5 gün):** `python manage.py check_task_deadlines --days 2 5`

### Sipariş günü bugün (sale completed)

- **Komut:** `python manage.py check_order_day`
- **Ne yapar:** `order_day` (teslim/tamamlanma tarihi) **bugün** olan, iptal edilmemiş siparişler için organisor + agent'a bildirim.
- **Test için:**
  1. Bir siparişin `order_day` alanını bugünün tarihi yapın (admin veya DB).
  2. `python manage.py check_order_day`
  3. İlgili organisor ve agent bildirim listesine baksın.
- **Sadece listele:** `python manage.py check_order_day --dry-run`

### Lead 30 gündür sipariş vermedi

- **Komut:** `python manage.py check_lead_no_order`
- **Ne yapar:** Agent'ı olan lead'lerden son 30 günde sipariş vermeyenler için agent'a bildirim.
- **Test için:**
  1. Bir lead'e agent atayın; o lead'in son siparişi 30 günden eski olsun (veya hiç siparişi olmasın ve lead 30 günden eski eklenmiş olsun).
  2. `python manage.py check_lead_no_order`
  3. Agent kullanıcısının bildirim listesine bakın.
- **Sadece listele:** `python manage.py check_lead_no_order --dry-run`

---

## Hızlı kontrol

- Bildirim listesi (giriş yapmış kullanıcı): **`/tasks/notifications/`**
- Okunmamış sayısı navbar'da gösteriliyor (context_processors ile).

Test ederken farklı kullanıcılarla (organisor, agent, atanan user) giriş yapıp her rolün kendi bildirimlerini kontrol edebilirsiniz.
