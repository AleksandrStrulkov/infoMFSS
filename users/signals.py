import logging

from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

logger = logging.getLogger(__name__)


@receiver(post_save, sender=get_user_model())
def log_user_creation(sender, instance, created, **kwargs):
    if created:  # Проверяем, что пользователь создан, а не обновлен
        logger.info(f"Создан новый пользователь: {instance.last_name} (ID: {instance.id})")
