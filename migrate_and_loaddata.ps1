# PostgreSQL kurduktan ve .env'deki DB_PASSWORD'u güncelledikten sonra calistir.
# Proje klasorunde: .\migrate_and_loaddata.ps1

Write-Host "Migration calistiriliyor..." -ForegroundColor Cyan
python manage.py migrate
if ($LASTEXITCODE -ne 0) {
    Write-Host "HATA: migrate basarisiz. PostgreSQL kurulu mu? .env'de DB_PASSWORD dogru mu?" -ForegroundColor Red
    exit 1
}

Write-Host "`nVeri yukleniyor (backup.json)..." -ForegroundColor Cyan
python manage.py loaddata backup.json --ignorenonexistent
if ($LASTEXITCODE -ne 0) {
    Write-Host "loaddata hata verdi. Deniyorum: loaddata backup.json" -ForegroundColor Yellow
    python manage.py loaddata backup.json
}

Write-Host "`nTamam. Sunucuyu baslatmak icin: python manage.py runserver" -ForegroundColor Green
