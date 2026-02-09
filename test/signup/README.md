# Signup Test System

This folder contains organized test files for the signup (registration) module.

## 📁 Folder Structure

```
test/signup/
├── __init__.py
├── working_tests/              # ✅ Working tests
│   ├── __init__.py
│   ├── test_signup_forms.py    # Form tests
│   ├── test_signup_views.py    # View tests
│   ├── test_signup_models.py   # Model tests
│   └── test_signup_integration.py  # Integration tests
├── test_runner.py              # Interactive test runner
└── README.md                   # This file
```

## 🚀 Running Tests

### ✅ Working Tests

#### Run All Tests
```bash
# Run all signup tests
python test/signup/test_runner.py all

# Or with Django manage.py
python manage.py test test.signup.working_tests
```

#### Run Specific Test Categories
```bash
# Form tests only
python test/signup/test_runner.py forms

# View tests only
python test/signup/test_runner.py views

# Model tests only
python manage.py test test.signup.working_tests.test_signup_models

# Integration tests only
python test/signup/test_runner.py integration
```

#### Interactive Test Runner
```bash
python test/signup/test_runner.py interactive
```

#### Django Test Commands
```bash
# With verbose mode
python manage.py test test.signup.working_tests -v 2

# Run a specific test class
python manage.py test test.signup.working_tests.test_signup_forms.TestCustomUserCreationForm

# Run a specific test method
python manage.py test test.signup.working_tests.test_signup_forms.TestCustomUserCreationForm.test_form_valid_data
```

## 📊 Test Coverage

### 🧪 Form Tests (test_signup_forms.py)
- **File:** `working_tests/test_signup_forms.py`
- **Test Classes:** 3 classes
- **Total Tests:** ~25 tests
- **Coverage:** CustomUserCreationForm, form validations, widget features

#### Tested Features:
- ✅ Form initialization and field presence
- ✅ Form test with valid data
- ✅ Required fields validation
- ✅ Email uniqueness check
- ✅ Phone number uniqueness check
- ✅ Username uniqueness check
- ✅ Password validation
- ✅ Widget features (placeholder, CSS classes)
- ✅ Form save method
- ✅ Clean methods
- ✅ Form integration tests

### 🌐 View Tests (test_signup_views.py)
- **File:** `working_tests/test_signup_views.py`
- **Test Classes:** 6 classes
- **Total Tests:** ~35 tests
- **Coverage:** SignupView, EmailVerificationView, view integrations

#### Tested Features:
- ✅ SignupView GET/POST requests
- ✅ Signup with valid data
- ✅ Signup with invalid data
- ✅ Signup with conflicting data
- ✅ Email sending (mock)
- ✅ Template usage
- ✅ EmailVerificationSentView
- ✅ EmailVerificationView (success/failure)
- ✅ EmailVerificationFailedView
- ✅ Token validation (valid/invalid/expired/used)
- ✅ Full signup flow integration

### 🗄️ Model Tests (test_signup_models.py)
- **File:** `working_tests/test_signup_models.py`
- **Test Classes:** 5 classes
- **Total Tests:** ~30 tests
- **Coverage:** User, UserProfile, EmailVerificationToken, Organisor models

#### Tested Features:
- ✅ User model creation and properties
- ✅ User uniqueness constraints
- ✅ UserProfile model and relations
- ✅ EmailVerificationToken model
- ✅ Token expiry check (24 hours)
- ✅ Organisor model and relations
- ✅ Model cascade delete operations
- ✅ Model data integrity
- ✅ Model validations

### 🔗 Integration Tests (test_signup_integration.py)
- **File:** `working_tests/test_signup_integration.py`
- **Test Classes:** 6 classes
- **Total Tests:** ~20 tests
- **Coverage:** Full signup flow, model relations, form-view integration

#### Tested Features:
- ✅ Full signup and verification flow
- ✅ Signup flow with invalid data
- ✅ Signup flow with conflicting data
- ✅ Email verification flows (success/failure)
- ✅ Model relations and cascade operations
- ✅ Form and view integration
- ✅ Data consistency check

## 📈 Test Statistics

### ✅ Total Test Count: ~110 tests
- **Form Tests:** ~25 tests
- **View Tests:** ~35 tests
- **Model Tests:** ~30 tests
- **Integration Tests:** ~20 tests

### 🎯 Test Coverage
- **Models:** User, UserProfile, EmailVerificationToken, Organisor
- **Views:** SignupView, EmailVerificationView, EmailVerificationSentView, EmailVerificationFailedView
- **Forms:** CustomUserCreationForm
- **URLs:** signup, verify-email, verify-email-sent, verify-email-failed
- **Templates:** signup.html, verify_email_sent.html, verify_email_failed.html

## 🔧 Test Features

### Mock Usage
- Uses `unittest.mock.patch` for email sending
- No actual email sending, only mock verification

### Test Data
- Each test uses unique usernames
- Test data is realistic and in valid format
- Cleanup is automatic after tests

### Error Scenarios
- Invalid email formats
- Conflicting usernames/emails
- Password mismatches
- Missing required fields
- Expired/used tokens

## 🎯 Signup Flow Under Test

1. **Signup Page** → Form display
2. **Form Submission** → Data validation
3. **User Creation** → User, UserProfile, Organisor creation
4. **Email Token** → EmailVerificationToken creation
5. **Email Sending** → Verification link sending
6. **Email Verification** → Email verification with token
7. **Login Redirect** → After successful verification

## 🚨 Important Notes

### Running Tests
- Django settings must load correctly
- Test database is used (real data is not affected)
- Mock usage is important for email tests

### Test Data
- Each test uses unique usernames
- Phone numbers and email addresses must also be unique
- Django automatically cleans up after tests

### Mock Usage
- `@patch('leads.views.send_mail')` is used for email sending tests
- Verifies that mock is called with correct parameters

## 📝 Test Development

### Adding New Tests
1. Select the appropriate test file (forms/views/models/integration)
2. Add new method to existing test class or create new class
3. Start test method with `test_`
4. Add assertions
5. Run and verify the test

### Test Best Practices
- Each test should be independent
- Test data should be realistic
- Mock usage where necessary
- Error scenarios should also be tested
- Test names should be descriptive

## 🔍 Troubleshooting

### Common Errors
1. **UserProfile unique constraint error:** Use unique usernames
2. **Email sending error:** Check mock usage
3. **Token expiry error:** Update test data
4. **Form validation error:** Check test data

### Debug Tips
- Use `-v 2` parameter for verbose output
- Run specific tests one by one
- Check test data
- Verify mock usage

## 📚 Resources

- [Django Testing Documentation](https://docs.djangoproject.com/en/stable/topics/testing/)
- [Python unittest Documentation](https://docs.python.org/3/library/unittest.html)
- [Django TestCase Documentation](https://docs.djangoproject.com/en/stable/topics/testing/tools/#django.test.TestCase)
