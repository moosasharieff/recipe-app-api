"""
Tests for the user API.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('user:create')
CREATE_TOKEN_URL = reverse('user:token')
MY_URL = reverse('user:my_url')


def create_user(**params):
    """Func() to create new users with dynamic params."""
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """Test the public features of the user API."""

    def setUp(self):
        """Setting up pre-requisites for test cases."""
        self.client = APIClient()

    def test_create_user_success(self):
        """Test create user functionality is successful."""
        payload = {
            'email': 'test@example.com',
            'password': 'test@123',
            'name': 'Tester',
        }

        response = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user = get_user_model().objects.get(email=payload['email'])
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', response.data)

    def test_user_with_email_exists_error(self):
        """Test error is returned if user email already exists"""
        payload = {
            'email': 'test@example.com',
            'password': 'test@123',
            'name': 'Tester',
        }

        create_user(**payload)
        response = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_short_password(self):
        """Test error is return if password length is short."""
        payload = {
            'email': 'test@example.com',
            'password': 'test',
            'name': 'Tester',
        }

        response = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        user_exists = get_user_model().objects.filter(
            email=payload['email']).exists()
        self.assertFalse(user_exists)

    def test_user_token_creation_successful(self):
        """Test Token is generated successfully."""
        create_user(email='test@example.com', password='correctPass')

        payload = {
            'email': 'test@example.com',
            'password': 'correctPass'
        }

        response = self.client.post(CREATE_TOKEN_URL, payload)

        self.assertIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_authentication_with_invalid_credentials(self):
        """Test Token is generated with incorrect credentials."""
        create_user(email='test@example.com', password='correctPass')

        payload = {
            'email': 'test@example.com',
            'password': 'incorrectPass'
        }

        response = self.client.post(CREATE_TOKEN_URL, payload)

        self.assertNotIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_authentication_with_blank_password(self):
        create_user(email='test@example.com', password='correctPass')

        payload = {
            'email': 'test@example.com',
            'password': ''
        }

        response = self.client.post(CREATE_TOKEN_URL, payload)

        self.assertNotIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauthorized(self):
        """Test user is not authorized to access the endpoint."""

        payload = {
            'email': 'test@example.com',
            'password': 'testPassword'
        }

        response = self.client.get(MY_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):
    """Test endpoint which require authentication."""

    def setUp(self):
        """Setting up pre-requisites for test cases."""

        self.user = create_user(
            email='test@example.com',
            password='testPassword',
            name="Test User",
        )

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_succes(self):
        """Test user has successfully authenticated."""

        response = self.client.get(MY_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {
            'email': 'test@example.com',
            'name': 'Test User'
        })

    def test_post_method_not_allowed(self):
        """Test POST Method is not allowed for MY_URL Endpoint."""

        response = self.client.post(MY_URL, {})

        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_user_update_profile(self):
        """Test Updating user profile is successfully after authenticating."""
        payload = {
            'name': 'Updated Name',
            'password': 'UpdatedPassword'
        }

        response = self.client.patch(MY_URL, payload)

        self.user.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(self.user.name, payload['name'])
