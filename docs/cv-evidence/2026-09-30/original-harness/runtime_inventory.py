import os,sys,json,inspect
from pathlib import Path
sys.path.insert(0,'/Users/berkakidil/Desktop/Crm-Example')
sys.argv=['manage.py','test']
os.environ.update(DJANGO_SETTINGS_MODULE='audit_settings',DEBUG='True',SECRET_KEY='local-audit-key',USE_R2='false',USE_GMAIL_API='false')
import django
django.setup()
from django.apps import apps
from django.urls import URLPattern, URLResolver,get_resolver
local={'leads','agents','organisors','ProductsAndStock','orders','finance','tasks','activity_log'}
models=[{'app':m._meta.app_label,'name':m.__name__,'file':inspect.getsourcefile(m),'line':inspect.getsourcelines(m)[1]} for m in apps.get_models() if m._meta.app_label in local and not m._meta.abstract and not m._meta.proxy]
routes=[]
def walk(items,prefix=''):
 for item in items:
  if isinstance(item,URLResolver):
   if item.app_name=='admin':continue
   walk(item.url_patterns,prefix+str(item.pattern))
  elif isinstance(item,URLPattern) and item.callback.__module__!='django.views.static': routes.append({'path':prefix+str(item.pattern),'name':item.name})
walk(get_resolver().url_patterns)
out={'models':models,'routes':routes}
Path('/private/tmp/crm-cv-audit/runtime-inventory.json').write_text(json.dumps(out,indent=2))
print('Registered local concrete models:',len(models),'Application leaf URL patterns:',len(routes))
