from django.db import models
from django.conf import settings
from groups.models import Group

class Settlement(models.Model):
    payer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payments_made')
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payments_received')
    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True, blank=True, related_name='settlements')
    
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    notes = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.payer.email} paid {self.receiver.email} ₹{self.amount}"