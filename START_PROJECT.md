# Django CRM Projesi Başlatma Rehberi

## Projeyi Sıfırdan Başlatmak İçin Gerekli Komutlar

### 1. Terminal/PowerShell'i açın ve proje klasörüne gidin:
```powershell
cd "C:\Users\berka\Desktop\GITHUB REPOSITORıES\env"
```

### 2. Django sunucusunu başlatın:
```powershell
.\new_env\Scripts\python.exe manage.py runserver
```

### 3. Tarayıcınızda şu adrese gidin:
```
http://127.0.0.1:8000/
```

## Alternatif Komutlar (Eğer yukarıdaki çalışmazsa):

### Eğer Python modülü bulunamazsa:
```powershell
# Önce gerekli paketleri yükleyin
.\new_env\Scripts\python.exe -m pip install -r requirements.txt

# Sonra sunucuyu başlatın
.\new_env\Scripts\python.exe manage.py runserver
```

### Eğer port meşgulse:
```powershell
# Çalışan Python işlemlerini durdurun
taskkill /f /im python.exe

# Sonra sunucuyu başlatın
.\new_env\Scripts\python.exe manage.py runserver
```

## Tek Komut ile Başlatma (Önerilen):
```powershell
cd "C:\Users\berka\Desktop\GITHUB REPOSITORıES\env" && .\new_env\Scripts\python.exe manage.py runserver
```

## Not:
- Sunucuyu durdurmak için terminal'de `Ctrl+C` tuşlarına basın
- Proje http://127.0.0.1:8000/ adresinde çalışacak
- Eğer hata alırsanız, önce `taskkill /f /im python.exe` komutunu çalıştırın
