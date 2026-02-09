from django.contrib import admin
from django.contrib.auth import get_user_model
from .models import Task, Notification

User = get_user_model()


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'task', 'is_read', 'action_label', 'action_url', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('title', 'message')


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'assigned_to', 'assigned_by', 'organisation', 'status', 'priority', 'start_date', 'end_date')
    list_filter = ('status', 'priority', 'organisation')
    search_fields = ('title', 'content')
    date_hierarchy = 'start_date'

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'assigned_to' and request.user.is_authenticated:
            # Exclude current user so admin cannot assign tasks to themselves
            kwargs['queryset'] = kwargs.get('queryset', User.objects.all()).exclude(pk=request.user.pk)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
