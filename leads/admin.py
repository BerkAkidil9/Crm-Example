from django.contrib import admin

from .models import User, Lead, Agent, UserProfile, Category, SourceCategory, ValueCategory

admin.site.register(Category) 
admin.site.register(SourceCategory)
admin.site.register(ValueCategory)
admin.site.register(User)
admin.site.register(UserProfile)
admin.site.register(Lead)
admin.site.register(Agent)