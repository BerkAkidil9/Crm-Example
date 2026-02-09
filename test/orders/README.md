# Orders App Test System

This folder contains organized test files for the Orders module.

## 📁 Folder Structure

```
test/orders/
├── __init__.py
├── working_tests/          # ✅ Working tests
│   ├── __init__.py
│   ├── test_models.py
│   ├── test_views.py
│   ├── test_forms.py
│   └── test_integration.py
├── test_runner.py          # Interactive test runner
└── README.md
```

## 🚀 Running Tests

### ✅ Working Tests
```bash
# Model tests
python manage.py test test.orders.working_tests.test_models

# View tests
python manage.py test test.orders.working_tests.test_views

# Form tests
python manage.py test test.orders.working_tests.test_forms

# Integration tests
python manage.py test test.orders.working_tests.test_integration

# All orders tests
python manage.py test test.orders.working_tests
```

## 📊 Test Coverage

### Models (2 models)
- ✅ orders (working)
- ✅ OrderProduct (working)

### Views (6 views)
- ✅ OrderListView (working)
- ✅ OrderDetailView (working)
- ✅ OrderCreateView (working)
- ✅ OrderUpdateView (working)
- ✅ OrderCancelView (working)
- ✅ OrderDeleteView (working)

### Forms (3 forms)
- ✅ OrderModelForm (working)
- ✅ OrderForm (working)
- ✅ OrderProductFormSet (working)

## 🔧 Custom Test Features

### Stock Management Tests
- Automatic stock reduction tests
- Stock restoration tests
- Insufficient stock check tests

### Signal Tests
- OrderProduct creation signal tests
- Order cancel signal tests
- Stock movement record tests

### Finance Integration Tests
- OrderFinanceReport creation tests
- Total price calculation tests

## 📈 Test Statistics

- **Total Test Count:** 45+ tests
- **Model Tests:** 15 tests
- **View Tests:** 20 tests
- **Form Tests:** 8 tests
- **Integration Tests:** 5 tests

## 📝 Notes

- Tests use Django TestCase
- Each test runs independently
- Test database is created and torn down automatically
- Mock used for email sending
- Factory pattern used for test data creation
- TransactionTestCase used for signal tests
