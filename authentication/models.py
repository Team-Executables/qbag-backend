from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin)

from rest_framework_simplejwt.tokens import RefreshToken




class UserManager(BaseUserManager):
    def create_user(self, name, email, employment, user_type, password=None, active=True, staff=False, admin=False, verified=False):
        if not email:
            raise ValueError("Users must have an email address")

        if not password:
            raise ValueError("Users must have password")

        user_obj = self.model(
            name = name,
            email=self.normalize_email(email),
            employment=employment,
            user_type = user_type
        )
        user_obj.set_password(password)
        user_obj.is_staff = staff
        user_obj.is_admin = admin
        user_obj.is_active = active
        user_obj.is_verified = verified
        user_obj.save(using=self._db)
        return user_obj

    def create_staffuser(self, name, email, employment, password=None):
        user = self.create_user(
            name,
            email,
            employment,
            password=password,
            staff=True
        )

        return user
    
    def create_superuser(self, name, email, employment, password=None):
        user = self.create_user(
            name,
            email,
            employment,
            user_type = 'other',
            password=password,
            staff=True,
            admin = True
        )
        user.is_superuser = True
        return user




USER_TYPE_CHOICES = (
    ('other', 'other'),
    ('teacher', 'teacher')
)

# def upload(instance, filename):
#     return 'avatars/{filename}'.format(filename=filename)

class User(AbstractBaseUser):
    name = models.CharField(max_length=50, blank=True)
    email = models.EmailField(max_length=255, unique=True)
    employment=models.CharField(max_length=100, blank=True)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    user_type = models.CharField(max_length=25, choices=USER_TYPE_CHOICES, default='other')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name','employment']

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_lable):
        return True

    objects = UserManager()

    def __str__(self):
        return f"{self.email}-{self.user_type}"

    def tokens(self):
        refresh = RefreshToken.for_user(self)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        }