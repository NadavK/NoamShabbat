from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField, UserChangeForm, UserCreationForm
from django.forms import forms
from django.template.backends import django
#from guardian.admin import GuardedModelAdmin
from django.db import models

from users.models import CaseInsensitiveUser


# class AdminUserChangeForm(forms.ModelForm):
#     password = ReadOnlyPasswordHashField(
#         help_text="Raw passwords are not stored, so there is no way to see "
#                   "this user's password, but you can change the password "
#                   "using <a href=\"password/\">this form</a>."
#     )
#
#     class Meta:
#         model = CaseInsensitiveUser
#         # fields = (
#         #     'email', 'first_name', 'last_name',
#         # )
#
#     def clean_password(self):
#         return self.initial["password"]

@admin.register(CaseInsensitiveUser)
class CaseInsensitiveUserAdmin(UserAdmin):
    search_fields = ['name']
