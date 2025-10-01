"""
ProductsAndStock Test Çalıştırıcı
Bu dosya tüm ProductsAndStock testlerini çalıştırır ve sonuçları raporlar.
"""

import os
import sys
import django
import unittest
from django.test.runner import DiscoverRunner
from django.conf import settings

# Django ayarlarını yükle
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djcrm.settings')
django.setup()


class ProductsAndStockTestRunner:
    """ProductsAndStock test çalıştırıcı sınıfı"""
    
    def __init__(self):
        self.test_results = {}
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.errors = 0
    
    def run_all_tests(self):
        """Tüm testleri çalıştır"""
        print("=" * 80)
        print("🚀 PRODUCTSANDSTOCK KAPSAMLI TEST SİSTEMİ")
        print("=" * 80)
        print()
        
        # Test dosyalarını tanımla
        test_files = [
            ('Modeller Testleri', 'test_products_stock_models'),
            ('Viewlar Testleri', 'test_products_stock_views'),
            ('Formlar Testleri', 'test_products_stock_forms'),
            ('Entegrasyon Testleri', 'test_products_stock_integration'),
        ]
        
        for test_name, test_module in test_files:
            print(f"🔍 {test_name} çalıştırılıyor...")
            print("-" * 60)
            
            try:
                # Test modülünü import et
                module = __import__(f'test.{test_module}', fromlist=[test_module])
                
                # Test suite oluştur
                loader = unittest.TestLoader()
                suite = loader.loadTestsFromModule(module)
                
                # Test çalıştır
                runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
                result = runner.run(suite)
                
                # Sonuçları kaydet
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
                
                # Durum göster
                if result.wasSuccessful():
                    print(f"✅ {test_name} BAŞARILI")
                else:
                    print(f"❌ {test_name} BAŞARISIZ")
                
                print()
                
            except Exception as e:
                print(f"❌ {test_name} HATASI: {str(e)}")
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
        """Belirli bir test dosyasını çalıştır"""
        print(f"🔍 {test_name} çalıştırılıyor...")
        print("-" * 60)
        
        test_modules = {
            'modeller': 'test_products_stock_models',
            'viewlar': 'test_products_stock_views',
            'formlar': 'test_products_stock_forms',
            'entegrasyon': 'test_products_stock_integration',
        }
        
        if test_name.lower() not in test_modules:
            print(f"❌ Bilinmeyen test: {test_name}")
            print("Mevcut testler: modeller, viewlar, formlar, entegrasyon")
            return False
        
        try:
            module_name = test_modules[test_name.lower()]
            module = __import__(f'test.{module_name}', fromlist=[module_name])
            
            loader = unittest.TestLoader()
            suite = loader.loadTestsFromModule(module)
            
            runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
            result = runner.run(suite)
            
            if result.wasSuccessful():
                print(f"✅ {test_name} BAŞARILI")
                return True
            else:
                print(f"❌ {test_name} BAŞARISIZ")
                return False
                
        except Exception as e:
            print(f"❌ {test_name} HATASI: {str(e)}")
            return False
    
    def run_model_tests(self):
        """Sadece model testlerini çalıştır"""
        return self.run_specific_test('modeller')
    
    def run_view_tests(self):
        """Sadece view testlerini çalıştır"""
        return self.run_specific_test('viewlar')
    
    def run_form_tests(self):
        """Sadece form testlerini çalıştır"""
        return self.run_specific_test('formlar')
    
    def run_integration_tests(self):
        """Sadece entegrasyon testlerini çalıştır"""
        return self.run_specific_test('entegrasyon')
    
    def print_summary(self):
        """Test sonuçlarını özetle"""
        print("=" * 80)
        print("📊 TEST SONUÇLARI ÖZETİ")
        print("=" * 80)
        print()
        
        # Her test dosyası için sonuç
        for test_name, result in self.test_results.items():
            status = "✅ BAŞARILI" if result['success'] else "❌ BAŞARISIZ"
            print(f"{test_name:<25} {status}")
            print(f"  Test Sayısı: {result['tests_run']}")
            print(f"  Hatalar: {result['errors']}")
            print(f"  Başarısız: {result['failures']}")
            print()
        
        # Genel istatistikler
        print("-" * 80)
        print("📈 GENEL İSTATİSTİKLER")
        print("-" * 80)
        print(f"Toplam Test: {self.total_tests}")
        print(f"Başarılı: {self.passed_tests}")
        print(f"Başarısız: {self.failed_tests}")
        print(f"Hatalar: {self.errors}")
        
        if self.total_tests > 0:
            success_rate = (self.passed_tests / self.total_tests) * 100
            print(f"Başarı Oranı: %{success_rate:.1f}")
        
        print()
        
        # Genel durum
        if self.failed_tests == 0 and self.errors == 0:
            print("🎉 TÜM TESTLER BAŞARILI!")
        elif self.failed_tests > 0 or self.errors > 0:
            print("⚠️  BAZI TESTLER BAŞARISIZ!")
        
        print("=" * 80)
    
    def run_quick_tests(self):
        """Hızlı testler (sadece temel testler)"""
        print("🚀 HIZLI TESTLER ÇALIŞTIRILIYOR...")
        print("=" * 50)
        
        # Sadece model testlerini çalıştır
        return self.run_model_tests()
    
    def run_performance_tests(self):
        """Performans testleri"""
        print("⚡ PERFORMANS TESTLERİ ÇALIŞTIRILIYOR...")
        print("=" * 50)
        
        # Sadece entegrasyon testlerini çalıştır (performans testleri içerir)
        return self.run_integration_tests()


def main():
    """Ana fonksiyon"""
    runner = ProductsAndStockTestRunner()
    
    print("ProductsAndStock Test Sistemi")
    print("=" * 40)
    print("1. Tüm testleri çalıştır")
    print("2. Model testleri")
    print("3. View testleri")
    print("4. Form testleri")
    print("5. Entegrasyon testleri")
    print("6. Hızlı testler")
    print("7. Performans testleri")
    print("8. Çıkış")
    print()
    
    while True:
        try:
            choice = input("Seçiminizi yapın (1-8): ").strip()
            
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
                print("Çıkılıyor...")
                break
            else:
                print("Geçersiz seçim! Lütfen 1-8 arası bir sayı girin.")
            
            print("\n" + "=" * 50)
            
        except KeyboardInterrupt:
            print("\n\nÇıkılıyor...")
            break
        except Exception as e:
            print(f"\nHata: {str(e)}")


if __name__ == "__main__":
    main()
