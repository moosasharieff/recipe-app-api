"""
Django admin page customization.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from . import models


class UserAdmin(BaseUserAdmin):
    """Adding customization to the admin page."""
    ordering = ['id']
    list_display = ['email', 'name']
    fieldsets = (
        # 1st section : Field columns
        (None, {'fields': ('name', 'email', 'password')}),
        # 2nd section : Field columns
        (
            _('Permissions'), {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser',
                )
            }
        ),
        # 3rd section : Field columns
        (
            _('Important Dates'), {
                'fields': (
                    'last_login',
                )
            }
        )
    )

    readonly_fields = ['last_login']

    # Add User Data in Admin Page
    add_fieldsets = (
        (None, {
            'classes': ('wide'),
            'fields': (
                'name',
                'email',
                'password1',
                'password2',
                'is_active',
                'is_staff',
                'is_superuser',)
        }),
    )


admin.site.register(models.User, UserAdmin)
