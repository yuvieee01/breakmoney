from django.contrib import admin
from .models import ActivityLog

@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'user', 'action_type', 'description', 'group')
    list_filter = ('action_type', 'created_at', 'group')
    search_fields = ('description', 'user__email')