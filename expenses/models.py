from django.db import models
from django.conf import settings
from groups.models import Group

class Expense(models.Model):
    CATEGORY_CHOICES = [
        ('FOOD', 'Food & Drink'),
        ('RENT', 'Rent & Household'),
        ('TRAVEL', 'Travel & Transport'),
        ('UTILITIES', 'Utilities'),
        ('OTHER', 'Other'),
    ]
    SPLIT_TYPES = [
        ('EQUAL', 'Equally'),
        ('EXACT', 'Exact Amounts'),
        ('PERCENTAGE', 'Percentages'),
        ('SHARES', 'Shares'),
        ('ADJUSTMENT', 'By Adjustment'),
    ]

    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True, blank=True, related_name='expenses')
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='OTHER')
    split_type = models.CharField(max_length=15, choices=SPLIT_TYPES, default='EQUAL')
    notes = models.TextField(blank=True, null=True)
    receipt = models.ImageField(upload_to='receipts/', blank=True, null=True)
    
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='created_expenses')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.description} - ₹{self.amount}"

class ExpenseParticipant(models.Model):
    expense = models.ForeignKey(Expense, on_delete=models.CASCADE, related_name='participants')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    amount_owed = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    weight = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    class Meta:
        unique_together = ('expense', 'user')

    def __str__(self):
        return f"{self.user.email} in {self.expense.description} (Paid: {self.amount_paid}, Owes: {self.amount_owed})"
    
    @property
    def net_balance(self):
        return self.amount_paid - self.amount_owed