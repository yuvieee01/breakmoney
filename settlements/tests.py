from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from groups.models import Group
from .models import Settlement
from . import services

User = get_user_model()

class SettlementsTests(TestCase):
    def setUp(self):
        self.payer = User.objects.create_user(email='payer@test.com', password='pw')
        self.receiver = User.objects.create_user(email='receiver@test.com', password='pw')
        self.group = Group.objects.create(name="Test Group", created_by=self.payer)

    def test_create_settlement(self):
        settlement = services.create_settlement(
            payer=self.payer,
            receiver=self.receiver,
            amount=Decimal('50.00'),
            currency='USD',
            date='2026-01-01',
            group=self.group
        )
        self.assertEqual(settlement.amount, Decimal('50.00'))
        self.assertEqual(settlement.payer, self.payer)
        self.assertEqual(settlement.receiver, self.receiver)

    def test_cannot_settle_with_self(self):
        with self.assertRaises(ValueError):
            services.create_settlement(
                payer=self.payer,
                receiver=self.payer,
                amount=Decimal('10.00'),
                currency='USD',
                date='2026-01-01'
            )

    def test_negative_or_zero_amount_invalid(self):
        with self.assertRaises(ValueError):
            services.create_settlement(
                payer=self.payer,
                receiver=self.receiver,
                amount=Decimal('0.00'),
                currency='USD',
                date='2026-01-01'
            )

    def test_delete_settlement_permissions(self):
        settlement = services.create_settlement(
            payer=self.payer,
            receiver=self.receiver,
            amount=Decimal('50.00'),
            currency='USD',
            date='2026-01-01'
        )
        
        random_user = User.objects.create_user(email='hacker@test.com', password='pw')
        
        # Random user cannot delete
        with self.assertRaises(PermissionError):
            services.delete_settlement(settlement.id, random_user)
            
        # Payer can delete
        services.delete_settlement(settlement.id, self.payer)
        self.assertEqual(Settlement.objects.count(), 0)
