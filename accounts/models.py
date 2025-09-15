from django.db import models
from django.contrib.auth.models import AbstractUser

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

    def is_superadmin(self):
        return self.role == self.Role.SUPERADMIN

    def is_admin(self):
        return self.role == self.Role.ADMIN
