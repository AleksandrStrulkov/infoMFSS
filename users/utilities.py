import base64

from django.conf import settings
from django.core.signing import Signer
from django.template.loader import render_to_string

signer = Signer()


def send_activation_notification(user):
    # Используем HTTP через nginx (порт 80) или значение из настроек
    activation_host = getattr(settings, 'DEFAULT_ACTIVATION_HOST', 'localhost')
    # Если порт не указан, используем стандартный HTTP порт 80
    if ':' not in activation_host:
        host = f"http://{activation_host}"
    else:
        # Если порт указан, используем его (для локальной разработки может быть 8001)
        host = f"http://{activation_host}"
    # Используем base64 кодирование вместо URL encoding для избежания двойного кодирования
    # Django template {% url %} автоматически кодирует параметры, поэтому base64 безопаснее
    signed_email = signer.sign(user.email)
    encoded_sign = base64.urlsafe_b64encode(signed_email.encode('utf-8')).decode('utf-8').rstrip('=')
    context = {"user": user, "host": host, "sign": encoded_sign}
    subject = render_to_string("email/activation_letter_subject.txt", context)
    body_text = render_to_string("email/activation_letter_body.txt", context)
    user.email_user(subject, body_text)
