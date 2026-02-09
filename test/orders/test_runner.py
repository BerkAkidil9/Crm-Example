#!/usr/bin/env python3
"""
Orders Test Runner
This script runs tests for the Orders module.
"""

import os
import sys
import django
import subprocess
import time

# Load Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djcrm.settings')
django.setup()

def run_test_command(test_path, verbose=False):
    """Run test command"""
    cmd = ['python', 'manage.py', 'test', test_path]
    if verbose:
        cmd.append('-v')
        cmd.append('2')
    
    print(f"Running command: {' '.join(cmd)}")
    print("-" * 60)
    
    start_time = time.time()
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=os.getcwd())
        end_time = time.time()
        
        print(f"Test duration: {end_time - start_time:.2f} seconds")
        print("-" * 60)
        
        if result.returncode == 0:
            print("✅ Test passed!")
            print(result.stdout)
        else:
            print("❌ Test failed!")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
        
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Test execution error: {e}")
        return False

def main():
    """Main function"""
    print("Orders Test Runner")
    print("=" * 60)
    print()
    
    # Test options
    tests = {
        '1': {
            'name': 'Model Tests',
            'path': 'test.orders.working_tests.test_models',
            'description': 'Tests for Orders models'
        },
        '2': {
            'name': 'View Tests',
            'path': 'test.orders.working_tests.test_views',
            'description': 'Tests for Orders views'
        },
        '3': {
            'name': 'Form Tests',
            'path': 'test.orders.working_tests.test_forms',
            'description': 'Tests for Orders forms'
        },
        '4': {
            'name': 'Integration Tests',
            'path': 'test.orders.working_tests.test_integration',
            'description': 'Orders integration tests'
        },
        '5': {
            'name': 'All Tests',
            'path': 'test.orders.working_tests',
            'description': 'All orders tests'
        }
    }
    
    while True:
        print("Test Options:")
        print("-" * 30)
        for key, test in tests.items():
            print(f"{key}. {test['name']}")
            print(f"   {test['description']}")
            print()
        
        print("Options:")
        print("v - Verbose mode (detailed output)")
        print("q - Quit")
        print()
        
        choice = input("Select test (1-5, v, q): ").strip().lower()
        
        if choice == 'q':
            print("Exiting...")
            break
        elif choice == 'v':
            verbose_mode = True
            print("Verbose mode active!")
            continue
        elif choice in tests:
            verbose_mode = getattr(main, 'verbose_mode', False)
            test_info = tests[choice]
            
            print(f"\nStarting {test_info['name']}...")
            print(f"Description: {test_info['description']}")
            print()
            
            success = run_test_command(test_info['path'], verbose=verbose_mode)
            
            if success:
                print(f"\n🎉 {test_info['name']} completed successfully!")
            else:
                print(f"\n💥 {test_info['name']} failed!")
            
            print("\n" + "=" * 60)
            print()
        else:
            print("❌ Invalid choice! Please enter 1-5, v or q.")
            print()

def run_all_tests():
    """Run all tests"""
    print("Running All Orders Tests...")
    print("=" * 60)
    
    tests = [
        ('Model Tests', 'test.orders.working_tests.test_models'),
        ('View Tests', 'test.orders.working_tests.test_views'),
        ('Form Tests', 'test.orders.working_tests.test_forms'),
        ('Integration Tests', 'test.orders.working_tests.test_integration'),
    ]
    
    results = []
    
    for test_name, test_path in tests:
        print(f"\nStarting {test_name}...")
        success = run_test_command(test_path, verbose=True)
        results.append((test_name, success))
        print()
    
    # Summarize results
    print("=" * 60)
    print("TEST RESULTS SUMMARY")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{test_name}: {status}")
        if success:
            passed += 1
        else:
            failed += 1
    
    print("-" * 60)
    print(f"Total: {len(results)} test suite(s)")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Success Rate: {(passed/len(results)*100):.1f}%")
    
    if failed == 0:
        print("\n🎉 All tests passed!")
    else:
        print(f"\n💥 {failed} test suite(s) failed!")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == '--all':
        run_all_tests()
    else:
        main()
