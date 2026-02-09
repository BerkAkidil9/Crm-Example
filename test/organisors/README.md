# Organisors Test System

This folder contains organized test files for the organisors module.

## 📁 Folder Structure

```
test/organisors/
├── __init__.py
├── working_tests/          # ✅ Working tests
│   ├── __init__.py
│   ├── test_models.py      # Model tests
│   ├── test_forms.py       # Form tests
│   ├── test_views.py       # View tests
│   ├── test_mixins.py      # Mixin tests
│   └── test_integration.py # Integration tests
├── test_runner.py          # Interactive test runner
└── README.md
```

## 🚀 Running Tests

### ✅ Run All Tests
```bash
# With interactive menu
python test/organisors/test_runner.py

# Run all tests directly
python test/organisors/test_runner.py all

# With Django test command
python manage.py test test.organisors.working_tests
```

### 📋 Run Specific Test Categories
```bash
# Model tests
python test/organisors/test_runner.py models
python manage.py test test.organisors.working_tests.test_models

# Form tests
python test/organisors/test_runner.py forms
python manage.py test test.organisors.working_tests.test_forms

# View tests
python test/organisors/test_runner.py views
python manage.py test test.organisors.working_tests.test_views

# Mixin tests
python test/organisors/test_runner.py mixins
python manage.py test test.organisors.working_tests.test_mixins

# Integration tests
python test/organisors/test_runner.py integration
python manage.py test test.organisors.working_tests.test_integration
```

## 📊 Test Coverage

### Models (1 model)
- ✅ Organisor (working)
  - Model creation
  - String representation
  - Relations (User, UserProfile)
  - Cascade delete
  - Unique constraints
  - Meta options

### Views (5 views)
- ✅ OrganisorListView (working)
- ✅ OrganisorCreateView (working)
- ✅ OrganisorDetailView (working)
- ✅ OrganisorUpdateView (working)
- ✅ OrganisorDeleteView (working)

### Forms (2 forms)
- ✅ OrganisorModelForm (working)
- ✅ OrganisorCreateForm (working)

### Mixins (3 mixins)
- ✅ AdminOnlyMixin (working)
- ✅ OrganisorAndAdminMixin (working)
- ✅ SelfProfileOnlyMixin (working)

### Integration Tests
- ✅ Full organisor lifecycle
- ✅ Permission system
- ✅ Form validation
- ✅ Model relations
- ✅ Email verification
- ✅ Bulk operations
- ✅ Error handling

## 🎯 Test Features

### Model Tests
- **Organisor Model**: Basic CRUD operations, relations, constraints
- **Relation Tests**: User-Organisor, Organisation-Organisor
- **Cascade Delete**: Organisor is deleted when User/Organisation is deleted
- **Unique Constraints**: OneToOneField constraints
- **Edge Cases**: Boundary conditions and error scenarios

### Form Tests
- **OrganisorModelForm**: Update form validations
- **OrganisorCreateForm**: Create form validations
- **Field Validation**: Email, username, phone number uniqueness
- **Password Validation**: Password match and security rules
- **Widget Attributes**: CSS classes and placeholders
- **Clean Methods**: Custom validation methods

### View Tests
- **Permission System**: Admin, Organisor, Agent access controls
- **CRUD Operations**: Create, Read, Update, Delete operations
- **Template Rendering**: Correct templates are used
- **Form Handling**: GET/POST requests and validation
- **Redirect Logic**: Redirects after successful operations
- **Error Handling**: 404, 403 errors and form errors

### Mixin Tests
- **AdminOnlyMixin**: Only admin users can access
- **OrganisorAndAdminMixin**: Admin and organisor users can access
- **SelfProfileOnlyMixin**: Users can only access their own profiles
- **Permission Hierarchy**: Admin > Organisor > Agent > Anonymous
- **Edge Cases**: Non-existent records, unauthorized access

### Integration Tests
- **Complete Lifecycle**: Full organisor lifecycle
- **Permission Integration**: Permission system across all views
- **Form Integration**: Form validation and error handling
- **Model Integration**: Model relations and cascade operations
- **Email Integration**: Email verification and sending
- **Bulk Operations**: Bulk create and delete operations

## 🔧 Test Data

### User Types
- **Admin User**: ID=1 or username='berk' (all operations)
- **Organisor User**: is_organisor=True (limited operations)
- **Agent User**: is_agent=True (no operations)
- **Anonymous User**: Not logged in (redirect)

### Test Data
- **Unique Users**: Unique username/email for each test
- **Realistic Data**: Phone numbers, dates
- **Edge Cases**: Invalid data, boundary conditions
- **Mock Objects**: Mock usage for email sending

## 📈 Test Metrics

### Test Counts
- **Model Tests**: ~20 tests
- **Form Tests**: ~30 tests
- **View Tests**: ~50 tests
- **Mixin Tests**: ~25 tests
- **Integration Tests**: ~15 tests
- **Total**: ~140 tests

### Test Categories
- **Unit Tests**: Individual component tests
- **Integration Tests**: Inter-component interaction
- **Permission Tests**: Authorization and access controls
- **Validation Tests**: Form and model validations
- **Error Handling Tests**: Error scenarios

## 🎨 Test Style

### Naming Convention
- **Test Classes**: `Test[ComponentName][TestType]`
- **Test Methods**: `test_[specific_functionality]`
- **Setup Methods**: `setUp()` - prepares test data
- **Helper Methods**: `_helper_method_name()`

### Test Structure
```python
class TestComponentName(TestCase):
    def setUp(self):
        """Set up test data"""
        # Create test data
    
    def test_specific_functionality(self):
        """Test specific functionality"""
        # Test steps
        # Assertions
```

### Assertion Patterns
- **Status Codes**: `self.assertEqual(response.status_code, 200)`
- **Redirects**: `self.assertRedirects(response, expected_url)`
- **Template Usage**: `self.assertTemplateUsed(response, 'template.html')`
- **Content**: `self.assertContains(response, 'expected_text')`
- **Database**: `self.assertTrue(Model.objects.filter(...).exists())`

## 🚨 Error Handling

### Test Errors
- **Import Errors**: Django setup and model imports
- **Database Errors**: Test database creation
- **Permission Errors**: Permission checks
- **Validation Errors**: Form and model validations

### Debug Information
- **Verbose Output**: Detailed output with `-v 2`
- **Error Messages**: Error messages and stack trace
- **Test Names**: Which test failed
- **Assertion Details**: Expected vs actual values

## 📝 Notes

- Tests use Django TestCase
- Each test runs independently
- Test database is automatically created and destroyed
- Mock usage for email sending
- Factory pattern for test data creation
- CSRF tokens are automatically handled in test environment

## 🔄 Update Notes

### v1.0.0 (Initial Release)
- Basic model, form, view tests
- Mixin tests
- Integration tests
- Test runner and documentation

### Future Plans
- Performance tests
- Load tests
- API tests (if API is added)
- Test coverage report
- Automated testing pipeline
