"""
Login Test Runner
Bu dosya login testlerini çalıştırmak için kullanılır.
"""

import os
import sys
import django
from django.test.utils import get_runner
from django.conf import settings

# Django ayarlarını yükle
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djcrm.settings')
django.setup()

def run_login_tests():
    """Login testlerini çalıştır"""
    print("Login Test Sistemi Başlatılıyor...")
    print("=" * 60)
    
    # Test runner oluştur
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    
    # Test modülleri
    test_modules = [
        'test.login.working.test_login_views',
        'test.login.working.test_login_forms',
        'test.login.working.test_login_authentication',
        'test.login.working.test_login_integration',
    ]
    
    # Testleri çalıştır
    failures = test_runner.run_tests(test_modules, verbosity=2)
    
    if failures:
        print(f"\n❌ {failures} test başarısız!")
        return False
    else:
        print("\n✅ Tüm testler başarılı!")
        return True

def run_specific_login_test(test_name):
    """Belirli bir login testini çalıştır"""
    print(f"Login Test Çalıştırılıyor: {test_name}")
    print("=" * 60)
    
    # Test runner oluştur
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    
    # Test modülü
    test_module = f'test.login.working.{test_name}'
    
    # Testi çalıştır
    failures = test_runner.run_tests([test_module], verbosity=2)
    
    if failures:
        print(f"\n❌ {failures} test başarısız!")
        return False
    else:
        print("\n✅ Test başarılı!")
        return True

def run_login_view_tests():
    """Login view testlerini çalıştır"""
    return run_specific_login_test('test_login_views')

def run_login_form_tests():
    """Login form testlerini çalıştır"""
    return run_specific_login_test('test_login_forms')

def run_login_authentication_tests():
    """Login authentication testlerini çalıştır"""
    return run_specific_login_test('test_login_authentication')

def run_login_integration_tests():
    """Login entegrasyon testlerini çalıştır"""
    return run_specific_login_test('test_login_integration')

def show_test_menu():
    """Test menüsünü göster"""
    print("\nLogin Test Menüsü")
    print("=" * 30)
    print("1. Tüm login testleri")
    print("2. Login view testleri")
    print("3. Login form testleri")
    print("4. Login authentication testleri")
    print("5. Login entegrasyon testleri")
    print("6. Çıkış")
    print("=" * 30)

def main():
    """Ana fonksiyon"""
    while True:
        show_test_menu()
        choice = input("\nSeçiminizi yapın (1-6): ").strip()
        
        if choice == '1':
            run_login_tests()
        elif choice == '2':
            run_login_view_tests()
        elif choice == '3':
            run_login_form_tests()
        elif choice == '4':
            run_login_authentication_tests()
        elif choice == '5':
            run_login_integration_tests()
        elif choice == '6':
            print("Çıkılıyor...")
            break
        else:
            print("Geçersiz seçim! Lütfen 1-6 arasında bir sayı girin.")
        
        input("\nDevam etmek için Enter'a basın...")

if __name__ == "__main__":
    main()
