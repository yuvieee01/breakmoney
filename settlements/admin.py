from django.contrib import admin
from .models import Settlement

@admin.register(Settlement)
class SettlementAdmin(admin.ModelAdmin):
    list_display = ('payer', 'receiver', 'amount', 'date', 'group')
    list_filter = ('date', 'group')
    search_fields = ('payer__email', 'receiver__email', 'notes')