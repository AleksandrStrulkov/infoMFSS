from django.db import models
from django.contrib.auth.models import AbstractUser

NULLABLE = {'null': True, 'blank': True}


class User(AbstractUser):
    username = None

    email = models.EmailField(unique=True, verbose_name='Электронная почта')
    phone = models.CharField(max_length=12, verbose_name='Номер телефона', **NULLABLE)
    telegram_id = models.CharField(max_length=50, unique=True, verbose_name='telegram_id', **NULLABLE)
    is_activated = models.BooleanField(default=True, db_index=True, verbose_name='Прошел активацию?')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

