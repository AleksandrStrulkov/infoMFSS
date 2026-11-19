import base64

from django.conf import settings
from django.core.signing import Signer
from django.template.loader import render_to_string

signer = Signer()


def send_activation_notification(user):
    activation_host = getattr(settings, 'DEFAULT_ACTIVATION_HOST', 'localhost')
    if activation_host.startswith(('http://', 'https://')):
        host = activation_host
    else:
        schema = 'http' if settings.DEBUG else 'https'
        host = f"{schema}://{activation_host}"

    signed_email = signer.sign(user.email)
    encoded_sign = base64.urlsafe_b64encode(signed_email.encode('utf-8')).decode('utf-8').rstrip('=')
    context = {"user": user, "host": host, "sign": encoded_sign}
    subject = render_to_string("email/activation_letter_subject.txt", context)
    body_text = render_to_string("email/activation_letter_body.txt", context)
    user.email_user(subject, body_text)
