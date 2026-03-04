from django.db import models
from users.models import User

class Pickup(models.Model):

    WASTE_TYPE = (
        ('dry','Dry Waste'),
        ('wet','Wet Waste'),
        ('ewaste','E-Waste')
    )

    STATUS = (
        ('pending','Pending'),
        ('collected','Collected'),
    )

    resident = models.ForeignKey(User,on_delete=models.CASCADE)
    waste_type = models.CharField(max_length=20,choices=WASTE_TYPE)
    address = models.TextField()
    date = models.DateField()

    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default="pending"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.waste_type