# Finance Test System

This folder contains organized test files for the Finance module.

## 📁 Folder Structure

```
test/finance/
├── __init__.py
├── working_tests/          # ✅ Working tests
│   ├── __init__.py
│   ├── test_models.py      # Model tests
│   ├── test_views.py       # View tests
│   ├── test_forms.py       # Form tests
│   └── test_integration.py # Integration tests
├── test_runner.py          # Interactive test runner
└── README.md
```

## 🚀 Running Tests

### ✅ All Tests
```bash
# All finance tests
python manage.py test test.finance.working_tests

# Verbose mode
python manage.py test test.finance.working_tests -v 2

# Using test runner
python test/finance/test_runner.py --module all
```

### 📊 Module-Based Tests
```bash
# Model tests
python manage.py test test.finance.working_tests.test_models
python test/finance/test_runner.py --module models

# View tests
python manage.py test test.finance.working_tests.test_views
python test/finance/test_runner.py --module views

# Form tests
python manage.py test test.finance.working_tests.test_forms
python test/finance/test_runner.py --module forms

# Integration tests
python manage.py test test.finance.working_tests.test_integration
python test/finance/test_runner.py --module integration
```

## 📊 Test Coverage

### Models (1 model)
- ✅ OrderFinanceReport (working)
  - Model creation
  - String representation
  - Default values
  - OneToOneField relationship
  - Unique constraint
  - Cascade delete
  - Float precision
  - Edge cases

### Views (1 view)
- ✅ FinancialReportView (working)
  - GET request
  - POST request (valid/invalid)
  - Date range filtering
  - Template rendering
  - Context data
  - Aggregation
  - Edge cases

### Forms (1 form)
- ✅ DateRangeForm (working)
  - Valid data
  - Invalid data
  - Date validation
  - Clean method
  - Widget configuration
  - Error messages
  - Edge cases

### Integration Tests
- ✅ Finance-Orders integration
- ✅ Finance-Products integration
- ✅ Finance-Views integration
- ✅ Data consistency
- ✅ Cascade operations
- ✅ Date filtering
- ✅ Organisation filtering

## 🎯 Test Details

### OrderFinanceReport Model Tests (15 tests)
1. **Model Creation Tests**
   - OrderFinanceReport creation
   - String representation
   - Default report_date
   - Manual report_date

2. **Field Tests**
   - Earned amount (positive, zero, negative)
   - Float precision
   - Large amounts

3. **Relationship Tests**
   - OneToOneField with orders
   - Unique constraint
   - Cascade delete

4. **Integration Tests**
   - Multiple orders
   - Date filtering
   - Organisation filtering
   - Aggregation

### FinancialReportView Tests (15 tests)
1. **GET Request Tests**
   - Template rendering
   - Context data
   - Form display

2. **POST Request Tests**
   - Valid dates
   - Invalid dates
   - Date range filtering
   - Empty results

3. **Template Tests**
   - With reports
   - Empty results
   - Data display

4. **Edge Cases**
   - No orders
   - Orders without finance reports
   - Zero/negative amounts

### DateRangeForm Tests (20 tests)
1. **Validation Tests**
   - Valid data
   - Invalid data
   - Date format errors
   - Missing fields

2. **Date Logic Tests**
   - Same dates
   - End date before start date
   - Future dates
   - Past dates

3. **Form Configuration Tests**
   - Widget years range
   - Field types
   - Required fields
   - Labels

4. **Edge Cases**
   - Extreme date ranges
   - Leap year dates
   - Year boundaries
   - None values

### Integration Tests (15 tests)
1. **Finance-Orders Integration**
   - Order creation with finance report
   - Order cancellation impact
   - Order deletion cascade
   - Multiple orders aggregation

2. **Finance-Products Integration**
   - Profit calculation
   - Multiple products profit
   - Stock movement integration

3. **Finance-Views Integration**
   - Full workflow
   - Form integration

4. **Data Consistency**
   - Data integrity
   - Unique constraints

## 📈 Test Statistics

### Total Test Count: 65 tests
- **Model Tests:** 15 tests
- **View Tests:** 15 tests  
- **Form Tests:** 20 tests
- **Integration Tests:** 15 tests

### Test Categories
- **Unit Tests:** 50 tests
- **Integration Tests:** 15 tests

### Covered Modules
- ✅ OrderFinanceReport model
- ✅ FinancialReportView
- ✅ DateRangeForm
- ✅ Finance-Orders integration
- ✅ Finance-Products integration
- ✅ Finance-Views integration

## 🔧 Test Features

### Test Setup
- Each test runs independently
- Test database is automatically created and torn down
- Mock used when needed
- Factory pattern for test data creation

### Test Data
- Organisor users
- UserProfiles
- Leads
- Categories and products
- Orders and OrderProducts
- Finance reports

### Assertions
- Model field validations
- View response codes
- Template content
- Form validation
- Database queries
- Data relationships

## 🎯 Future Plans

1. **Performance Tests** - Testing with large datasets
2. **Security Tests** - Authorization and authentication
3. **API Tests** - REST API endpoints
4. **Load Tests** - High traffic scenarios
5. **Coverage Reports** - Test coverage analysis

## 📝 Notes

- Tests use Django TestCase
- Each test runs independently
- Test database is automatically created and torn down
- Mock used for email sending
- Factory pattern used for test data creation
- Integration tests test cross-module interaction
- Edge case tests cover boundary conditions
