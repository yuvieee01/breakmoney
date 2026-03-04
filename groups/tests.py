from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from . import services, selectors

User = get_user_model()

class GroupsTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(email='admin@test.com', password='pw')
        self.user2 = User.objects.create_user(email='member@test.com', password='pw')
        self.group = services.create_group("Test Trip", self.user1, "USD")

    def test_group_creation_makes_creator_admin(self):
        self.assertEqual(self.group.name, "Test Trip")
        self.assertTrue(selectors.is_group_admin(self.group, self.user1))
        
    def test_add_member(self):
        services.add_member_by_email(self.group, self.user1, self.user2.email)
        members = selectors.get_group_members(self.group)
        self.assertEqual(members.count(), 2)
        
    def test_non_admin_cannot_add_member(self):
        services.add_member_by_email(self.group, self.user1, self.user2.email)
        user3 = User.objects.create_user(email='hacker@test.com', password='pw')
        
        with self.assertRaises(PermissionError):
            services.add_member_by_email(self.group, self.user2, user3.email)

    def test_remove_member(self):
        services.add_member_by_email(self.group, self.user1, self.user2.email)
        services.remove_member(self.group, self.user1, self.user2.id)
        members = selectors.get_group_members(self.group)
        self.assertEqual(members.count(), 1)