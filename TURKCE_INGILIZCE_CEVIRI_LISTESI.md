# Turkish Content in the Project (Excluding Migrations) – English Translation List

This file lists all Turkish text in the project **excluding migration files**. Use this list when translating to English.

---

## 1. Application code (Python)

### 1.1 `ProductsAndStock/views.py`
| Line | Turkish | Suggested English | Status |
|------|---------|-------------------|--------|
| 229 | `# Update'de organisation zaten mevcut` | `# Organisation already set on update` | ✅ Translated |

### 1.2 `ProductsAndStock/admin.py`
| Line | Turkish | Suggested English | Status |
|------|---------|-------------------|--------|
| 11 | `# Organisor olan ve en az bir urunu olan UserProfile'lar (admin'de urun olan tum org'lar)` | `# UserProfiles that are organisors and have at least one product (all orgs with products in admin)` | ✅ Translated |

*(Comments in views.py lines 532–547 are already in English.)*

---

## 2. Test files (Python – comments)

### 2.1 `test/finance/working_tests/test_integration.py`
| Line | Turkish | Suggested English | Status |
|------|---------|-------------------|--------|
| 284 | `"""Finance report organizasyon filtreleme"""` | `"""Finance report organisation filtering"""` | ✅ Translated |
| 433 | `# Kar hesaplama` | `# Profit calculation` | ✅ Translated |
| 633 | `"""FinancialReportView form entegrasyonu"""` | `"""FinancialReportView form integration"""` | ✅ Translated |
| 638 | `# GET request - form render edilmeli` | `# GET request - form should be rendered` | ✅ Translated |

### 2.2 `test/products_and_stock/working_tests/test_integration_broken.py`
| Line | Turkish | Suggested English | Status |
|------|---------|-------------------|--------|
| 293 | `# 20% discount + 10 TL discount` | `# 20% discount + 10 currency units discount` | ✅ Translated |
| 338 | `# Toplam kar` | `# Total profit` | ✅ Translated |

### 2.3 `test/products_and_stock/working_tests/test_integration.py`
| Line | Turkish | Suggested English | Status |
|------|---------|-------------------|--------|
| 338 | `# Toplam kar` | `# Total profit` | ✅ Translated |

### 2.4 `test/products_and_stock/working_tests/test_forms.py`
| Line | Turkish | Suggested English | Status |
|------|---------|-------------------|--------|
| 574 | (already English) | `# Set subcategory queryset manually (without AJAX)` | ✅ Already English |

### 2.5 `test/products_and_stock/broken_tests/test_views.py`
| Line | Turkish | Suggested English | Status |
|------|---------|-------------------|--------|
| 398 | `# Negatif fiyat` | `# Negative price` | ✅ Translated |

### 2.6 `test/orders/working_tests/test_integration.py`
| Line | Turkish | Suggested English | Status |
|------|---------|-------------------|--------|
| 592 | `# Toplam fiyat hesapla` | `# Calculate total price` | ✅ Translated |

---

## 3. Do not change (test data)

The following are **not Turkish**; they are Unicode/special-character test data — **do not translate**:

| File | Content | Description |
|------|----------|-------------|
| `test/login/working/test_login_forms.py` | `'username': 'tëstüsér'` | Special character test |
| `test/forget_password/test_forget_password_forms.py` | `'pässwörd123!'` | Unicode password test |

---

## 4. Migration files (do not modify)

The following migration files contain Turkish `verbose_name` and choice text; **do not change them**. Changing them would create new migrations or cause database incompatibility:

- `activity_log/migrations/0001_initial.py` – Action, Object type, Object summary, Date, User, Activity log, etc.
- `activity_log/migrations/0002_add_affected_agent.py` – (Object type etc. may be in English; check)
- `tasks/migrations/0001_initial.py` – Title, Content, Start Date, End Date, Pending, In Progress, Completed, Assigned By, Assigned To, Task, Tasks
- `leads/migrations/0020_user_age_user_gender.py` – Male, Female, Other

Use English only for **new** models/fields; leave existing migration files as they are.

---

## 5. Already in English

- **Models (not migrations):** `activity_log/models.py`, `tasks/models.py`, `leads/models.py`, `ProductsAndStock/models.py`, `organisors/models.py` – verbose_name and choices are in English.
- **ProductsAndStock/views.py** lines 532–547: Recent Alerts, Stock Recommendations etc. comments are in English.
- **HTML templates:** Search labels "Search" etc. are in English.
- **Documentation:** `START_PROJECT.md`, `test/README.md` etc. are in English.

---

## Summary – Translation completed

| File | Line | Old (Turkish) | New (English) | Status |
|------|------|---------------|---------------|--------|
| `ProductsAndStock/views.py` | 229 | Update'de organisation zaten mevcut | Organisation already set on update | ✅ |
| `test/finance/working_tests/test_integration.py` | 433 | Kar hesaplama | Profit calculation | ✅ |
| `test/finance/working_tests/test_integration.py` | 638 | form render edilmeli | form should be rendered | ✅ |
| `test/products_and_stock/working_tests/test_integration_broken.py` | 293 | 10 TL discount | 10 currency units discount | ✅ |
| `test/products_and_stock/working_tests/test_integration_broken.py` | 338 | Toplam kar | Total profit | ✅ |
| `test/products_and_stock/working_tests/test_integration.py` | 338 | Toplam kar | Total profit | ✅ |
| `test/products_and_stock/broken_tests/test_views.py` | 398 | Negatif fiyat | Negative price | ✅ |
| `test/orders/working_tests/test_integration.py` | 592 | Toplam fiyat hesapla | Calculate total price | ✅ |
| `ProductsAndStock/admin.py` | 11 | Organisor olan ve en az bir urunu olan... | UserProfiles that are organisors and have at least one product... | ✅ |
| `test/finance/working_tests/test_integration.py` | 284 | Finance report organizasyon filtreleme | Finance report organisation filtering | ✅ |
| `test/finance/working_tests/test_integration.py` | 633 | FinancialReportView form entegrasyonu | FinancialReportView form integration | ✅ |

**Total: 11 phrases, 7 files – all translated to English.** Migrations and test data (tëstüsér, pässwörd123!) were not changed.

---

## Verification (final check)

- **Unicode test data:** `tëstüsér` (test_login_forms.py) and `pässwörd123!` (test_forget_password_forms.py) were **not translated** – left as-is for special character testing.
- **Migration files:** None were modified (activity_log, tasks, leads migrations).
- **Project-wide (last scan):** All .py files were scanned; excluding migrations and unicode, Turkish characters and common Turkish words (organizasyon filtreleme, entegrasyonu, urunu, tum org, etc.) were searched; the remaining 3 phrases (admin.py, test_integration.py x2) were translated. No Turkish remains outside migrations and unicode.
