# Turkish Content Locations (Migrations Excluded) – Translation Complete

This file listed all Turkish text in the project (excluding migration files) for translation to English.

**Translation completed:** All Turkish comments, docstrings, help text, and user-facing strings in the following have been translated to English (migrations were not modified):

- **test/logout/** – test_logout_integration.py, test_logout_views.py  
- **test/login/** – test_login_views.py, test_login_forms.py, test_login_integration.py  
- **test/leads/** – test_views.py  
- **test/finance/working_tests/** – test_views.py, test_models.py, test_forms.py, test_integration.py  
- **test/orders/working_tests/** – test_views.py, test_integration.py  
- **test/organisors/working_tests/** – test_forms.py, test_mixins.py  
- **test/agents/working_tests/** – test_forms.py  
- **test/signup/working/** – test_signup_models.py  
- **test/products_and_stock/** – broken_tests (test_forms.py, test_views.py), working_tests (test_integration.py)  
- **ProductsAndStock/management/commands/** – update_products_for_dashboard.py  

**Note:** Test data such as `pässwörd123!` and `tëstüsér` (used for password/Unicode tests) were left unchanged. Migration files under `**/migrations/*.py` were intentionally not modified.
