"""
Forget Password Test Runner
Bu dosya forget password testlerini çalıştırmak için kullanılır.
"""

import os
import sys
import django
from django.test.utils import get_runner
from django.conf import settings

# Django ayarlarını yükle
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djcrm.settings')
django.setup()

def run_forget_password_tests():
    """Forget password testlerini çalıştır"""
    print("Forget Password Testleri Başlatılıyor...")
    print("=" * 60)
    
    # Test runner oluştur
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    
    # Test modülleri
    test_modules = [
        'test.forget_password.test_forget_password_views',
        'test.forget_password.test_forget_password_forms',
    ]
    
    # Testleri çalıştır
    failures = test_runner.run_tests(test_modules, verbosity=2)
    
    if failures:
        print(f"\n❌ {failures} test başarısız!")
        return False
    else:
        print("\n✅ Tüm testler başarılı!")
        return True

def run_specific_test(test_name):
    """Belirli bir testi çalıştır"""
    print(f"Forget Password Testi Çalıştırılıyor: {test_name}")
    print("=" * 60)
    
    # Test runner oluştur
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    
    # Belirli testi çalıştır
    failures = test_runner.run_tests([test_name], verbosity=2)
    
    if failures:
        print(f"\n❌ Test başarısız!")
        return False
    else:
        print("\n✅ Test başarılı!")
        return True

def run_view_tests():
    """Sadece view testlerini çalıştır"""
    return run_specific_test('test.forget_password.test_forget_password_views')

def run_form_tests():
    """Sadece form testlerini çalıştır"""
    return run_specific_test('test.forget_password.test_forget_password_forms')

def run_integration_tests():
    """Sadece entegrasyon testlerini çalıştır"""
    print("Forget Password Entegrasyon Testleri Çalıştırılıyor...")
    print("=" * 60)
    
    # Test runner oluştur
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    
    # Sadece entegrasyon testlerini çalıştır
    test_modules = [
        'test.forget_password.test_forget_password_views.TestForgetPasswordIntegration',
        'test.forget_password.test_forget_password_forms.TestForgetPasswordFormIntegration',
    ]
    
    failures = test_runner.run_tests(test_modules, verbosity=2)
    
    if failures:
        print(f"\n❌ {failures} entegrasyon testi başarısız!")
        return False
    else:
        print("\n✅ Tüm entegrasyon testleri başarılı!")
        return True

def show_test_menu():
    """Test menüsünü göster"""
    print("\n" + "=" * 60)
    print("FORGET PASSWORD TEST MENÜSÜ")
    print("=" * 60)
    print("1. Tüm testleri çalıştır")
    print("2. Sadece view testlerini çalıştır")
    print("3. Sadece form testlerini çalıştır")
    print("4. Sadece entegrasyon testlerini çalıştır")
    print("5. Belirli bir testi çalıştır")
    print("6. Test istatistikleri")
    print("0. Çıkış")
    print("=" * 60)

def show_test_statistics():
    """Test istatistiklerini göster"""
    print("\n" + "=" * 60)
    print("FORGET PASSWORD TEST İSTATİSTİKLERİ")
    print("=" * 60)
    
    # Test dosyalarını kontrol et
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
                
                # Test class sayısı
                class_count = content.count('class Test')
                test_classes += class_count
                
                # Test method sayısı
                method_count = content.count('def test_')
                total_tests += method_count
                
                print(f"📁 {test_file}:")
                print(f"   - Test Sınıfları: {class_count}")
                print(f"   - Test Metodları: {method_count}")
    
    print(f"\n📊 TOPLAM İSTATİSTİKLER:")
    print(f"   - Toplam Test Sınıfı: {test_classes}")
    print(f"   - Toplam Test Metodu: {total_tests}")
    print(f"   - Test Dosyası: {len(test_files)}")
    
    print(f"\n📋 TEST KAPSAMI:")
    print(f"   ✅ CustomPasswordResetView testleri")
    print(f"   ✅ PasswordResetDoneView testleri")
    print(f"   ✅ CustomPasswordResetConfirmView testleri")
    print(f"   ✅ PasswordResetCompleteView testleri")
    print(f"   ✅ CustomPasswordResetForm testleri")
    print(f"   ✅ CustomSetPasswordForm testleri")
    print(f"   ✅ Entegrasyon testleri")
    print(f"   ✅ Güvenlik testleri")
    print(f"   ✅ Edge case testleri")

def main():
    """Ana fonksiyon"""
    while True:
        show_test_menu()
        
        try:
            choice = input("\nSeçiminizi yapın (0-6): ").strip()
            
            if choice == '0':
                print("Çıkılıyor...")
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
                test_name = input("Test adını girin (örn: test.forget_password.test_forget_password_views.TestCustomPasswordResetView): ").strip()
                if test_name:
                    run_specific_test(test_name)
                else:
                    print("❌ Geçersiz test adı!")
            elif choice == '6':
                show_test_statistics()
            else:
                print("❌ Geçersiz seçim! Lütfen 0-6 arası bir sayı girin.")
            
            input("\nDevam etmek için Enter'a basın...")
            
        except KeyboardInterrupt:
            print("\n\nÇıkılıyor...")
            break
        except Exception as e:
            print(f"\n❌ Hata: {e}")
            input("Devam etmek için Enter'a basın...")

if __name__ == "__main__":
    main()
