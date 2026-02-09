"""
Logout Test Runner
Bu dosya logout testlerini interaktif olarak çalıştırmayı sağlar.
"""

import os
import sys
import django

# Django ayarlarını yükle
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djcrm.settings')
django.setup()

from django.core.management import call_command
from django.test.runner import DiscoverRunner


def print_header(text):
    """Başlık yazdır"""
    print("\n" + "=" * 70)
    print(text.center(70))
    print("=" * 70 + "\n")


def print_section(text):
    """Bölüm başlığı yazdır"""
    print("\n" + "-" * 70)
    print(text)
    print("-" * 70)


def run_tests(test_label, verbosity=2):
    """Testleri çalıştır"""
    try:
        call_command('test', test_label, verbosity=verbosity)
        return True
    except SystemExit as e:
        if e.code == 0:
            return True
        return False


def main():
    """Ana test runner fonksiyonu"""
    print_header("🔐 LOGOUT TEST RUNNER 🔐")
    
    print("Logout Test Seçenekleri:")
    print("\n1. ✅ Tüm Çalışan Logout Testleri")
    print("2. 📝 Logout View Testleri")
    print("3. 🔗 Logout Entegrasyon Testleri")
    print("4. 🚀 Tüm Logout Testleri (Working)")
    print("5. ❌ Çıkış")
    
    choice = input("\nSeçiminizi yapın (1-5): ")
    
    if choice == '1':
        print_section("Tüm Çalışan Logout Testleri Çalıştırılıyor...")
        run_tests('test.logout.working', verbosity=2)
    
    elif choice == '2':
        print_section("Logout View Testleri Çalıştırılıyor...")
        run_tests('test.logout.working.test_logout_views', verbosity=2)
    
    elif choice == '3':
        print_section("Logout Entegrasyon Testleri Çalıştırılıyor...")
        run_tests('test.logout.working.test_logout_integration', verbosity=2)
    
    elif choice == '4':
        print_section("Tüm Logout Testleri Çalıştırılıyor...")
        run_tests('test.logout.working', verbosity=2)
    
    elif choice == '5':
        print("\n👋 Test runner kapatılıyor...")
        sys.exit(0)
    
    else:
        print("\n❌ Geçersiz seçim! Lütfen 1-5 arası bir sayı girin.")
        return main()
    
    # Tekrar çalıştırma seçeneği
    print("\n" + "=" * 70)
    repeat = input("Başka bir test çalıştırmak ister misiniz? (e/h): ")
    if repeat.lower() == 'e':
        return main()
    else:
        print("\n👋 Test runner kapatılıyor...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Test runner kullanıcı tarafından durduruldu.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error occurred: {e}")
        sys.exit(1)

