# Turkish → English Translation Summary (Excluding Migrations)

This file lists all Turkish content in the project **excluding migration files**. Use it as a reference when translating to English.

**Last updated:** February 2025 – Full pass: test/forget_password, test/login (all files + test_runner), test/logout (working), test/leads (test_views, test_integration), test/organisors (test_views, test_forms), test/orders (test_views, test_integration), test/finance (test_integration, test_views), ProductsAndStock management command. Migration files excluded. Some docstrings in test/finance, test/orders, test/products_and_stock, test/signup, test/agents may still use "test" suffix; replace with "test" if desired.

---

## 1. HTML Templates (UI text)

| File | Original (Turkish) | Suggested English | Status |
|-------|---------------------|---------------------|--------|
| `organisors/templates/organisors/organisor_list.html` | Search (label) | `Search` | ✅ Already English |
| `agents/templates/agents/agent_list.html` | Search (label) | `Search` | ✅ Already English |
| `leads/templates/leads/lead_list.html` | Search (label) | `Search` | ✅ Already English |

---

## 2. Python – Application code (comments / messages)

| File | Line | Original (Turkish) | Suggested English | Status |
|-------|-------|---------------------|---------------------|--------|
| `ProductsAndStock/views.py` | 567-568 | Turkish comments | Already in English in current codebase | Done |

---

## 3. Documentation (MD files)

### 3.1 `START_PROJECT.md` (was fully Turkish, now translated)
- **Title:** → "Django CRM Project Startup Guide"
- → "Required Commands to Start the Project from Scratch"
- → "Open Terminal/PowerShell and go to the project folder"
- → "Start the Django server"
- → "Go to the following address in your browser"
- → "Alternative Commands (If the above does not work)"
- → "If Python module is not found"
- → "First install the required packages"
- → "Then start the server"
- → "If the port is in use"
- → "Stop running Python processes"
- → "Start with Single Command (Recommended)"
- → "Note:"
- → "To stop the server, press..."
- → "The project will run at..."
- → "If you get an error..."

### 3.2 `test/README.md`
- → "Test System"
- → "This folder contains organized test files for all modules."
- → "Folder Structure"
- → "Agent tests"
- → "Finance tests"
- → "Password reset tests"
- → "Lead tests"
- → "Login tests"
- → "Working tests" / "Broken tests"
- → "Logout tests"
- → "Order tests"
- → "Organisor tests"
- → "Product and stock tests"
- → "Signup tests"
- → "Running Tests"
- → "NEW!"
- → "All logout tests (33 tests - 100% success!)"
- → "Interactive test runner"
- → "Other Module Tests"
- And all other sentences in the file (now in English).

### 3.3 `test/orders/README.md`
- → "This folder contains organized test files for the Orders module."
- → "Folder Structure"
- → "Working tests"
- → "Running Tests"
- → "Test Coverage"
- → "Custom Test Features"
- → "Stock restoration tests"
- → "Insufficient stock check tests"
- → "Stock movement record tests"
- → "Test Statistics"
- → "Total Test Count"
- And other phrases (now in English).

### 3.4 `test/login/README.md`
- → "This folder contains all test files related to login."
- → "Folder Structure"
- → "Running Tests"
- → "Working Tests"
- → "Test Coverage"
- → "Test Features"
- → "Valid data test" / "Invalid data test"
- → "Login with username test"
- → "Login with email test"
- And all other text (now in English).

### 3.5 `test/leads/README.md`
- → "This folder contains organized test files for the Leads module."
- → "Test runner"
- → "From command line"
- → "All tests"
- → "Quick tests"
- → "Show test coverage"
- → "Test Types"
- → "Model creation and saving"
- → "Form initialization and field check"
- → "Form validation (valid/invalid data)"
- → "Test Data Management"
- → "If Test Fails"
- → "Common Issues"
- → "Future Plans"
- And other phrases in the file (now in English).

### 3.6 `test/forget_password/README.md`
- → "This folder contains organized test files for the forget password module."
- → "Test runner"
- → "Run All Tests"
- → "Run Specific Test Files"
- → "Run Specific Test Classes"
- → "Run Specific Test Methods"
- → "Test Coverage"
- → "POST test with valid email"
- → "Password mismatch test"
- → "Weak password test"
- And all other text (now in English).

### 3.7 `test/logout/TEST_RESULTS.md`
- Fully described in English (headings, test names, categories, suggestions, lessons learned, etc.). All of this text can be in English.

### 3.8 `test/logout/SUMMARY.md` (formerly OZET.md)
- File renamed to SUMMARY.md; content was already in English.

### 3.9 `test/organisors/README.md`
- Any Turkish parts translated similarly to "Test Coverage", "Running Tests", etc.

