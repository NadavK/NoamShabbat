from django.contrib.auth.models import AbstractUser, UserManager


class CaseInsensitiveUserManager(UserManager):
    def get_by_natural_key(self, username):
        return self.get(username__iexact=username)

    # def get_by_natural_key(self, username):
    #     case_insensitive_username_field = '{}__iexact'.format(self.model.USERNAME_FIELD)
    #     return self.get(**{case_insensitive_username_field: username})


class CaseInsensitiveUser(AbstractUser):
    objects = CaseInsensitiveUserManager()
