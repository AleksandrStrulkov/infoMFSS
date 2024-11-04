from django.db import models
from django.contrib.auth.models import AbstractUser

NULLABLE = {'null': True, 'blank': True}


class User(AbstractUser):
    username = None

    email = models.EmailField(unique=True, verbose_name='Email')
    phone = models.CharField(max_length=15, verbose_name='Номер телефона')
    telegram_id = models.CharField(max_length=50, unique=True, verbose_name='telegram_id', **NULLABLE)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

