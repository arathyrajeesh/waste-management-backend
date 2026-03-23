from django.contrib.auth.models import AbstractUser
from django.contrib.gis.db import models

class User(AbstractUser):

    ROLE_CHOICES = (
        ('admin','Admin'),
        ('resident','Resident'),
        ('hks_worker','HKS Worker'),
        ('recycler', 'Recycler'),
    )

    email = models.EmailField(unique=True)   
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='resident')
    phone = models.CharField(max_length=15)
    ward = models.CharField(max_length=50)
    
    # Location fields for HKS workers (GeoDjango Spatial)
    location = models.PointField(null=True, blank=True)
    last_location_update = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.username