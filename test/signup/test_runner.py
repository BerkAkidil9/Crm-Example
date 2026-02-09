"""
Signup Test Runner
This file is used to run signup tests.
"""

import os
import sys
import django
from django.test.utils import get_runner
from django.conf import settings

# Load Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djcrm.settings')
django.setup()

def run_signup_tests():
    """Run signup tests"""
    print("🚀 Starting Signup Tests...")
    print("=" * 60)
    
    # Create test runner
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    
    # Define test modules
    test_modules = [
        'test.signup.working_tests.test_signup_forms',
        'test.signup.working_tests.test_signup_views', 
        'test.signup.working_tests.test_signup_models',
        'test.signup.working_tests.test_signup_integration',
    ]
    
    print("📋 Test modules to run:")
    for module in test_modules:
        print(f"  - {module}")
    print()
    
    # Run tests
    failures = test_runner.run_tests(test_modules, verbosity=2)
    
    print("\n" + "=" * 60)
    if failures == 0:
        print("✅ All signup tests passed!")
    else:
        print(f"❌ {failures} test(s) failed!")
    
    return failures

def run_specific_test(test_name):
    """Run a specific test"""
    print(f"🎯 Running {test_name}...")
    print("=" * 60)
    
    # Create test runner
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    
    # Run specific test
    failures = test_runner.run_tests([test_name], verbosity=2)
    
    print("\n" + "=" * 60)
    if failures == 0:
        print(f"✅ {test_name} passed!")
    else:
        print(f"❌ {test_name} failed!")
    
    return failures

def run_form_tests():
    """Run form tests only"""
    return run_specific_test('test.signup.working_tests.test_signup_forms')

def run_view_tests():
    """Run view tests only"""
    return run_specific_test('test.signup.working_tests.test_signup_views')

def run_model_tests():
    """Run model tests only"""
    return run_specific_test('test.signup.working_tests.test_signup_models')

def run_integration_tests():
    """Run integration tests only"""
    return run_specific_test('test.signup.working_tests.test_signup_integration')

def interactive_test_runner():
    """Interactive test runner"""
    while True:
        print("\n🔧 Signup Test Runner")
        print("=" * 40)
        print("1. Run all tests")
        print("2. Run form tests")
        print("3. Run view tests")
        print("4. Run model tests")
        print("5. Run integration tests")
        print("6. Run a specific test")
        print("0. Exit")
        print("-" * 40)
        
        choice = input("Enter your choice (0-6): ").strip()
        
        if choice == '0':
            print("👋 Exiting test runner...")
            break
        elif choice == '1':
            run_signup_tests()
        elif choice == '2':
            run_form_tests()
        elif choice == '3':
            run_view_tests()
        elif choice == '4':
            run_model_tests()
        elif choice == '5':
            run_integration_tests()
        elif choice == '6':
            test_name = input("Enter test name: ").strip()
            if test_name:
                run_specific_test(test_name)
            else:
                print("❌ Invalid test name!")
        else:
            print("❌ Invalid choice!")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'all':
            run_signup_tests()
        elif command == 'forms':
            run_form_tests()
        elif command == 'views':
            run_view_tests()
        elif command == 'models':
            run_model_tests()
        elif command == 'integration':
            run_integration_tests()
        elif command == 'interactive':
            interactive_test_runner()
        else:
            print("❌ Invalid command!")
            print("Usage: python test_runner.py [all|forms|views|models|integration|interactive]")
    else:
        # By default run all tests
        run_signup_tests()
