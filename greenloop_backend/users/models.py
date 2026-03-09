from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):

    ROLE_CHOICES = (
        ('admin','Admin'),
        ('resident','Resident'),
        ('hks_worker','HKS Worker'),
        ('recycler', 'Recycler'),
    )

    email = models.EmailField(unique=True)   

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='resident')
    phone = models.CharField(max_length=15)
    ward = models.CharField(max_length=50)

    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    def __str__(self):
        return self.username