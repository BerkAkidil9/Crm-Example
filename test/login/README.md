# Login Test System

This folder contains all test files related to login.

## 📁 Folder Structure

```
test/login/
├── __init__.py
├── README.md
├── test_runner.py
├── working/
│   ├── __init__.py
│   ├── test_login_views.py
│   ├── test_login_forms.py
│   ├── test_login_authentication.py
│   └── test_login_integration.py
└── broken_tests/
    ├── __init__.py
    └── test_login_views.py
```

## 🚀 Running Tests

### ✅ Working Tests
```bash
# Login view tests
python manage.py test test.login.working.test_login_views

# Login form tests
python manage.py test test.login.working.test_login_forms

# Authentication backend tests
python manage.py test test.login.working.test_login_authentication

# Login integration tests
python manage.py test test.login.working.test_login_integration

# All login tests
python manage.py test test.login.working
```

## 📊 Test Coverage

### Views (1 view)
- ✅ CustomLoginView (to be tested)

### Forms (1 form)
- ✅ CustomAuthenticationForm (to be tested)

### Authentication Backend (1 backend)
- ✅ EmailOrUsernameModelBackend (to be tested)

### Integration Tests
- ✅ Complete login flow (to be tested)
- ✅ Email verification requirement (to be tested)
- ✅ Redirect behavior (to be tested)

## 🔧 Test Features

### Login View Tests
- GET request test
- POST request with valid data test
- POST request with invalid data test
- Template usage test
- Form class test
- Redirect test

### Login Form Tests
- Form initialization test
- Valid data test
- Invalid data test
- Widget properties test
- Error messages test

### Authentication Backend Tests
- Login with username test
- Login with email test
- Invalid credentials test
- Unverified email user test
- User can authenticate test

### Integration Tests
- Full login flow test
- Email verification requirement test
- Redirect behavior test
- Session management test

## 📝 Notes

- Tests use Django TestCase
- Each test runs independently
- Test database is created and torn down automatically
- Mock used for email sending
- Factory pattern used for test data creation
