from django.dispatch import Signal, receiver
from .utilities import send_activation_notification
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
import logging

post_register = Signal()

logger = logging.getLogger(__name__)


@receiver(post_register)
def post_register_dispatcher(sender, **kwargs):
    send_activation_notification(kwargs["instance"])


@receiver(post_save, sender=get_user_model())
def log_user_creation(sender, instance, created, **kwargs):
    if created:  # Проверяем, что пользователь создан, а не обновлен
        logger.info(f"Создан новый пользователь: {instance.last_name} (ID: {instance.id})")
