"""
Login Test Runner
This file is used to run login tests.
"""

import os
import sys
import django
from django.test.utils import get_runner
from django.conf import settings

# Load Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djcrm.settings')
django.setup()

def run_login_tests():
    """Run login tests"""
    print("Starting Login Test System...")
    print("=" * 60)
    
    # Create test runner
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    
    # Test modules
    test_modules = [
        'test.login.working.test_login_views',
        'test.login.working.test_login_forms',
        'test.login.working.test_login_authentication',
        'test.login.working.test_login_integration',
    ]
    
    # Run tests
    failures = test_runner.run_tests(test_modules, verbosity=2)
    
    if failures:
        print(f"\n❌ {failures} tests failed!")
        return False
    else:
        print("\n✅ All tests passed!")
        return True

def run_specific_login_test(test_name):
    """Run a specific login test"""
    print(f"Running Login Test: {test_name}")
    print("=" * 60)
    
    # Create test runner
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    
    # Test module
    test_module = f'test.login.working.{test_name}'
    
    # Run test
    failures = test_runner.run_tests([test_module], verbosity=2)
    
    if failures:
        print(f"\n❌ {failures} tests failed!")
        return False
    else:
        print("\n✅ Test passed!")
        return True

def run_login_view_tests():
    """Run login view tests"""
    return run_specific_login_test('test_login_views')

def run_login_form_tests():
    """Run login form tests"""
    return run_specific_login_test('test_login_forms')

def run_login_authentication_tests():
    """Run login authentication tests"""
    return run_specific_login_test('test_login_authentication')

def run_login_integration_tests():
    """Run login integration tests"""
    return run_specific_login_test('test_login_integration')

def show_test_menu():
    """Show test menu"""
    print("\nLogin Test Menu")
    print("=" * 30)
    print("1. All login tests")
    print("2. Login view tests")
    print("3. Login form tests")
    print("4. Login authentication tests")
    print("5. Login integration tests")
    print("6. Exit")
    print("=" * 30)

def main():
    """Main function"""
    while True:
        show_test_menu()
        choice = input("\nEnter your choice (1-6): ").strip()
        
        if choice == '1':
            run_login_tests()
        elif choice == '2':
            run_login_view_tests()
        elif choice == '3':
            run_login_form_tests()
        elif choice == '4':
            run_login_authentication_tests()
        elif choice == '5':
            run_login_integration_tests()
        elif choice == '6':
            print("Exiting...")
            break
        else:
            print("Invalid choice! Please enter a number between 1 and 6.")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()
