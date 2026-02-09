"""
Organisors Test Runner
This file runs all tests in the organisors module.
"""

import os
import sys
import django
from django.test.utils import get_runner
from django.conf import settings

# Load Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djcrm.settings')
django.setup()

def run_organisor_tests():
    """Run organisor tests"""
    print("Organisors Test System")
    print("=" * 60)
    
    # Create test runner
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    
    # Test modules
    test_modules = [
        'test.organisors.working_tests.test_models',
        'test.organisors.working_tests.test_forms',
        'test.organisors.working_tests.test_views',
        'test.organisors.working_tests.test_mixins',
        'test.organisors.working_tests.test_integration',
    ]
    
    print("Test Modules to Run:")
    for module in test_modules:
        print(f"  - {module}")
    print()
    
    # Run tests
    failures = test_runner.run_tests(test_modules, verbosity=2)
    
    if failures:
        print(f"\n❌ {failures} tests failed!")
        return False
    else:
        print("\n✅ All tests passed!")
        return True

def run_specific_test(test_module):
    """Run specific test module"""
    print(f"Organisors {test_module} Tests")
    print("=" * 60)
    
    # Create test runner
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    
    # Test module
    test_module_path = f'test.organisors.working_tests.{test_module}'
    
    print(f"Running Test Module: {test_module_path}")
    print()
    
    # Run test
    failures = test_runner.run_tests([test_module_path], verbosity=2)
    
    if failures:
        print(f"\n❌ {failures} tests failed!")
        return False
    else:
        print("\n✅ All tests passed!")
        return True

def run_model_tests():
    """Run model tests"""
    return run_specific_test('test_models')

def run_form_tests():
    """Run form tests"""
    return run_specific_test('test_forms')

def run_view_tests():
    """Run view tests"""
    return run_specific_test('test_views')

def run_mixin_tests():
    """Run mixin tests"""
    return run_specific_test('test_mixins')

def run_integration_tests():
    """Run integration tests"""
    return run_specific_test('test_integration')

def show_test_menu():
    """Show test menu"""
    print("\nOrganisors Test Menu")
    print("=" * 30)
    print("1. Run all tests")
    print("2. Run model tests")
    print("3. Run form tests")
    print("4. Run view tests")
    print("5. Run mixin tests")
    print("6. Run integration tests")
    print("0. Exit")
    print()

def main():
    """Main function"""
    while True:
        show_test_menu()
        choice = input("Enter your choice (0-6): ").strip()
        
        if choice == '0':
            print("Exiting...")
            break
        elif choice == '1':
            run_organisor_tests()
        elif choice == '2':
            run_model_tests()
        elif choice == '3':
            run_form_tests()
        elif choice == '4':
            run_view_tests()
        elif choice == '5':
            run_mixin_tests()
        elif choice == '6':
            run_integration_tests()
        else:
            print("Invalid choice! Please enter a number between 0-6.")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    # Check command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == 'all':
            run_organisor_tests()
        elif sys.argv[1] == 'models':
            run_model_tests()
        elif sys.argv[1] == 'forms':
            run_form_tests()
        elif sys.argv[1] == 'views':
            run_view_tests()
        elif sys.argv[1] == 'mixins':
            run_mixin_tests()
        elif sys.argv[1] == 'integration':
            run_integration_tests()
        else:
            print("Invalid argument! Usage:")
            print("python test_runner.py [all|models|forms|views|mixins|integration]")
    else:
        # Interactive menu
        main()
