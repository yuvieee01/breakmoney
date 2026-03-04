from django.contrib import admin
from .models import Expense, ExpenseParticipant

class ExpenseParticipantInline(admin.TabularInline):
    model = ExpenseParticipant
    extra = 0

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('description', 'amount', 'group', 'date', 'split_type')
    list_filter = ('split_type', 'category', 'date')
    search_fields = ('description', 'notes')
    inlines = [ExpenseParticipantInline]