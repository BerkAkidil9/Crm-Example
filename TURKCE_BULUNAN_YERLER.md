# All Turkish Content in the Project (Excluding Migrations)

This is the list of Turkish texts scanned **excluding** migration files. Use as a reference for translation.

---

## 1. Application code (Python)

### 1.1 `ProductsAndStock/views.py`
| Line | Turkish | Suggested English | Status |
|------|---------|-------------------|--------|
| 531 | (comment) | `# Recent Alerts: by severity high to low (CRITICAL -> HIGH -> MEDIUM -> LOW), then by newest date` | ✅ Already English |
| 546 | `# Stock Recommendations: sadece sorun hala gecerliyse goster, urun basina tek oneri (en onemli)` | `# Stock Recommendations: show only if issue still valid, one recommendation per product (most important)` | ✅ Translated |
| 547 | `# Ayni urunde hem DISCOUNT hem REDUCE_STOCK olmasin; confidence_score ile sirali, urun basina ilk gelen` | `# Do not show both DISCOUNT and REDUCE_STOCK for same product; ordered by confidence_score, first per product` | ✅ Translated |

---

## 2. Test files (Python)

### 2.1 `test/products_and_stock/working_tests/test_integration_broken.py`
| Line | Turkish | Suggested English | Status |
|------|---------|-------------------|--------|
| 293 | `# %20 indirim + 10 TL indirim` | `# 20% discount + 10 TL discount` | ✅ Translated |
| 308 | `# Aktif tarihli indirim` | `# Discount with active date range` | ✅ Already English (in file) |
| 313 | `# Aktif tarihli indirim` | `# Discount with active date range` | ✅ Already English (in file) |

### 2.2 `test/products_and_stock/working_tests/test_forms.py`
| Line | Turkish | Suggested English | Status |
|------|---------|-------------------|--------|
| 574 | `# Subcategory queryset'ini manuel olarak ayarla (AJAX olmadan)` | `# Set subcategory queryset manually (without AJAX)` | ✅ Already English |

### 2.3 `test/products_and_stock/broken_tests/test_forms.py`
| Line | Turkish | Suggested English | Status |
|------|---------|-------------------|--------|
| 574 | Same comment | `# Set subcategory queryset manually (without AJAX)` | ✅ Already English |

### 2.4 `test/finance/working_tests/test_integration.py`
| Line | Turkish | Suggested English | Status |
|------|---------|-------------------|--------|
| 267 | `# creation_date manuel set et` | `# set creation_date manually` | ✅ Translated |

---

## 3. Do not change

- **Test data (Unicode):** `test/login/working/test_login_forms.py` → `'tëstüsér'`; `test/forget_password/test_forget_password_forms.py` → `'pässwörd123!'` — These are not Turkish; they are special-character test data; do not translate.
- **Migration files:** All Turkish `verbose_name` and choice texts in `activity_log/migrations/`, `tasks/migrations/`, `leads/migrations/` — Do not modify.

---

## 4. Summary – Translation status

All listed Turkish phrases have been translated to English (excluding migrations and test data).

| File | Line | Status |
|------|------|--------|
| `ProductsAndStock/views.py` | 546, 547 | ✅ Translated |
| `test/products_and_stock/working_tests/test_integration_broken.py` | 293 | ✅ Translated |
| `test/finance/working_tests/test_integration.py` | 267 | ✅ Translated |

**Total: 4 phrases, 3 files — all in English.**