### 3.10 `test/signup/README.md`
- Any Turkish parts translated to English using the same terminology.

---

## 4. Python – Test files (Turkish docstrings / comments)

### Translated in this session (Feb 2025)
- **test/orders/working_tests/test_views.py** – All docstrings and comments → English
- **test/orders/working_tests/test_forms.py** – All docstrings and comments → English
- **test/agents/test_runner.py** – Full file (menu, messages, docstrings) → English
- **test/logout/test_runner.py** – Full file → English
- **test/forget_password/test_runner.py** – Full file → English

### Still containing Turkish (optional to translate)
| Location | Note |
|----------|------|
| `test/leads/test_forms.py` | Many Turkish docstrings and comments |
| `test/leads/test_models.py`, `test_views.py` | Some Turkish docstrings |
| `test/products_and_stock/working_tests/` | test_forms, test_integration, simple_test, __init__.py |
| `test/products_and_stock/test_runner.py` | Menu and messages |
| `test/products_and_stock/broken_tests/` | test_forms, test_views, test_views_simple |
| `test/forget_password/test_forget_password_forms.py` | Docstrings (e.g. "Form password mismatch test"), comments |
| `test/forget_password/test_forget_password_views.py` | Docstrings and comments |
| `test/login/working/` | test_login_views, test_login_integration, test_login_authentication – comments/docstrings |
| `test/logout/working/` | test_logout_views, test_logout_integration – docstrings and comments |

Example translations (for reference):
- "Set up test data"
- "Form initialization test"
- "Load Django settings"
- "Authenticated user"
- "Exit" (menu label)

---

## 5. Summary table (excluding migrations)

| Category | Approx. file count | Priority |
|----------|--------------------------|---------|
| HTML (UI) | 3 | High (user-facing) |
| Python app (comment) | 1 (`ProductsAndStock/views.py`) | Medium |
| Documentation (MD) | 10+ | Medium |
| Test files (docstring/comment) | 9+ | Low (optional) |

---

## 6. About migrations

**Migrations are excluded from translation.**  
Files such as `activity_log/migrations/0001_initial.py`, `tasks/migrations/0001_initial.py` may contain Turkish `verbose_name` and choice texts. Changing these would generate new migrations or risk database incompatibility; use English only for **new** models/fields. Leave existing migration files untouched.

---

## 7. Completed translations (February 2025)

The following have been translated to English (migrations left unchanged as per section 6):

- **Application code:** `ProductsAndStock/forms.py` (comments)
- **Test runners:** `test/finance/test_runner.py`, `test/orders/test_runner.py`, `test/leads/test_runner.py`, **test/agents/test_runner.py**, **test/logout/test_runner.py**, **test/forget_password/test_runner.py** (all Turkish strings)
- **Orders tests:** `test/orders/working_tests/test_models.py`, `test_integration.py`, **test_views.py**, **test_forms.py** (docstrings and comments – full translation in this session)
- **Finance tests:** `test/finance/working_tests/test_models.py`, `test_integration.py`, `test_forms.py` (docstrings and comments)
- **Organisors tests:** `test/organisors/working_tests/test_integration.py` (one comment)

**Remaining (optional):** test/leads (test_forms, test_models, test_views), test/login/working, test/logout/working, test/products_and_stock (broken_tests), test/signup – may still contain Turkish docstrings/comments.

---

## 8. Latest translation pass (February 2025 – full pass)

The following were translated to English in this session (migrations left unchanged):

- **Application code:** `ProductsAndStock/forms.py` (comment), `leads/management/commands/create_default_categories.py` (comments), `agents/mixins.py` (comments).
- **Test init:** `test/__init__.py`, `test/forget_password/__init__.py`.
- **Forget password tests:** `test/forget_password/test_forget_password_forms.py`, `test/forget_password/test_forget_password_views.py` (all docstrings and comments).
- **Orders tests:** `test/orders/working_tests/test_forms.py`, `test/orders/working_tests/test_views.py` (remaining Turkish comments).
- **Finance tests:** `test/finance/working_tests/test_forms.py` (docstrings: suffix normalized to "test" / "tests").
- **Organisors tests:** `test/organisors/working_tests/test_views.py` (one comment).
- **Agents tests:** `test/agents/working_tests/test_mixins.py` (one comment).

**Still containing Turkish (optional to translate):**  
`test/login/working/*` (4 files), `test/logout/working/*` (2 files), `test/products_and_stock/broken_tests/test_views.py`, `test/products_and_stock/broken_tests/test_forms.py`, `test/login/test_runner.py` – docstrings and comments. Same pattern: replace Turkish docstrings/comments with English equivalents (e.g. "Create test user", "test" → "test").

---

*This report was created via automatic scanning and review. Add any additional Turkish text you notice to this list.*
