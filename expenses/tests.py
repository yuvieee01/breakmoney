from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from groups.models import Group
from .models import Expense, ExpenseParticipant
from . import services

User = get_user_model()

class ExpensesServicesTests(TestCase):
    def setUp(self):
        self.u1 = User.objects.create_user(email='u1@test.com', password='pw')
        self.u2 = User.objects.create_user(email='u2@test.com', password='pw')
        self.u3 = User.objects.create_user(email='u3@test.com', password='pw')
        self.group = Group.objects.create(name="Test Group", created_by=self.u1)

    def test_equal_split_with_pennies(self):
        """Test ₹10 split equally among 3 people. Base is 3.33. Payer should get the 0.01 remainder."""
        participants = [
            {'user': self.u1, 'amount_paid': Decimal('10.00'), 'weight': 1},
            {'user': self.u2, 'amount_paid': Decimal('0.00'), 'weight': 1},
            {'user': self.u3, 'amount_paid': Decimal('0.00'), 'weight': 1},
        ]
        
        expense = services.create_expense(
            user=self.u1, group=self.group, description="Dinner",
            amount=Decimal('10.00'), currency="USD", date="2026-01-01",
            category="FOOD", split_type="EQUAL", participants_data=participants
        )
        
        p1 = ExpenseParticipant.objects.get(expense=expense, user=self.u1)
        p2 = ExpenseParticipant.objects.get(expense=expense, user=self.u2)
        p3 = ExpenseParticipant.objects.get(expense=expense, user=self.u3)
        
        # P1 gets the extra penny because they paid
        self.assertEqual(p1.amount_owed, Decimal('3.34'))
        self.assertEqual(p2.amount_owed, Decimal('3.33'))
        self.assertEqual(p3.amount_owed, Decimal('3.33'))

    def test_exact_split_validation(self):
        """Test exact amounts must equal total."""
        participants = [
            {'user': self.u1, 'amount_paid': Decimal('100.00'), 'weight': 50},
            {'user': self.u2, 'amount_paid': Decimal('0.00'), 'weight': 40},
            # Missing 10
        ]
        
        with self.assertRaises(ValueError):
            services.create_expense(
                user=self.u1, group=self.group, description="Test",
                amount=Decimal('100.00'), currency="USD", date="2026-01-01",
                category="OTHER", split_type="EXACT", participants_data=participants
            )
