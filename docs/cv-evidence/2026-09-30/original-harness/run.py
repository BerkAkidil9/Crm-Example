import os, sys, platform, json, datetime, sqlite3
from pathlib import Path
ROOT = Path('/private/tmp/crm-cv-audit')
REPO = Path('/Users/berkakidil/Desktop/Crm-Example')
sys.path.insert(0, str(REPO))
sys.dont_write_bytecode = True
for key in list(os.environ):
    if key.startswith(('DB_', 'R2_', 'GMAIL_', 'RENDER_', 'EMAIL_', 'AWS_')) or key == 'DATABASE_URL':
        del os.environ[key]
os.environ.update(DJANGO_SETTINGS_MODULE='audit_settings', SECRET_KEY='temporary-local-audit-key-not-for-deployment', DEBUG='True', USE_R2='false', USE_GMAIL_API='false', PYTHONDONTWRITEBYTECODE='1')
sys.argv = ['manage.py', 'test', '--noinput', '--verbosity=2', '--testrunner=audit_runner.Runner']
import coverage
cov = coverage.Coverage(config_file=str(ROOT / 'coverage.ini'))
cov.start()
import django
(ROOT / 'environment.json').write_text(json.dumps({'timestamp':datetime.datetime.now(datetime.timezone.utc).isoformat(), 'python':sys.version,'platform':platform.platform(),'django':django.get_version(),'sqlite':sqlite3.sqlite_version,'coverage':coverage.__version__, 'commit':'20d197814e6491b0360f941e994d8be114b0bafd'},indent=2))
from django.core.management import execute_from_command_line
try:
    execute_from_command_line(sys.argv)
finally:
    cov.stop()
    cov.save()
    cov.json_report()
    cov.html_report(directory=str(ROOT / 'htmlcov'))
    with (ROOT / 'coverage.txt').open('w') as f: cov.report(file=f)
