"""
Signup Test Runner
Bu dosya signup testlerini çalıştırmak için kullanılır.
"""

import os
import sys
import django
from django.test.utils import get_runner
from django.conf import settings

# Django ayarlarını yükle
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djcrm.settings')
django.setup()

def run_signup_tests():
    """Signup testlerini çalıştır"""
    print("🚀 Signup Testleri Başlatılıyor...")
    print("=" * 60)
    
    # Test runner oluştur
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    
    # Test modüllerini tanımla
    test_modules = [
        'test.signup.working_tests.test_signup_forms',
        'test.signup.working_tests.test_signup_views', 
        'test.signup.working_tests.test_signup_models',
        'test.signup.working_tests.test_signup_integration',
    ]
    
    print("📋 Çalıştırılacak Test Modülleri:")
    for module in test_modules:
        print(f"  - {module}")
    print()
    
    # Testleri çalıştır
    failures = test_runner.run_tests(test_modules, verbosity=2)
    
    print("\n" + "=" * 60)
    if failures == 0:
        print("✅ Tüm signup testleri başarıyla geçti!")
    else:
        print(f"❌ {failures} test başarısız oldu!")
    
    return failures

def run_specific_test(test_name):
    """Belirli bir testi çalıştır"""
    print(f"🎯 {test_name} testi çalıştırılıyor...")
    print("=" * 60)
    
    # Test runner oluştur
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    
    # Belirli testi çalıştır
    failures = test_runner.run_tests([test_name], verbosity=2)
    
    print("\n" + "=" * 60)
    if failures == 0:
        print(f"✅ {test_name} testi başarıyla geçti!")
    else:
        print(f"❌ {test_name} testi başarısız oldu!")
    
    return failures

def run_form_tests():
    """Sadece form testlerini çalıştır"""
    return run_specific_test('test.signup.working_tests.test_signup_forms')

def run_view_tests():
    """Sadece view testlerini çalıştır"""
    return run_specific_test('test.signup.working_tests.test_signup_views')

def run_model_tests():
    """Sadece model testlerini çalıştır"""
    return run_specific_test('test.signup.working_tests.test_signup_models')

def run_integration_tests():
    """Sadece entegrasyon testlerini çalıştır"""
    return run_specific_test('test.signup.working_tests.test_signup_integration')

def interactive_test_runner():
    """İnteraktif test çalıştırıcı"""
    while True:
        print("\n🔧 Signup Test Çalıştırıcı")
        print("=" * 40)
        print("1. Tüm testleri çalıştır")
        print("2. Form testlerini çalıştır")
        print("3. View testlerini çalıştır")
        print("4. Model testlerini çalıştır")
        print("5. Entegrasyon testlerini çalıştır")
        print("6. Belirli bir test çalıştır")
        print("0. Çıkış")
        print("-" * 40)
        
        choice = input("Seçiminizi yapın (0-6): ").strip()
        
        if choice == '0':
            print("👋 Test çalıştırıcısından çıkılıyor...")
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
            test_name = input("Test adını girin: ").strip()
            if test_name:
                run_specific_test(test_name)
            else:
                print("❌ Geçersiz test adı!")
        else:
            print("❌ Geçersiz seçim!")

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
            print("❌ Geçersiz komut!")
            print("Kullanım: python test_runner.py [all|forms|views|models|integration|interactive]")
    else:
        # Varsayılan olarak tüm testleri çalıştır
        run_signup_tests()
