from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.template.backends import django
#from guardian.admin import GuardedModelAdmin
from django.db import models

from users.models import CaseInsensitiveUser


@admin.register(CaseInsensitiveUser)
class CaseInsensitiveUserAdmin(admin.ModelAdmin):
#class CaseInsensitiveUserAdmin(UserAdmin):
    pass

