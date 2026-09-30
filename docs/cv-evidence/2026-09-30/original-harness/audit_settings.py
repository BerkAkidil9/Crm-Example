from djcrm.settings import *
DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': ':memory:'}}
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
MEDIA_ROOT = '/private/tmp/crm-cv-audit/media'
STATIC_ROOT = '/private/tmp/crm-cv-audit/static'
# Keep production password hashers; no application logic overrides.
