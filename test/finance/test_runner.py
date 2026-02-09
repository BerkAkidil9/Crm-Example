"""
Finance Test Runner
This file is used to run tests for the Finance module.
"""

import os
import sys
import django
from django.test.utils import get_runner
from django.conf import settings

# Load Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djcrm.settings')
django.setup()

def run_finance_tests():
    """Run Finance tests"""
    print("Starting Finance Tests...")
    print("=" * 60)
    
    # Create test runner
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    
    # Define test modules
    test_modules = [
        'test.finance.working_tests.test_models',
        'test.finance.working_tests.test_views',
        'test.finance.working_tests.test_forms',
        'test.finance.working_tests.test_integration',
    ]
    
    # Run tests
    failures = test_runner.run_tests(test_modules, verbosity=2)
    
    if failures:
        print(f"\n❌ {failures} test(s) failed!")
        return False
    else:
        print("\n✅ All tests passed!")
        return True

def run_specific_test(test_module):
    """Run a specific test module"""
    print(f"Starting Finance {test_module} Tests...")
    print("=" * 60)
    
    # Create test runner
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    
    # Run test module
    failures = test_runner.run_tests([f'test.finance.working_tests.{test_module}'], verbosity=2)
    
    if failures:
        print(f"\n❌ {failures} test(s) failed!")
        return False
    else:
        print("\n✅ All tests passed!")
        return True

def run_model_tests():
    """Run model tests"""
    return run_specific_test('test_models')

def run_view_tests():
    """Run view tests"""
    return run_specific_test('test_views')

def run_form_tests():
    """Run form tests"""
    return run_specific_test('test_forms')

def run_integration_tests():
    """Run integration tests"""
    return run_specific_test('test_integration')

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Finance Test Runner')
    parser.add_argument('--module', choices=['models', 'views', 'forms', 'integration', 'all'], 
                       default='all', help='Which test module do you want to run?')
    
    args = parser.parse_args()
    
    if args.module == 'all':
        success = run_finance_tests()
    elif args.module == 'models':
        success = run_model_tests()
    elif args.module == 'views':
        success = run_view_tests()
    elif args.module == 'forms':
        success = run_form_tests()
    elif args.module == 'integration':
        success = run_integration_tests()
    
    sys.exit(0 if success else 1)
