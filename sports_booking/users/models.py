from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models


class User(AbstractUser):
    TRAINER = 'trainer'
    USER = 'user'
    ROLE_CHOICES = [
        (TRAINER, 'Trainer'),
        (USER, 'User'),
    ]

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=USER)
    bio = models.TextField(null=True, blank=True)

    groups = models.ManyToManyField(
        Group,
        related_name='custom_user_groups',
        blank=True,
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='custom_user_permissions',
        blank=True,
    )

    def is_trainer(self):
        return self.role == self.TRAINER
