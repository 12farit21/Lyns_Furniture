"""
Custom admin configuration for Django built-in models
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.models import User, Group
from unfold.admin import ModelAdmin
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm


# Unregister the default User and Group admin
admin.site.unregister(User)
admin.site.unregister(Group)


@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    """Custom User admin with Unfold styling"""
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm
    compressed_fields = True
    list_filter_submit = True


@admin.register(Group)
class GroupAdmin(BaseGroupAdmin, ModelAdmin):
    """Custom Group admin with Unfold styling"""
    compressed_fields = True
    list_filter_submit = True
