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
        'link': 'www.samplerecipe01.com',
    }

    defaults.update(params)

    recipe = Recipe.objects.create(user=user, **defaults)
    return recipe


def create_user(**param):
    return get_user_model().objects.create_user(**param)


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
        self.user = create_user(email='test@example.com',
                                password='testPassword')
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
        other_user = create_user(email='otherUser@example.com',
                                 password='otherUserPassword')

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

    def test_create_recipe(self):
        """Test create a recipe using the API"""
        payload = {
            'title': 'Sampel recipe',
            'time_taken': 50,
            'cost': Decimal('10.2')
        }

        response = self.client.post(RECIPE_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        recipes = Recipe.objects.get(id=response.data['id'])
        for key, value in payload.items():
            # recipe's value in db == payload's value
            self.assertEqual(getattr(recipes, key), value)

    def test_partial_update(self):
        """Test patch method for partial update."""
        # Creating a recipe
        original_link = "www.foundrecipe.com"
        recipe = create_recipe(self.user)

        # Updating recipe content
        payload = {'title': 'Patch Updated Recipe Title',
                   'link': original_link}
        url = recipe_detail_url(recipe.id)
        response = self.client.patch(url, payload)

        # Assertions
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.link, payload['link'])
        self.assertEqual(recipe.user, self.user)

    def test_update_user_returns_error(self):
        """Test Updating a new user to the recipe which is already
        connected to the user will give an error."""
        new_user = create_user(email='new_user@example.com',
                               password='NewUserpassword')
        recipe = create_recipe(user=self.user)

        payload = {'user': new_user}
        url = recipe_detail_url(recipe.id)
        self.client.patch(url, payload)

        recipe.refresh_from_db()
        self.assertEqual(recipe.user, self.user)

    def test_update_all_fields(self):
        """Test if all the fields of the recipe are successfully updating."""
        recipe = create_recipe(user=self.user)

        payload = {
            'title': 'Sample Recipe Title',
            'description': 'Sample Recipe Description',
            'time_taken': 15,
            'cost': Decimal('5.25'),
            'link': 'www.samplerecipe01.com',
        }
        url = recipe_detail_url(recipe.id)
        response = self.client.put(url, payload)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        self.assertEqual(recipe.user, self.user)
        self.assertEqual(recipe.id, recipe.id)
        self.assertEqual(recipe.title, payload['title'])

    def test_delete_recipe_(self):
        """Test Delete the recipe from the user."""
        recipe = create_recipe(user=self.user)

        url = recipe_detail_url(recipe.id)
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Recipe.objects.filter(id=recipe.id).exists())

    def test_delete_other_user_recipe(self):
        """Test deleting other users recipe should give error."""
        new_user = create_user(email='newUser@example.com',
                               password='userPassword')
        recipe = create_recipe(user=new_user)

        url = recipe_detail_url(recipe.id)
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Recipe.objects.filter(id=recipe.id).exists())
