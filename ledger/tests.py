from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from expenses.services import create_expense
from settlements.services import create_settlement
from . import services, selectors

User = get_user_model()

class LedgerAlgorithmTests(TestCase):
    def setUp(self):
        self.u1 = User.objects.create_user(email='u1@test.com', password='pw')
        self.u2 = User.objects.create_user(email='u2@test.com', password='pw')
        self.u3 = User.objects.create_user(email='u3@test.com', password='pw')

    def test_simplification_algorithm(self):
        """
        A pays 30 for A, B, C. (B owes A 10, C owes A 10)
        B pays 30 for A, B, C. (A owes B 10, C owes B 10)
        Net should be: C owes A 10, C owes B 10. A and B are settled.
        """
        # Expense 1: U1 pays 30
        create_expense(
            user=self.u1, group=None, description="E1", amount=Decimal('30.00'),
            date='2026-01-01', category='OTHER', split_type='EQUAL',
            participants_data=[
                {'user': self.u1, 'amount_paid': Decimal('30.00'), 'weight': 1},
                {'user': self.u2, 'amount_paid': Decimal('0.00'), 'weight': 1},
                {'user': self.u3, 'amount_paid': Decimal('0.00'), 'weight': 1}
            ]
        )
        # Expense 2: U2 pays 30
        create_expense(
            user=self.u2, group=None, description="E2", amount=Decimal('30.00'),
            date='2026-01-02', category='OTHER', split_type='EQUAL',
            participants_data=[
                {'user': self.u1, 'amount_paid': Decimal('0.00'), 'weight': 1},
                {'user': self.u2, 'amount_paid': Decimal('30.00'), 'weight': 1},
                {'user': self.u3, 'amount_paid': Decimal('0.00'), 'weight': 1}
            ]
        )
        
        # Test individual net balances
        self.assertEqual(selectors.get_user_net_balance(self.u1), Decimal('10.00'))
        self.assertEqual(selectors.get_user_net_balance(self.u2), Decimal('10.00'))
        self.assertEqual(selectors.get_user_net_balance(self.u3), Decimal('-20.00'))

        # Test Simplification
        transactions = services.simplify_debts()
        
        # U3 owes 20 total. It should be split 10 to U1 and 10 to U2
        self.assertEqual(len(transactions), 2)
        for t in transactions:
            self.assertEqual(t['from_user'], self.u3)
            self.assertEqual(t['amount'], Decimal('10.00'))
            self.assertIn(t['to_user'], [self.u1, self.u2])