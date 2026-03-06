from django.db import models
from users.models import User

class Complaint(models.Model):

    STATUS = (
        ('pending','Pending'),
        ('resolved','Resolved'),
    )

    resident = models.ForeignKey(User, on_delete=models.CASCADE)

    title = models.CharField(max_length=200)
    description = models.TextField()

    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default='pending'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title