"""
ProductsAndStock Test Runner
This file runs all ProductsAndStock tests and reports results.
"""

import os
import sys
import django
import unittest
from django.test.runner import DiscoverRunner
from django.conf import settings

# Load Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djcrm.settings')
django.setup()


class ProductsAndStockTestRunner:
    """ProductsAndStock test runner class"""
    
    def __init__(self):
        self.test_results = {}
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.errors = 0
    
    def run_all_tests(self):
        """Run all tests"""
        print("=" * 80)
        print("🚀 PRODUCTSANDSTOCK COMPREHENSIVE TEST SYSTEM")
        print("=" * 80)
        print()
        
        # Define test files
        test_files = [
            ('Model Tests', 'test_products_stock_models'),
            ('View Tests', 'test_products_stock_views'),
            ('Form Tests', 'test_products_stock_forms'),
            ('Integration Tests', 'test_products_stock_integration'),
        ]
        
        for test_name, test_module in test_files:
            print(f"🔍 Running {test_name}...")
            print("-" * 60)
            
            try:
                # Import test module
                module = __import__(f'test.{test_module}', fromlist=[test_module])
                
                # Create test suite
                loader = unittest.TestLoader()
                suite = loader.loadTestsFromModule(module)
                
                # Run tests
                runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
                result = runner.run(suite)
                
                # Save results
                self.test_results[test_name] = {
                    'tests_run': result.testsRun,
                    'failures': len(result.failures),
                    'errors': len(result.errors),
                    'success': result.wasSuccessful()
                }
                
                self.total_tests += result.testsRun
                self.passed_tests += result.testsRun - len(result.failures) - len(result.errors)
                self.failed_tests += len(result.failures)
                self.errors += len(result.errors)
                
                # Show status
                if result.wasSuccessful():
                    print(f"✅ {test_name} SUCCESSFUL")
                else:
                    print(f"❌ {test_name} FAILED")
                
                print()
                
            except Exception as e:
                print(f"❌ {test_name} ERROR: {str(e)}")
                self.test_results[test_name] = {
                    'tests_run': 0,
                    'failures': 0,
                    'errors': 1,
                    'success': False
                }
                self.errors += 1
                print()
        
        self.print_summary()
    
    def run_specific_test(self, test_name):
        """Run a specific test file"""
        print(f"🔍 Running {test_name}...")
        print("-" * 60)
        
        test_modules = {
            'models': 'test_products_stock_models',
            'views': 'test_products_stock_views',
            'forms': 'test_products_stock_forms',
            'integration': 'test_products_stock_integration',
        }
        
        if test_name.lower() not in test_modules:
            print(f"❌ Unknown test: {test_name}")
            print("Available tests: models, views, forms, integration")
            return False
        
        try:
            module_name = test_modules[test_name.lower()]
            module = __import__(f'test.{module_name}', fromlist=[module_name])
            
            loader = unittest.TestLoader()
            suite = loader.loadTestsFromModule(module)
            
            runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
            result = runner.run(suite)
            
            if result.wasSuccessful():
                print(f"✅ {test_name} SUCCESSFUL")
                return True
            else:
                print(f"❌ {test_name} FAILED")
                return False
                
        except Exception as e:
            print(f"❌ {test_name} ERROR: {str(e)}")
            return False
    
    def run_model_tests(self):
        """Run model tests only"""
        return self.run_specific_test('models')
    
    def run_view_tests(self):
        """Run view tests only"""
        return self.run_specific_test('views')
    
    def run_form_tests(self):
        """Run form tests only"""
        return self.run_specific_test('forms')
    
    def run_integration_tests(self):
        """Run integration tests only"""
        return self.run_specific_test('integration')
    
    def print_summary(self):
        """Summarize test results"""
        print("=" * 80)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 80)
        print()
        
        # Result for each test file
        for test_name, result in self.test_results.items():
            status = "✅ SUCCESSFUL" if result['success'] else "❌ FAILED"
            print(f"{test_name:<25} {status}")
            print(f"  Test Count: {result['tests_run']}")
            print(f"  Errors: {result['errors']}")
            print(f"  Failed: {result['failures']}")
            print()
        
        # General statistics
        print("-" * 80)
        print("📈 GENERAL STATISTICS")
        print("-" * 80)
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.failed_tests}")
        print(f"Errors: {self.errors}")
        
        if self.total_tests > 0:
            success_rate = (self.passed_tests / self.total_tests) * 100
            print(f"Success Rate: %{success_rate:.1f}")
        
        print()
        
        # Overall status
        if self.failed_tests == 0 and self.errors == 0:
            print("🎉 ALL TESTS SUCCESSFUL!")
        elif self.failed_tests > 0 or self.errors > 0:
            print("⚠️  SOME TESTS FAILED!")
        
        print("=" * 80)
    
    def run_quick_tests(self):
        """Quick tests (basic tests only)"""
        print("🚀 RUNNING QUICK TESTS...")
        print("=" * 50)
        
        # Run model tests only
        return self.run_model_tests()
    
    def run_performance_tests(self):
        """Performance tests"""
        print("⚡ RUNNING PERFORMANCE TESTS...")
        print("=" * 50)
        
        # Run integration tests only (includes performance tests)
        return self.run_integration_tests()


def main():
    """Main function"""
    runner = ProductsAndStockTestRunner()
    
    print("ProductsAndStock Test System")
    print("=" * 40)
    print("1. Run all tests")
    print("2. Model tests")
    print("3. View tests")
    print("4. Form tests")
    print("5. Integration tests")
    print("6. Quick tests")
    print("7. Performance tests")
    print("8. Exit")
    print()
    
    while True:
        try:
            choice = input("Enter your choice (1-8): ").strip()
            
            if choice == "1":
                runner.run_all_tests()
            elif choice == "2":
                runner.run_model_tests()
            elif choice == "3":
                runner.run_view_tests()
            elif choice == "4":
                runner.run_form_tests()
            elif choice == "5":
                runner.run_integration_tests()
            elif choice == "6":
                runner.run_quick_tests()
            elif choice == "7":
                runner.run_performance_tests()
            elif choice == "8":
                print("Exiting...")
                break
            else:
                print("Invalid choice! Please enter a number between 1 and 8.")
            
            print("\n" + "=" * 50)
            
        except KeyboardInterrupt:
            print("\n\nExiting...")
            break
        except Exception as e:
            print(f"\nError: {str(e)}")


if __name__ == "__main__":
    main()
