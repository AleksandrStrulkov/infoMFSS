from __future__ import annotations

import logging
from datetime import datetime

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

NULLABLE = {"null": True, "blank": True}

logger = logging.getLogger(__name__)


class User(AbstractUser):
    username = None

    last_name = models.CharField(
        max_length=50,
        verbose_name="Фамилия",
    )
    first_name = models.CharField(
        max_length=50,
        verbose_name="Имя",
    )
    middle_name = models.CharField(
        max_length=50,
        verbose_name="Отчество",
    )
    email = models.EmailField(unique=True, verbose_name="E-mail", **NULLABLE)
    phone = models.CharField(max_length=12, verbose_name="Номер телефона", **NULLABLE)
    telegram_id = models.CharField(max_length=50, unique=True, verbose_name="telegram_id", **NULLABLE)
    is_activated = models.BooleanField(default=True, db_index=True, verbose_name="Прошел активацию?")
    location_of_work = models.CharField(
        max_length=50,
        verbose_name="Место работы",
    )
    post = models.CharField(
        max_length=50,
        verbose_name="Должность",
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def save(self, *args, **kwargs):
        is_new = self._state.adding  # Проверяем, что объект новый
        super().save(*args, **kwargs)
        if is_new:
            logger.info(
                f"Создан новый пользователь: {self.last_name} (ID: {self.id})",
                extra={"classname": self.__class__.__name__},
            )


class Invitation(models.Model):
    token = models.CharField(max_length=64, unique=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="created_invitations"
    )
    created_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True, blank=True)
    registered_user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="registration_invitation",
    )

    class Meta:
        indexes = [models.Index(fields=["created_by", "used_at", "expires_at"], name="invite_author_status_idx")]
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(used_at__isnull=True, registered_user__isnull=True)
                    | models.Q(used_at__isnull=False, registered_user__isnull=False)
                ),
                name="invite_usage_pair",
            )
        ]

    def is_valid(self, at: datetime | None = None) -> bool:
        """Check whether the invitation may still be redeemed."""
        return self.used_at is None and self.registered_user_id is None and self.expires_at > (at or timezone.now())


class AllowedPerson(models.Model):
    last_name = models.CharField(
        max_length=50,
        verbose_name="Фамилия",
    )  # Фамилия
    first_name = models.CharField(
        max_length=50,
        verbose_name="Имя",
    )  # Имя
    middle_name = models.CharField(
        max_length=50,
        verbose_name="Отчество",
    )  # Отчество (необязательно)
    is_active = models.BooleanField(default=True)  # Можно отключать пользователей

    class Meta:
        verbose_name = "Разрешенный пользователь"
        verbose_name_plural = "Разрешенные пользователи"
        ordering = ["last_name"]

    def __str__(self):
        return f"{self.last_name} {self.first_name} {self.middle_name}"

    def save(self, *args, **kwargs):
        is_new = self._state.adding  # Проверяем, что объект новый
        super().save(*args, **kwargs)
        if is_new:
            logger.info(
                f"Добавлен разрешенный пользователь: {self.last_name} (ID: {self.id})",
                extra={"classname": self.__class__.__name__},
            )


class SMSDevice(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)

    def is_valid(self):
        return (timezone.now() - self.created_at).seconds < 300  # 5 минут
