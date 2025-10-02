"""
Agent Test Runner
Bu dosya agent testlerini çalıştırmak için kullanılır.
"""

import os
import sys
import django
from django.test.utils import get_runner
from django.conf import settings

# Django ayarlarını yükle
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djcrm.settings')
django.setup()

def run_agent_tests():
    """Agent testlerini çalıştır"""
    print("Agent Testleri Başlatılıyor...")
    print("=" * 60)
    
    # Test runner oluştur
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    
    # Test modüllerini tanımla
    test_modules = [
        'test.agents.working_tests.test_models',
        'test.agents.working_tests.test_forms',
        'test.agents.working_tests.test_views',
        'test.agents.working_tests.test_mixins',
        'test.agents.working_tests.test_integration',
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
    print(f"Agent Test Modülü Çalıştırılıyor: {test_module}")
    print("=" * 60)
    
    # Test runner oluştur
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    
    # Testi çalıştır
    failures = test_runner.run_tests([test_module], verbosity=2)
    
    if failures:
        print(f"\n❌ {failures} test başarısız!")
        return False
    else:
        print("\n✅ Test başarılı!")
        return True

def run_model_tests():
    """Model testlerini çalıştır"""
    return run_specific_test('test.agents.working_tests.test_models')

def run_form_tests():
    """Form testlerini çalıştır"""
    return run_specific_test('test.agents.working_tests.test_forms')

def run_view_tests():
    """View testlerini çalıştır"""
    return run_specific_test('test.agents.working_tests.test_views')

def run_mixin_tests():
    """Mixin testlerini çalıştır"""
    return run_specific_test('test.agents.working_tests.test_mixins')

def run_integration_tests():
    """Entegrasyon testlerini çalıştır"""
    return run_specific_test('test.agents.working_tests.test_integration')

def show_test_menu():
    """Test menüsünü göster"""
    print("\n" + "=" * 60)
    print("AGENT TEST MENÜSÜ")
    print("=" * 60)
    print("1. Tüm testleri çalıştır")
    print("2. Model testleri")
    print("3. Form testleri")
    print("4. View testleri")
    print("5. Mixin testleri")
    print("6. Entegrasyon testleri")
    print("7. Çıkış")
    print("=" * 60)

def main():
    """Ana fonksiyon"""
    while True:
        show_test_menu()
        
        try:
            choice = input("\nSeçiminizi yapın (1-7): ").strip()
            
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
                print("Çıkılıyor...")
                break
            else:
                print("❌ Geçersiz seçim! Lütfen 1-7 arası bir sayı girin.")
            
            input("\nDevam etmek için Enter'a basın...")
            
        except KeyboardInterrupt:
            print("\n\nÇıkılıyor...")
            break
        except Exception as e:
            print(f"\n❌ Hata oluştu: {e}")
            input("\nDevam etmek için Enter'a basın...")

if __name__ == "__main__":
    main()
