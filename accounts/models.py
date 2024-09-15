from django.db import models

# Create your models here.
from django.contrib.auth.models import User, AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    avatar = models.ImageField(upload_to='temp/', null=True, blank=True)