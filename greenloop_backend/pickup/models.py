from django.db import models
from users.models import User

class Pickup(models.Model):

    WASTE_TYPE = (
        ('dry','Dry Waste'),
        ('wet','Wet Waste'),
        ('ewaste','E-Waste')
    )

    resident = models.ForeignKey(User,on_delete=models.CASCADE)
    waste_type = models.CharField(max_length=20,choices=WASTE_TYPE)
    address = models.TextField()
    date = models.DateField()
    status = models.CharField(max_length=20,default="pending")

    def __str__(self):
        return self.waste_type