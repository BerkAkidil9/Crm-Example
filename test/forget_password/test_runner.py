"""
Forget Password Test Runner
This file is used to run forget password tests.
"""

import os
import sys
import django
from django.test.utils import get_runner
from django.conf import settings

# Load Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djcrm.settings')
django.setup()

def run_forget_password_tests():
    """Run forget password tests"""
    print("Starting Forget Password Tests...")
    print("=" * 60)
    
    # Create test runner
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    
    # Test modules
    test_modules = [
        'test.forget_password.test_forget_password_views',
        'test.forget_password.test_forget_password_forms',
    ]
    
    # Run tests
    failures = test_runner.run_tests(test_modules, verbosity=2)
    
    if failures:
        print(f"\n❌ {failures} tests failed!")
        return False
    else:
        print("\n✅ All tests passed!")
        return True

def run_specific_test(test_name):
    """Run a specific test"""
    print(f"Running Forget Password Test: {test_name}")
    print("=" * 60)
    
    # Create test runner
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    
    # Run specific test
    failures = test_runner.run_tests([test_name], verbosity=2)
    
    if failures:
        print(f"\n❌ Test failed!")
        return False
    else:
        print("\n✅ Test passed!")
        return True

def run_view_tests():
    """Run view tests only"""
    return run_specific_test('test.forget_password.test_forget_password_views')

def run_form_tests():
    """Run form tests only"""
    return run_specific_test('test.forget_password.test_forget_password_forms')

def run_integration_tests():
    """Run integration tests only"""
    print("Running Forget Password Integration Tests...")
    print("=" * 60)
    
    # Create test runner
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    
    # Run integration tests only
    test_modules = [
        'test.forget_password.test_forget_password_views.TestForgetPasswordIntegration',
        'test.forget_password.test_forget_password_forms.TestForgetPasswordFormIntegration',
    ]
    
    failures = test_runner.run_tests(test_modules, verbosity=2)
    
    if failures:
        print(f"\n❌ {failures} integration tests failed!")
        return False
    else:
        print("\n✅ All integration tests passed!")
        return True

def show_test_menu():
    """Show test menu"""
    print("\n" + "=" * 60)
    print("FORGET PASSWORD TEST MENU")
    print("=" * 60)
    print("1. Run all tests")
    print("2. Run view tests only")
    print("3. Run form tests only")
    print("4. Run integration tests only")
    print("5. Run a specific test")
    print("6. Test statistics")
    print("0. Exit")
    print("=" * 60)

def show_test_statistics():
    """Show test statistics"""
    print("\n" + "=" * 60)
    print("FORGET PASSWORD TEST STATISTICS")
    print("=" * 60)
    
    # Check test files
    test_files = [
        'test/forget_password/test_forget_password_views.py',
        'test/forget_password/test_forget_password_forms.py',
    ]
    
    total_tests = 0
    test_classes = 0
    
    for test_file in test_files:
        if os.path.exists(test_file):
            with open(test_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Test class count
                class_count = content.count('class Test')
                test_classes += class_count
                
                # Test method count
                method_count = content.count('def test_')
                total_tests += method_count
                
                print(f"📁 {test_file}:")
                print(f"   - Test Classes: {class_count}")
                print(f"   - Test Methods: {method_count}")
    
    print(f"\n📊 TOTAL STATISTICS:")
    print(f"   - Total Test Classes: {test_classes}")
    print(f"   - Total Test Methods: {total_tests}")
    print(f"   - Test Files: {len(test_files)}")
    
    print(f"\n📋 TEST COVERAGE:")
    print(f"   ✅ CustomPasswordResetView tests")
    print(f"   ✅ PasswordResetDoneView tests")
    print(f"   ✅ CustomPasswordResetConfirmView tests")
    print(f"   ✅ PasswordResetCompleteView tests")
    print(f"   ✅ CustomPasswordResetForm tests")
    print(f"   ✅ CustomSetPasswordForm tests")
    print(f"   ✅ Integration tests")
    print(f"   ✅ Security tests")
    print(f"   ✅ Edge case tests")

def main():
    """Main function"""
    while True:
        show_test_menu()
        
        try:
            choice = input("\nEnter your choice (0-6): ").strip()
            
            if choice == '0':
                print("Exiting...")
                break
            elif choice == '1':
                run_forget_password_tests()
            elif choice == '2':
                run_view_tests()
            elif choice == '3':
                run_form_tests()
            elif choice == '4':
                run_integration_tests()
            elif choice == '5':
                test_name = input("Enter test name (e.g. test.forget_password.test_forget_password_views.TestCustomPasswordResetView): ").strip()
                if test_name:
                    run_specific_test(test_name)
                else:
                    print("❌ Invalid test name!")
            elif choice == '6':
                show_test_statistics()
            else:
                print("❌ Invalid choice! Please enter a number between 0 and 6.")
            
            input("\nPress Enter to continue...")
            
        except KeyboardInterrupt:
            print("\n\nExiting...")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            input("Press Enter to continue...")

if __name__ == "__main__":
    main()
