from django.db import models
from django.conf import settings
from groups.models import Group

class ActivityLog(models.Model):
    ACTION_CHOICES = [
        ('EXPENSE_ADDED', 'Expense Added'),
        ('EXPENSE_DELETED', 'Expense Deleted'),
        ('SETTLEMENT_ADDED', 'Payment Recorded'),
        ('SETTLEMENT_DELETED', 'Payment Deleted'),
        ('GROUP_CREATED', 'Group Created'),
        ('USER_JOINED', 'User Joined'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='activities_initiated')
    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True, blank=True, related_name='activity_logs')
    action_type = models.CharField(max_length=50, choices=ACTION_CHOICES)
    description = models.CharField(max_length=255)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.created_at.strftime('%Y-%m-%d %H:%M')} - {self.description}"