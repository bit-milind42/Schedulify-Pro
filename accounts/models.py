from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = (
        ('customer', 'Customer'),
        ('provider', 'Service Provider'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')
    specialty = models.CharField(max_length=100, blank=True)

    def is_provider(self):
        return self.role == 'provider'

    def __str__(self):
        base = super().__str__()
        if self.is_provider() and self.specialty:
            return f"{base} ({self.specialty})"
        return base
