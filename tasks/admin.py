from django.contrib import admin
from django.contrib.auth import get_user_model
from .models import Task

User = get_user_model()


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'assigned_to', 'assigned_by', 'organisation', 'status', 'start_date', 'end_date')
    list_filter = ('status', 'organisation')
    search_fields = ('title', 'content')
    date_hierarchy = 'start_date'

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'assigned_to' and request.user.is_authenticated:
            # Exclude current user so admin cannot assign tasks to themselves
            kwargs['queryset'] = kwargs.get('queryset', User.objects.all()).exclude(pk=request.user.pk)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
