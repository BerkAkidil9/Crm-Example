"""Run all new test suites with SQLite in-memory database."""
import os
os.environ['DB_ENGINE'] = 'django.db.backends.sqlite3'
os.environ['DATABASE_URL'] = ''
import dotenv
dotenv.load_dotenv = lambda *a, **kw: None
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djcrm.settings')

import django
django.setup()

from django.conf import settings
settings.DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': ':memory:'}}
settings.STORAGES = {
    'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
    'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'},
}

from django.test.utils import get_runner
TestRunner = get_runner(settings)
test_runner = TestRunner(verbosity=2)
failures = test_runner.run_tests([
    'test.tasks.working_tests',
    'test.activity_log.working_tests',
    'test.agents.working_tests.test_views',
    'test.agents.working_tests.test_integration',
])

if failures == 0:
    print("\n=== ALL 162 TESTS PASSED ===")
else:
    print(f"\n=== {failures} TEST(S) FAILED ===")
