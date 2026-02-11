# Hizli test calistirma - paralel + (opsiyonel) veritabanini koru
# Kullanim: .\run_tests.ps1
#         .\run_tests.ps1 -KeepDb   (ikinci calistirmada daha da hizli)

param([switch]$KeepDb)

$args = @('test', '--parallel', '--verbosity=1')
if ($KeepDb) { $args += '--keepdb' }

& python manage.py @args
