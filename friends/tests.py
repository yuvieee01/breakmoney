from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Friendship, FriendInvitation
from . import services, selectors

User = get_user_model()

class FriendsTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(email='user1@test.com', password='pw')
        self.user2 = User.objects.create_user(email='user2@test.com', password='pw')

    def test_add_existing_user_as_friend(self):
        obj, action = services.add_friend_by_email(self.user1, self.user2.email)
        self.assertEqual(action, "FRIEND_ADDED")
        self.assertTrue(selectors.are_friends(self.user1, self.user2))

    def test_add_non_existing_user_creates_invite(self):
        obj, action = services.add_friend_by_email(self.user1, 'unknown@test.com')
        self.assertEqual(action, "INVITE_SENT")
        self.assertEqual(FriendInvitation.objects.count(), 1)

    def test_cannot_add_self(self):
        with self.assertRaises(ValueError):
            services.add_friend_by_email(self.user1, self.user1.email)

    def test_cannot_add_twice(self):
        services.add_friend_by_email(self.user1, self.user2.email)
        with self.assertRaises(ValueError):
            services.add_friend_by_email(self.user1, self.user2.email)

    def test_remove_friend(self):
        services.add_friend_by_email(self.user1, self.user2.email)
        services.remove_friend(self.user1, self.user2)
        self.assertFalse(selectors.are_friends(self.user1, self.user2))