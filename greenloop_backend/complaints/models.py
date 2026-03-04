from django.db import models
from users.models import User

class Complaint(models.Model):

    user = models.ForeignKey(User,on_delete=models.CASCADE)
    message = models.TextField()
    status = models.CharField(max_length=20,default="open")
    created_at = models.DateTimeField(auto_now_add=True)