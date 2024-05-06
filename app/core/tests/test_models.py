"""
Tests for models.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model

from decimal import Decimal

from core import models


class ModelTests(TestCase):
    """Test models functionality."""

    def test_create_user_with_email_successful(self):
        """Test creating a user with an email is successful."""
        email = 'test@example.com'
        password = 'testingPassword@123'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        # Assertions
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_is_normalized(self):
        """Test email is normalized for the new users."""
        sample_emails = [
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['Test2@Example.com', 'Test2@example.com'],
            ['TEST3@EXAMPLE.COM', 'TEST3@example.com'],
            ['test4@example.com', 'test4@example.com']
        ]

        for email, expected_email in sample_emails:
            user = get_user_model().objects.create_user(email, 'sample123')
            self.assertEqual(user.email, expected_email)

    def test_new_user_without_email_raises_error(self):
        """Test that creating a user without an email raises a ValueError."""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', 'test123')

    def test_new_user_with_superuser_privileges(self):
        email = 'test1@example.com'
        password = 'test1@123'
        user = get_user_model().objects.create_superuser(email, password)

        # Assertions
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
    
    def test_create_receipe(self):
        """Test creating a receipe is successful."""
        user = get_user_model().objects.create_user(
            'test@example.com',
            'testPassword'
        )

        recipe = models.Recipe.objects.create(
            user=user,
            title='Sample recipe name',
            time_taken=5,
            preparation_cost=Decimal(5.50),
            description='Sample recipe description.'
        )

        self.assertEqual(str(recipe), recipe.title)