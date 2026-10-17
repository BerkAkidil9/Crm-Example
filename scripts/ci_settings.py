"""Disposable settings for project checks; never use for deployment."""
import os
from pathlib import Path

from djcrm.settings import *  # noqa: F403

_work = Path(os.environ['CRM_CHECK_DIR'])
DATABASES = {'default': {
    'ENGINE': 'django.db.backends.sqlite3',
    'NAME': _work / 'checks.sqlite3',
    'TEST': {'NAME': ':memory:'},
}}
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
MEDIA_ROOT = _work / 'media' / str(os.getpid())
STATIC_ROOT = _work / 'static'
STORAGES = {
    'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
    'staticfiles': {'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage'},
}
USE_R2 = False
TEST_RUNNER = 'scripts.ci_runner.ShardedDiscoverRunner'
