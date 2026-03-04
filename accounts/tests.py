from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from . import services, selectors

User = get_user_model()

class AccountsTests(TestCase):
    def setUp(self):
        self.user_data = {
            'email': 'testuser@example.com',
            'password': 'testpassword123',
            'first_name': 'Test',
            'last_name': 'User',
            'default_currency': 'USD'
        }
        self.user = services.create_user(**self.user_data)

    def test_user_creation_service(self):
        """Test the create_user service logic."""
        self.assertEqual(self.user.email, self.user_data['email'])
        self.assertTrue(self.user.check_password(self.user_data['password']))
        self.assertEqual(self.user.default_currency, 'USD')

    def test_user_selector(self):
        """Test the get_user_by_email selector."""
        fetched_user = selectors.get_user_by_email(self.user_data['email'])
        self.assertIsNotNone(fetched_user)
        self.assertEqual(fetched_user.email, self.user_data['email'])
        
        missing_user = selectors.get_user_by_email('missing@example.com')
        self.assertIsNone(missing_user)

    def test_profile_update_service(self):
        """Test the update_user_profile service."""
        updated_user = services.update_user_profile(
            self.user, 
            first_name='Updated', 
            default_currency='EUR',
            email_notifications=False
        )
        self.assertEqual(updated_user.first_name, 'Updated')
        self.assertEqual(updated_user.default_currency, 'EUR')
        self.assertFalse(updated_user.email_notifications)

    def test_login_view(self):
        """Test standard authentication flow."""
        response = self.client.get(reverse('accounts:login'))
        self.assertEqual(response.status_code, 200)

        login_response = self.client.post(reverse('accounts:login'), {
            'username': self.user_data['email'],
            'password': self.user_data['password']
        })
        # Standard redirect for login is dashboard/home
        self.assertRedirects(login_response, reverse('dashboard'))

    def test_profile_view_authentication_required(self):
        """Ensure unauthenticated users are redirected."""
        response = self.client.get(reverse('accounts:profile'))
        self.assertRedirects(response, f"{reverse('accounts:login')}?next={reverse('accounts:profile')}")

    def test_profile_view_update(self):
        """Test profile update via the generic UpdateView and Form."""
        self.client.force_login(self.user)
        response = self.client.post(reverse('accounts:profile'), {
            'first_name': 'NewName',
            'last_name': 'User',
            'default_currency': 'GBP',
            'timezone': 'Europe/London',
            'email_notifications': True
        })
        self.assertRedirects(response, reverse('accounts:profile'))
        
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'NewName')
        self.assertEqual(self.user.default_currency, 'GBP')