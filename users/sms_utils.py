import requests
from urllib.parse import urlencode
from django.conf import settings


def send_sms_via_smsc(phone, code):
    params = {
            'login': settings.SMSC_LOGIN,
            'psw': settings.SMSC_PASSWORD,
            'phones': phone,
            'mes': f'Ваш код: {code}',
            'sender': settings.SMSC_SENDER,
            'fmt': 3,  # Ответ в JSON
            'charset': 'utf-8'
    }

    url = f"https://smsc.ru/sys/send.php?{urlencode(params)}"
    response = requests.get(url)
    return response.json()