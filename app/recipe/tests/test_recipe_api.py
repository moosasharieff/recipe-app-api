"""
Tests for recipe app.
"""
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from core.models import Recipe

from rest_framework import status
from rest_framework.test import APIClient

from recipe.serializers import RecipeSerializer, RecipeDetailSerializer

RECIPE_URL = reverse('recipe:recipe-list')

def recipe_detail_url(recipe_id):
    """Create and return recipe detail URL."""
    return reverse('recipe:recipe-detail', args=[recipe_id])


def create_recipe(user, **params):
    """Create new recipe for the user."""

    defaults = {
        'title': 'Sample Recipe Title',
        'description': 'Sample Recipe Description',
        'time_taken': 15,
        'cost': Decimal('5.25'),
        'link': 'www.samplerecipe/01.com',
    }

    defaults.update(params)

    recipe = Recipe.objects.create(user=user, **defaults)
    return recipe


class PublicRecipeApiTests(TestCase):
    """Test Unauthorized Recipe APIs."""

    def setUp(self):
        """Setting up Pre-requisites for test cases."""
        self.client = APIClient()

    def test_auth_required(self):
        """Test to check if Authorization is required to fetch
        all the recipes of a user."""
        response = self.client.get(RECIPE_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTests(TestCase):
    """Test Authorized Recipe APIs."""

    def setUp(self):
        """Setting up pre-requisites for test cases."""

        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@example.com',
            'testPassword'
        )
        # Authenticating the user
        self.client.force_authenticate(self.user)

    def test_retrieve_recipe(self):
        """Test retrieve recipes post user authentication."""
        create_recipe(self.user)
        create_recipe(self.user)

        response = self.client.get(RECIPE_URL)

        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_recipe_list_limited_to_user(self):
        """Test list recipe but limited to the authenticated user only."""
        other_user = get_user_model().objects.create_user(
            'otherUser@example.com',
            'otherUserPassword',
        )

        create_recipe(self.user)  # Authenticated user
        create_recipe(other_user)  # Un-authenticated user

        response = self.client.get(RECIPE_URL)

        recipe = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipe, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_recipe_detail(self):
        """Test get details of one specific recipe for authenticated user."""
        recipe = create_recipe(self.user)

        url = recipe_detail_url(recipe.id)
        response = self.client.get(url)
        serializer = RecipeDetailSerializer(recipe)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)
