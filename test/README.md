# Test System

This folder contains organized test files for all modules.

## 📁 Folder Structure

```
test/
├── __init__.py
├── README.md
├── agents/                     # Agent tests
├── finance/                    # Finance tests
├── forget_password/            # Password reset tests
├── leads/                      # Lead tests
├── login/                      # Login tests
│   ├── working/               # ✅ Working tests
│   ├── broken_tests/          # ❌ Broken tests
│   ├── test_runner.py
│   └── README.md
├── logout/                     # 🆕 Logout tests
│   ├── working/               # ✅ Working tests (33 tests)
│   ├── test_runner.py
│   ├── README.md
│   └── TEST_RESULTS.md
├── orders/                     # Order tests
├── organisors/                 # Organisor tests
├── products_and_stock/         # Product and stock tests
└── signup/                     # Signup tests
```

## 🚀 Running Tests

### 🆕 Logout Tests (NEW!)
```bash
# All logout tests (33 tests - 100% success!)
python manage.py test test.logout.working

# Logout view tests
python manage.py test test.logout.working.test_logout_views

# Logout integration tests
python manage.py test test.logout.working.test_logout_integration

# Interactive test runner
python test/logout/test_runner.py
```

### Login Tests
```bash
# All login tests
python manage.py test test.login.working

# Login view tests
python manage.py test test.login.working.test_login_views

# Login authentication tests
python manage.py test test.login.working.test_login_authentication
```

### Signup Tests
```bash
# All signup tests
python manage.py test test.signup.working
```

### Other Module Tests
```bash
# Agents tests
python manage.py test test.agents.working_tests

# Finance tests
python manage.py test test.finance.working_tests

# Orders tests
python manage.py test test.orders.working_tests

# Organisors tests
python manage.py test test.organisors.working_tests

# Products and Stock tests
python manage.py test test.products_and_stock.working_tests
```

## 📊 Test Status

### 🆕 Logout Tests (NEW!)
- **Status:** ✅ 33/33 tests passing (100%)
- **Coverage:** Views, integration, security, performance
- **Duration:** ~19 seconds
- **Files:** 
  - `test_logout_views.py` (19 tests)
  - `test_logout_integration.py` (14 tests)

### Login Tests
- **Status:** ✅ Working tests available
- **Coverage:** Views, forms, authentication, integration
- **Files:** 4 test files

### Signup Tests
- **Status:** ✅ Working tests available
- **Coverage:** Views, forms, models, integration
- **Files:** 4 test files

### Agents Tests
- **Status:** ✅ Working tests available
- **Coverage:** Views, forms, models, mixins, integration
- **Files:** 6 test files

### Finance Tests
- **Status:** ✅ Working tests available
- **Coverage:** Views, forms, models, integration
- **Files:** 4 test files

### Orders Tests
- **Status:** ✅ Working tests available
- **Coverage:** Views, forms, models, integration
- **Files:** 4 test files

### Organisors Tests
- **Status:** ✅ Working tests available
- **Coverage:** Views, forms, models, mixins, integration
- **Files:** 5 test files

### Products and Stock Tests
- **Status:** ⚠️ Partially passing (working_tests + broken_tests)
- **Working:** 5 tests
- **Issues:** 80+ tests
- **Issues:** UserProfile unique constraint, form validations

## 🎯 Overall Test Coverage

### Authentication & Authorization
- ✅ Login (multiple test files)
- ✅ **Logout (33 tests - NEW!)**
- ✅ Signup (multiple test files)
- ✅ Forget Password (test files)
- ✅ Email Verification (covered in login tests)

### Core Modules
- ✅ Leads (5 test files)
- ✅ Agents (6 test files)
- ✅ Organisors (5 test files)
- ✅ Orders (4 test files)
- ✅ Finance (4 test files)
- ⚠️ Products and Stock (partial)

### Test Types
- ✅ View tests
- ✅ Form tests
- ✅ Model tests
- ✅ Authentication backend tests
- ✅ Integration tests
- ✅ Security tests
- ✅ Performance tests
- ✅ Mixin tests

## 🆕 Recent Additions

### Logout Test System (October 12, 2025)
- 🎉 **33 tests** added successfully
- ✅ 100% test pass rate
- 📁 Organized folder structure
- 📖 Detailed documentation
- 🏃 Interactive test runner
- 🔒 Comprehensive security tests
- ⚡ Performance tests
- 🔗 Integration tests

### Features
- Django LogoutView tests
- Session management tests
- CSRF protection tests
- Session hijacking protection
- Session fixation protection
- Token invalidation tests
- Multi-session management
- Different user types (organizer, agent, superuser)
- Edge case scenarios

## 🎯 Future Plans

1. ✅ **Logout tests added** (COMPLETED!)
2. **Test extensions for other modules**
3. **Add test coverage report**
4. **CI/CD integration**
5. **Performance benchmark tests**

## 📝 Notes

- Tests use Django TestCase
- Each test runs independently
- Test database is created and torn down automatically
- Mock used for email sending
- Factory pattern used for test data creation
