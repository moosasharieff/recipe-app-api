"""
Tests for the Django admin administration
"""
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse


class AdminSiteTests(TestCase):
    """Tests for Django Admin."""

    def setUp(self):
        """setUp for Django Tests, creating user and client."""

        # Creating a superuser and authenticating through it.
        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(
            email='admin@example.com',
            password='testpass@123'
        )
        self.client.force_login(self.admin_user)

        # Creating a normal user.
        self.user = get_user_model().objects.create_user(
            email='user@example.com',
            password='testpass@123',
            name="Test User"
        )

    def test_users_list(self):
        """Test that users are listed on the admin page"""
        url = reverse('admin:core_user_changelist')
        response = self.client.get(url)

        # Assertions
        self.assertContains(response, self.user.name)
        self.assertContains(response, self.user.email)

    def test_edit_user_page(self):
        """Test the edit user page works."""
        url = reverse('admin:core_user_change', args=[self.user.id])
        response = self.client.get(url)

        # Assertions
        self.assertEqual(response.status_code, 200)

    def test_add_user_page(self):
        """Test the add user page works."""
        url = reverse('admin:core_user_add')
        response = self.client.get(url)

        # Assertions
        self.assertEqual(response.status_code, 200)
