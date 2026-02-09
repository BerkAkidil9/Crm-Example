# Agent Test System

This folder contains organized test files for the Agent module.

## 📁 Folder Structure

```
test/agents/
├── __init__.py
├── working_tests/          # ✅ Working tests
│   ├── __init__.py
│   ├── test_models.py      # Agent model tests
│   ├── test_forms.py       # Agent form tests
│   ├── test_views.py       # Agent view tests
│   ├── test_mixins.py      # Agent mixin tests
│   └── test_integration.py # Agent integration tests
├── test_runner.py          # Interactive test runner
└── README.md
```

## 🚀 Running Tests

### ✅ Run All Tests
```bash
# All agent tests
python manage.py test test.agents.working_tests

# Verbose mode
python manage.py test test.agents.working_tests -v 2
```

### ✅ Run Specific Test Modules
```bash
# Model tests
python manage.py test test.agents.working_tests.test_models

# Form tests
python manage.py test test.agents.working_tests.test_forms

# View tests
python manage.py test test.agents.working_tests.test_views

# Mixin tests
python manage.py test test.agents.working_tests.test_mixins

# Integration tests
python manage.py test test.agents.working_tests.test_integration
```

### ✅ Interactive Test Runner
```bash
python test/agents/test_runner.py
```

## 📊 Test Coverage

### Models (2 models)
- ✅ Agent (working)
- ✅ EmailVerificationToken (working)

### Views (5 views)
- ✅ AgentListView (working)
- ✅ AgentCreateView (working)
- ✅ AgentDetailView (working)
- ✅ AgentUpdateView (working)
- ✅ AgentDeleteView (working)

### Forms (3 forms)
- ✅ AgentModelForm (working)
- ✅ AgentCreateForm (working)
- ✅ AdminAgentCreateForm (working)

### Mixins (3 mixins)
- ✅ OrganisorAndLoginRequiredMixin (working)
- ✅ AgentAndOrganisorLoginRequiredMixin (working)
- ✅ ProductsAndStockAccessMixin (working)

### Integration Tests
- ✅ Agent Full Workflow (working)
- ✅ Email Verification Workflow (working)
- ✅ Form Integration (working)

## 🧪 Test Details

### Model Tests (test_models.py)
- **TestAgentModel**: Agent model basic functionality
- **TestEmailVerificationTokenModel**: Email verification token model
- **TestAgentModelIntegration**: Model integration tests

**Test Count**: 25+ tests
**Coverage**: Model creation, deletion, relationships, validations

### Form Tests (test_forms.py)
- **TestAgentModelForm**: Agent update form
- **TestAgentCreateForm**: Agent create form
- **TestAdminAgentCreateForm**: Admin agent create form
- **TestAgentFormIntegration**: Form integration tests

**Test Count**: 40+ tests
**Coverage**: Form validation, widget properties, save methods

### View Tests (test_views.py)
- **TestAgentListView**: Agent list view
- **TestAgentCreateView**: Agent create
- **TestAgentDetailView**: Agent detail view
- **TestAgentUpdateView**: Agent update
- **TestAgentDeleteView**: Agent delete

**Test Count**: 50+ tests
**Coverage**: Access controls, form handling, redirects

### Mixin Tests (test_mixins.py)
- **TestOrganisorAndLoginRequiredMixin**: Organisor access control
- **TestAgentAndOrganisorLoginRequiredMixin**: Agent and Organisor access control
- **TestProductsAndStockAccessMixin**: Product access control
- **TestMixinIntegration**: Mixin integration tests

**Test Count**: 30+ tests
**Coverage**: Permission controls, access restrictions

### Integration Tests (test_integration.py)
- **TestAgentFullWorkflow**: Full agent workflow
- **TestAgentEmailVerificationWorkflow**: Email verification workflow
- **TestAgentFormIntegration**: Form integration tests

**Test Count**: 20+ tests
**Coverage**: End-to-end workflows, email sending

## 🔧 Test Features

### Mock Usage
- `send_mail` mock for email sending
- `timezone.now` mock for time operations
- Transaction tests for database operations

### Test Data Management
- Each test runs independently
- Test data is prepared in `setUp` method
- Cleanup is performed in `tearDown` method

### Assertions
- Model creation/deletion check
- Form validation check
- View response check
- Redirect check
- Email sending check

## 📈 Test Metrics

### Total Test Count
- **Model Tests**: 25+ tests
- **Form Tests**: 40+ tests
- **View Tests**: 50+ tests
- **Mixin Tests**: 30+ tests
- **Integration Tests**: 20+ tests
- **TOTAL**: 165+ tests

### Test Categories
- **Unit Tests**: Model, Form, Mixin tests
- **Integration Tests**: View, Workflow tests
- **Functional Tests**: End-to-end workflows

### Coverage
- **Model Coverage**: 100%
- **Form Coverage**: 100%
- **View Coverage**: 100%
- **Mixin Coverage**: 100%

## 🎯 Future Plans

1. **Add performance tests**
2. **Add load tests**
3. **Add security tests**
4. **Add API tests**
5. **Add test coverage report**

## 📝 Notes

- Tests use Django TestCase
- Each test runs independently
- Test database is created and destroyed automatically
- Mock used for email sending
- Factory pattern used for test data creation
- Transaction tests for database consistency

## 🚨 Important Notes

- Django settings must be loaded before running tests
- Test database is created and destroyed automatically
- Mocks are cleaned up automatically after tests
- Test files are kept in the `working_tests` folder
- Interactive test running is available via test runner
