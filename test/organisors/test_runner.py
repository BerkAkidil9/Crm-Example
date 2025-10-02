"""
Organisors Test Runner
Bu dosya organisors modülündeki tüm testleri çalıştırır.
"""

import os
import sys
import django
from django.test.utils import get_runner
from django.conf import settings

# Django ayarlarını yükle
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djcrm.settings')
django.setup()

def run_organisor_tests():
    """Organisor testlerini çalıştır"""
    print("Organisors Test Sistemi")
    print("=" * 60)
    
    # Test runner oluştur
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    
    # Test modülleri
    test_modules = [
        'test.organisors.working_tests.test_models',
        'test.organisors.working_tests.test_forms',
        'test.organisors.working_tests.test_views',
        'test.organisors.working_tests.test_mixins',
        'test.organisors.working_tests.test_integration',
    ]
    
    print("Çalıştırılacak Test Modülleri:")
    for module in test_modules:
        print(f"  - {module}")
    print()
    
    # Testleri çalıştır
    failures = test_runner.run_tests(test_modules, verbosity=2)
    
    if failures:
        print(f"\n❌ {failures} test başarısız oldu!")
        return False
    else:
        print("\n✅ Tüm testler başarılı!")
        return True

def run_specific_test(test_module):
    """Belirli bir test modülünü çalıştır"""
    print(f"Organisors {test_module} Testleri")
    print("=" * 60)
    
    # Test runner oluştur
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    
    # Test modülü
    test_module_path = f'test.organisors.working_tests.{test_module}'
    
    print(f"Çalıştırılan Test Modülü: {test_module_path}")
    print()
    
    # Testi çalıştır
    failures = test_runner.run_tests([test_module_path], verbosity=2)
    
    if failures:
        print(f"\n❌ {failures} test başarısız oldu!")
        return False
    else:
        print("\n✅ Tüm testler başarılı!")
        return True

def run_model_tests():
    """Model testlerini çalıştır"""
    return run_specific_test('test_models')

def run_form_tests():
    """Form testlerini çalıştır"""
    return run_specific_test('test_forms')

def run_view_tests():
    """View testlerini çalıştır"""
    return run_specific_test('test_views')

def run_mixin_tests():
    """Mixin testlerini çalıştır"""
    return run_specific_test('test_mixins')

def run_integration_tests():
    """Entegrasyon testlerini çalıştır"""
    return run_specific_test('test_integration')

def show_test_menu():
    """Test menüsünü göster"""
    print("\nOrganisors Test Menüsü")
    print("=" * 30)
    print("1. Tüm testleri çalıştır")
    print("2. Model testlerini çalıştır")
    print("3. Form testlerini çalıştır")
    print("4. View testlerini çalıştır")
    print("5. Mixin testlerini çalıştır")
    print("6. Entegrasyon testlerini çalıştır")
    print("0. Çıkış")
    print()

def main():
    """Ana fonksiyon"""
    while True:
        show_test_menu()
        choice = input("Seçiminizi yapın (0-6): ").strip()
        
        if choice == '0':
            print("Çıkılıyor...")
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
            print("Geçersiz seçim! Lütfen 0-6 arasında bir sayı girin.")
        
        input("\nDevam etmek için Enter'a basın...")

if __name__ == "__main__":
    # Komut satırı argümanları kontrol et
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
            print("Geçersiz argüman! Kullanım:")
            print("python test_runner.py [all|models|forms|views|mixins|integration]")
    else:
        # İnteraktif menü
        main()
