from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

class UserManager(BaseUserManager):
    def create_user(self, username, email=None, password=None, **extra_fields):
        if not username:
            raise ValueError("The Username must be set")
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", User.Role.SUPERADMIN)  # 👈 auto-assign role

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(username, email, password, **extra_fields)


class User(AbstractUser):
    class Role(models.TextChoices):
        SUPERADMIN = 'SUPERADMIN', 'SuperAdmin'
        ADMIN = 'ADMIN', 'Admin'
        USER = 'USER', 'User'

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.USER)

    # field to let SuperAdmin assign a user to an Admin
    assigned_admin = models.ForeignKey(
        'self', null=True, blank=True, on_delete=models.SET_NULL,
        related_name='managed_users', limit_choices_to={'role': Role.ADMIN}
    )

    objects = UserManager()  # 👈 tell Django to use our custom manager

    def is_superadmin(self):
        return self.role == self.Role.SUPERADMIN

    def is_admin(self):
        return self.role == self.Role.ADMIN
