# Forget Password Test System

This folder contains organized test files for the forget password (password reset) module.

## 📁 Folder Structure

```
test/forget_password/
├── __init__.py
├── test_forget_password_views.py      # View tests
├── test_forget_password_forms.py      # Form tests
├── test_runner.py                     # Test runner
└── README.md                          # This file
```

## 🚀 Running Tests

### Run All Tests
```bash
# All forget password tests
python manage.py test test.forget_password

# Verbose mode
python manage.py test test.forget_password -v 2

# With test runner
python test/forget_password/test_runner.py
```

### Run Specific Test Files
```bash
# View tests only
python manage.py test test.forget_password.test_forget_password_views

# Form tests only
python manage.py test test.forget_password.test_forget_password_forms
```

### Run Specific Test Classes
```bash
# Password reset view tests
python manage.py test test.forget_password.test_forget_password_views.TestCustomPasswordResetView

# Password reset form tests
python manage.py test test.forget_password.test_forget_password_forms.TestCustomPasswordResetForm

# Set password form tests
python manage.py test test.forget_password.test_forget_password_forms.TestCustomSetPasswordForm
```

### Run Specific Test Methods
```bash
# A specific test method
python manage.py test test.forget_password.test_forget_password_views.TestCustomPasswordResetView.test_password_reset_view_get
```

## 📊 Test Coverage

### View Tests (test_forget_password_views.py)

#### CustomPasswordResetView Tests
- ✅ GET request test
- ✅ Template test
- ✅ Form class test
- ✅ POST test with valid email
- ✅ POST test with invalid email
- ✅ POST test with non-existent email
- ✅ POST test with unverified email
- ✅ POST test with empty email
- ✅ Case insensitive email test
- ✅ Email with whitespace test
- ✅ Email sending details test
- ✅ Multiple request test

#### PasswordResetDoneView Tests
- ✅ GET request test
- ✅ Template test
- ✅ Content test

#### CustomPasswordResetConfirmView Tests
- ✅ GET test with valid token
- ✅ Form class test
- ✅ POST test with valid data
- ✅ Password mismatch test
- ✅ Weak password test
- ✅ Empty password test
- ✅ Invalid token test
- ✅ Invalid uid test
- ✅ Expired token test
- ✅ Non-existent user test
- ✅ Inactive user test

#### PasswordResetCompleteView Tests
- ✅ GET request test
- ✅ Template test
- ✅ Content test

#### Integration Tests
- ✅ Full forget password flow test
- ✅ Test with invalid email
- ✅ Test with unverified email
- ✅ Form validation test
- ✅ Security measures test

### Form Tests (test_forget_password_forms.py)

#### CustomPasswordResetForm Tests
- ✅ Form initialization test
- ✅ Widget properties test
- ✅ Valid data test
- ✅ Invalid email format test
- ✅ Empty email test
- ✅ Non-existent email test
- ✅ Case insensitive email test
- ✅ Whitespace email test
- ✅ Long email test
- ✅ Email with special characters test
- ✅ Multiple @ symbols test
- ✅ Email without @ test
- ✅ Email without domain test
- ✅ Email without local part test
- ✅ Unicode email test
- ✅ Numeric email test
- ✅ Email with dot test
- ✅ Email with + test
- ✅ Email with hyphen test
- ✅ Email with underscore test

#### CustomSetPasswordForm Tests
- ✅ Form initialization test
- ✅ Widget properties test
- ✅ Help text test
- ✅ Valid data test
- ✅ Password mismatch test
- ✅ Empty password test
- ✅ Short password test
- ✅ Common password test
- ✅ Fully numeric password test
- ✅ Password similar to username test
- ✅ Password similar to email test
- ✅ Password similar to first name test
- ✅ Password similar to last name test
- ✅ Whitespace password test
- ✅ Unicode password test
- ✅ Password with special characters test
- ✅ Long password test
- ✅ Save functionality test
- ✅ Save commit=False test

#### Integration Tests
- ✅ Password reset form test with existing user
- ✅ Password reset form test with non-existent user
- ✅ Set password form test with valid data
- ✅ Set password form test with invalid data
- ✅ Form validation edge cases test
- ✅ Form field properties test

## 🔧 Test Features

### Security Tests
- ✅ Case insensitive email handling
- ✅ Whitespace trimming
- ✅ Returns success for non-existent email too (security)
- ✅ Token validation
- ✅ Password strength validation
- ✅ Similarity checks

### Edge Case Tests
- ✅ Empty forms
- ✅ None data
- ✅ Invalid formats
- ✅ Very long data
- ✅ Unicode characters
- ✅ Special characters

### Integration Tests
- ✅ Full password reset flow
- ✅ Form validations
- ✅ Email sending
- ✅ Password change
- ✅ Error handling

## 📈 Test Statistics

### Total Test Count
- **View Tests:** 25+ test methods
- **Form Tests:** 30+ test methods
- **Integration Tests:** 10+ test methods
- **Total:** 65+ test methods

### Test Classes
- **TestCustomPasswordResetView:** 12 tests
- **TestPasswordResetDoneView:** 3 tests
- **TestCustomPasswordResetConfirmView:** 10 tests
- **TestPasswordResetCompleteView:** 3 tests
- **TestForgetPasswordIntegration:** 5 tests
- **TestCustomPasswordResetForm:** 20 tests
- **TestCustomSetPasswordForm:** 18 tests
- **TestForgetPasswordFormIntegration:** 6 tests

## 🎯 Test Goals

### Functional Tests
- ✅ Password reset form works
- ✅ Email sending works
- ✅ Password change works
- ✅ Form validations work

### Security Tests
- ✅ Secure email handling
- ✅ Secure password validation
- ✅ Token security
- ✅ Input sanitization

### Usability Tests
- ✅ User-friendly error messages
- ✅ Proper form styling
- ✅ Responsive design
- ✅ Accessibility

## 🚨 Known Issues

There are currently no known issues.

## 🔮 Future Plans

1. **Add performance tests**
2. **Add load tests**
3. **Add mobile responsive tests**
4. **Add accessibility tests**
5. **Add internationalization tests**

## 📝 Notes

- Tests use Django TestCase
- Each test runs independently
- Test database is created and torn down automatically
- Mock used for email sending
- Factory pattern used for test data creation
- Comprehensive error handling
- Edge case coverage
- Security testing included

## 🏃‍♂️ Quick Start

```bash
# 1. Run the test runner
python test/forget_password/test_runner.py

# 2. Select from the menu
# 3. Run the tests
# 4. Review the results
```

## 📞 Support

For issues with the tests:
1. Use the test runner
2. Run in verbose mode
3. Isolate specific tests
4. Check log files
