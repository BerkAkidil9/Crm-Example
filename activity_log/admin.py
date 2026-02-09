from django.contrib import admin
from .models import ActivityLog


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'object_type', 'object_repr', 'organisation', 'affected_agent', 'created_at')
    list_filter = ('action', 'object_type', 'created_at')
    search_fields = ('object_repr', 'user__username', 'user__email')
    readonly_fields = ('user', 'action', 'object_type', 'object_id', 'object_repr', 'details', 'organisation', 'affected_agent', 'created_at')
    date_hierarchy = 'created_at'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
