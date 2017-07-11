from django.db import models
from django.contrib import auth
from django.contrib.auth.models import User
# Create your models here.

class Member(auth.models.User, auth.models.PermissionsMixin):

    user= models.OneToOneField(User)

    points = models.PositiveIntegerField(default=0)

    def __str__(self):
        return "@{}".format(self.username)
