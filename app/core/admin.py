"""
Django admin page customization.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from . import models


class UserAdmin(BaseUserAdmin):
    """Adding customization to the admin page."""
    ordering = ['id']
    list_display = ['email', 'name']

admin.site.register(models.User, UserAdmin)