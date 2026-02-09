"""
Agent Test Runner
This file is used to run agent tests.
"""

import os
import sys
import django
from django.test.utils import get_runner
from django.conf import settings

# Load Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djcrm.settings')
django.setup()

def run_agent_tests():
    """Run agent tests"""
    print("Starting Agent Tests...")
    print("=" * 60)
    
    # Create test runner
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    
    # Define test modules
    test_modules = [
        'test.agents.working_tests.test_models',
        'test.agents.working_tests.test_forms',
        'test.agents.working_tests.test_views',
        'test.agents.working_tests.test_mixins',
        'test.agents.working_tests.test_integration',
    ]
    
    # Run tests
    failures = test_runner.run_tests(test_modules, verbosity=2)
    
    if failures:
        print(f"\n❌ {failures} tests failed!")
        return False
    else:
        print("\n✅ All tests passed!")
        return True

def run_specific_test(test_module):
    """Run a specific test module"""
    print(f"Running Agent Test Module: {test_module}")
    print("=" * 60)
    
    # Create test runner
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    
    # Run test
    failures = test_runner.run_tests([test_module], verbosity=2)
    
    if failures:
        print(f"\n❌ {failures} tests failed!")
        return False
    else:
        print("\n✅ Test passed!")
        return True

def run_model_tests():
    """Run model tests"""
    return run_specific_test('test.agents.working_tests.test_models')

def run_form_tests():
    """Run form tests"""
    return run_specific_test('test.agents.working_tests.test_forms')

def run_view_tests():
    """Run view tests"""
    return run_specific_test('test.agents.working_tests.test_views')

def run_mixin_tests():
    """Run mixin tests"""
    return run_specific_test('test.agents.working_tests.test_mixins')

def run_integration_tests():
    """Run integration tests"""
    return run_specific_test('test.agents.working_tests.test_integration')

def show_test_menu():
    """Show test menu"""
    print("\n" + "=" * 60)
    print("AGENT TEST MENU")
    print("=" * 60)
    print("1. Run all tests")
    print("2. Model tests")
    print("3. Form tests")
    print("4. View tests")
    print("5. Mixin tests")
    print("6. Integration tests")
    print("7. Exit")
    print("=" * 60)

def main():
    """Main function"""
    while True:
        show_test_menu()
        
        try:
            choice = input("\nEnter your choice (1-7): ").strip()
            
            if choice == '1':
                run_agent_tests()
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
            elif choice == '7':
                print("Exiting...")
                break
            else:
                print("❌ Invalid choice! Please enter a number between 1 and 7.")
            
            input("\nPress Enter to continue...")
            
        except KeyboardInterrupt:
            print("\n\nExiting...")
            break
        except Exception as e:
            print(f"\n❌ Error occurred: {e}")
            input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()
