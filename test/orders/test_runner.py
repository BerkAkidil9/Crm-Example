#!/usr/bin/env python3
"""
Orders Test Runner
Bu script orders modülü için testleri çalıştırır.
"""

import os
import sys
import django
import subprocess
import time

# Django ayarlarını yükle
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djcrm.settings')
django.setup()

def run_test_command(test_path, verbose=False):
    """Test komutunu çalıştır"""
    cmd = ['python', 'manage.py', 'test', test_path]
    if verbose:
        cmd.append('-v')
        cmd.append('2')
    
    print(f"Çalıştırılan komut: {' '.join(cmd)}")
    print("-" * 60)
    
    start_time = time.time()
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=os.getcwd())
        end_time = time.time()
        
        print(f"Test süresi: {end_time - start_time:.2f} saniye")
        print("-" * 60)
        
        if result.returncode == 0:
            print("✅ Test başarılı!")
            print(result.stdout)
        else:
            print("❌ Test başarısız!")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
        
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Test çalıştırma hatası: {e}")
        return False

def main():
    """Ana fonksiyon"""
    print("Orders Test Runner")
    print("=" * 60)
    print()
    
    # Test seçenekleri
    tests = {
        '1': {
            'name': 'Model Testleri',
            'path': 'test.orders.working_tests.test_models',
            'description': 'Orders modelleri için testler'
        },
        '2': {
            'name': 'View Testleri',
            'path': 'test.orders.working_tests.test_views',
            'description': 'Orders view\'ları için testler'
        },
        '3': {
            'name': 'Form Testleri',
            'path': 'test.orders.working_tests.test_forms',
            'description': 'Orders form\'ları için testler'
        },
        '4': {
            'name': 'Entegrasyon Testleri',
            'path': 'test.orders.working_tests.test_integration',
            'description': 'Orders entegrasyon testleri'
        },
        '5': {
            'name': 'Tüm Testler',
            'path': 'test.orders.working_tests',
            'description': 'Tüm orders testleri'
        }
    }
    
    while True:
        print("Test Seçenekleri:")
        print("-" * 30)
        for key, test in tests.items():
            print(f"{key}. {test['name']}")
            print(f"   {test['description']}")
            print()
        
        print("Seçenekler:")
        print("v - Verbose mod (detaylı çıktı)")
        print("q - Çıkış")
        print()
        
        choice = input("Test seçin (1-5, v, q): ").strip().lower()
        
        if choice == 'q':
            print("Çıkılıyor...")
            break
        elif choice == 'v':
            verbose_mode = True
            print("Verbose mod aktif!")
            continue
        elif choice in tests:
            verbose_mode = getattr(main, 'verbose_mode', False)
            test_info = tests[choice]
            
            print(f"\n{test_info['name']} başlatılıyor...")
            print(f"Açıklama: {test_info['description']}")
            print()
            
            success = run_test_command(test_info['path'], verbose=verbose_mode)
            
            if success:
                print(f"\n🎉 {test_info['name']} başarıyla tamamlandı!")
            else:
                print(f"\n💥 {test_info['name']} başarısız!")
            
            print("\n" + "=" * 60)
            print()
        else:
            print("❌ Geçersiz seçim! Lütfen 1-5, v veya q girin.")
            print()

def run_all_tests():
    """Tüm testleri çalıştır"""
    print("Tüm Orders Testleri Çalıştırılıyor...")
    print("=" * 60)
    
    tests = [
        ('Model Testleri', 'test.orders.working_tests.test_models'),
        ('View Testleri', 'test.orders.working_tests.test_views'),
        ('Form Testleri', 'test.orders.working_tests.test_forms'),
        ('Entegrasyon Testleri', 'test.orders.working_tests.test_integration'),
    ]
    
    results = []
    
    for test_name, test_path in tests:
        print(f"\n{test_name} başlatılıyor...")
        success = run_test_command(test_path, verbose=True)
        results.append((test_name, success))
        print()
    
    # Sonuçları özetle
    print("=" * 60)
    print("TEST SONUÇLARI ÖZETİ")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for test_name, success in results:
        status = "✅ BAŞARILI" if success else "❌ BAŞARISIZ"
        print(f"{test_name}: {status}")
        if success:
            passed += 1
        else:
            failed += 1
    
    print("-" * 60)
    print(f"Toplam: {len(results)} test")
    print(f"Passed: {passed}")
    print(f"Başarısız: {failed}")
    print(f"Başarı Oranı: {(passed/len(results)*100):.1f}%")
    
    if failed == 0:
        print("\n🎉 Tüm testler başarılı!")
    else:
        print(f"\n💥 {failed} test başarısız!")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == '--all':
        run_all_tests()
    else:
        main()
