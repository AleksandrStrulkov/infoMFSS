from django.db import models
from django.contrib.auth.models import AbstractUser
import logging

NULLABLE = {'null': True, 'blank': True}

logger = logging.getLogger(__name__)


class User(AbstractUser):
    username = None

    last_name = models.CharField(max_length=50, verbose_name='Фамилия',)
    first_name = models.CharField(max_length=50, verbose_name='Имя',)
    middle_name = models.CharField(max_length=50, verbose_name='Отчество',)
    email = models.EmailField(unique=True, verbose_name='E-mail')
    phone = models.CharField(max_length=12, verbose_name='Номер телефона', **NULLABLE)
    telegram_id = models.CharField(max_length=50, unique=True, verbose_name='telegram_id', **NULLABLE)
    is_activated = models.BooleanField(default=True, db_index=True, verbose_name='Прошел активацию?')
    location_of_work = models.CharField(max_length=50, verbose_name='Место работы',)
    post = models.CharField(max_length=50, verbose_name='Должность',)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def save(self, *args, **kwargs):
        is_new = self._state.adding  # Проверяем, что объект новый
        super().save(*args, **kwargs)
        if is_new:
            logger.info(f'Создан новый пользователь: {self.last_name} (ID: {self.id})', extra={'classname': self.__class__.__name__})


class AllowedPerson(models.Model):
    last_name = models.CharField(max_length=50, verbose_name='Фамилия',)  # Фамилия
    first_name = models.CharField(max_length=50, verbose_name='Имя',)  # Имя
    middle_name = models.CharField(max_length=50, verbose_name='Отчество',)  # Отчество (необязательно)
    is_active = models.BooleanField(default=True)  # Можно отключать пользователей

    def __str__(self):
        return f"{self.last_name} {self.first_name} {self.middle_name}"

    class Meta:
        verbose_name = 'Разрешенный пользователь'
        verbose_name_plural = 'Разрешенные пользователи'
        ordering = ['last_name']
