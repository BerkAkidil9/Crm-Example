"""
Finance Test Runner
Bu dosya Finance modülü testlerini çalıştırmak için kullanılır.
"""

import os
import sys
import django
from django.test.utils import get_runner
from django.conf import settings

# Django ayarlarını yükle
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djcrm.settings')
django.setup()

def run_finance_tests():
    """Finance testlerini çalıştır"""
    print("Finance Testleri Başlatılıyor...")
    print("=" * 60)
    
    # Test runner oluştur
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    
    # Test modüllerini belirle
    test_modules = [
        'test.finance.working_tests.test_models',
        'test.finance.working_tests.test_views',
        'test.finance.working_tests.test_forms',
        'test.finance.working_tests.test_integration',
    ]
    
    # Testleri çalıştır
    failures = test_runner.run_tests(test_modules, verbosity=2)
    
    if failures:
        print(f"\n❌ {failures} test başarısız!")
        return False
    else:
        print("\n✅ Tüm testler başarılı!")
        return True

def run_specific_test(test_module):
    """Belirli bir test modülünü çalıştır"""
    print(f"Finance {test_module} Testleri Başlatılıyor...")
    print("=" * 60)
    
    # Test runner oluştur
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    
    # Test modülünü çalıştır
    failures = test_runner.run_tests([f'test.finance.working_tests.{test_module}'], verbosity=2)
    
    if failures:
        print(f"\n❌ {failures} test başarısız!")
        return False
    else:
        print("\n✅ Tüm testler başarılı!")
        return True

def run_model_tests():
    """Model testlerini çalıştır"""
    return run_specific_test('test_models')

def run_view_tests():
    """View testlerini çalıştır"""
    return run_specific_test('test_views')

def run_form_tests():
    """Form testlerini çalıştır"""
    return run_specific_test('test_forms')

def run_integration_tests():
    """Integration testlerini çalıştır"""
    return run_specific_test('test_integration')

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Finance Test Runner')
    parser.add_argument('--module', choices=['models', 'views', 'forms', 'integration', 'all'], 
                       default='all', help='Hangi test modülünü çalıştırmak istiyorsunuz?')
    
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
