"""
Logout Test Runner
This file allows running logout tests interactively.
"""

import os
import sys
import django

# Load Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djcrm.settings')
django.setup()

from django.core.management import call_command
from django.test.runner import DiscoverRunner


def print_header(text):
    """Print header"""
    print("\n" + "=" * 70)
    print(text.center(70))
    print("=" * 70 + "\n")


def print_section(text):
    """Print section header"""
    print("\n" + "-" * 70)
    print(text)
    print("-" * 70)


def run_tests(test_label, verbosity=2):
    """Run tests"""
    try:
        call_command('test', test_label, verbosity=verbosity)
        return True
    except SystemExit as e:
        if e.code == 0:
            return True
        return False


def main():
    """Main test runner function"""
    print_header("🔐 LOGOUT TEST RUNNER 🔐")
    
    print("Logout Test Options:")
    print("\n1. ✅ All Working Logout Tests")
    print("2. 📝 Logout View Tests")
    print("3. 🔗 Logout Integration Tests")
    print("4. 🚀 All Logout Tests (Working)")
    print("5. ❌ Exit")
    
    choice = input("\nEnter your choice (1-5): ")
    
    if choice == '1':
        print_section("Running All Working Logout Tests...")
        run_tests('test.logout.working', verbosity=2)
    
    elif choice == '2':
        print_section("Running Logout View Tests...")
        run_tests('test.logout.working.test_logout_views', verbosity=2)
    
    elif choice == '3':
        print_section("Running Logout Integration Tests...")
        run_tests('test.logout.working.test_logout_integration', verbosity=2)
    
    elif choice == '4':
        print_section("Running All Logout Tests...")
        run_tests('test.logout.working', verbosity=2)
    
    elif choice == '5':
        print("\n👋 Closing test runner...")
        sys.exit(0)
    
    else:
        print("\n❌ Invalid choice! Please enter a number between 1 and 5.")
        return main()
    
    # Run again option
    print("\n" + "=" * 70)
    repeat = input("Would you like to run another test? (y/n): ")
    if repeat.lower() == 'y':
        return main()
    else:
        print("\n👋 Closing test runner...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Test runner stopped by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error occurred: {e}")
        sys.exit(1)
