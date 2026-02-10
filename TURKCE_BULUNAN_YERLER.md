# All Turkish Content in the Project (Excluding Migrations)

This is the list of Turkish texts scanned **excluding** migration files. Use as a reference for translation.

---

## 1. Application code (Python)

### 1.1 `ProductsAndStock/views.py`
| Line | Original | Suggested English | Status |
|------|----------|-------------------|--------|
| 531 | (comment) | `# Recent Alerts: by severity high to low (CRITICAL -> HIGH -> MEDIUM -> LOW), then by newest date` | ✅ Already English |
| 546 | Stock Recommendations: show only if issue still valid, one recommendation per product (most important) | `# Stock Recommendations: show only if issue still valid, one recommendation per product (most important)` | ✅ Translated |
| 547 | Do not show both DISCOUNT and REDUCE_STOCK for same product; ordered by confidence_score, first per product | `# Do not show both DISCOUNT and REDUCE_STOCK for same product; ordered by confidence_score, first per product` | ✅ Translated |

---

## 2. Test files (Python)

### 2.1 `test/products_and_stock/working_tests/test_integration_broken.py`
| Line | Original | Suggested English | Status |
|------|----------|-------------------|--------|
| 293 | 20% discount + 10 currency units discount | `# 20% discount + 10 currency units discount` | ✅ Translated |
| 308 | Discount with active date range | `# Discount with active date range` | ✅ Already English (in file) |
| 313 | Discount with active date range | `# Discount with active date range` | ✅ Already English (in file) |

### 2.2 `test/products_and_stock/working_tests/test_forms.py`
| Line | Original | Suggested English | Status |
|------|----------|-------------------|--------|
| 574 | Set subcategory queryset manually (without AJAX) | `# Set subcategory queryset manually (without AJAX)` | ✅ Already English |

### 2.3 `test/products_and_stock/broken_tests/test_forms.py`
| Line | Original | Suggested English | Status |
|------|----------|-------------------|--------|
| 574 | Same comment | `# Set subcategory queryset manually (without AJAX)` | ✅ Already English |

### 2.4 `test/finance/working_tests/test_integration.py`
| Line | Original | Suggested English | Status |
|------|----------|-------------------|--------|
| 267 | Set creation_date manually | `# set creation_date manually` | ✅ Translated |

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
