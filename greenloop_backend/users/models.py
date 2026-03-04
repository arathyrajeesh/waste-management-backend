from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):

    ROLE_CHOICES = (
        ('admin','Admin'),
        ('resident','Resident'),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='resident')
    phone = models.CharField(max_length=15)
    ward = models.CharField(max_length=50)

    def __str__(self):
        return self.username