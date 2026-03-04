from django.db import models
from users.models import User

class Reward(models.Model):

    user = models.ForeignKey(User,on_delete=models.CASCADE)
    points = models.IntegerField(default=0)
    description = models.TextField()