import logging
import re
from urllib.parse import urlencode

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


def normalize_phone(phone):
    """
    Нормализация номера телефона для API smsc.ru
    
    Принимает номер в любом формате и приводит к формату 79991234567
    (без +, без пробелов, без дефисов, начинается с 7 или 8)
    """
    if not phone:
        return phone
    
    # Убираем все нецифровые символы кроме + в начале
    phone = re.sub(r'[^\d+]', '', str(phone))
    
    # Если номер начинается с +7, заменяем на 7
    if phone.startswith('+7'):
        phone = '7' + phone[2:]
    # Если номер начинается с 8, заменяем на 7
    elif phone.startswith('8'):
        phone = '7' + phone[1:]
    # Если номер начинается с 7, оставляем как есть
    elif not phone.startswith('7'):
        # Если номер не начинается с 7 или 8, добавляем 7
        phone = '7' + phone
    
    # Убираем все нецифровые символы (на случай, если что-то осталось)
    phone = re.sub(r'\D', '', phone)
    
    # Проверяем, что номер имеет правильную длину (11 цифр: 7 + 10)
    if len(phone) != 11:
        logger.warning(f"Номер телефона имеет нестандартную длину: {phone} (длина: {len(phone)})")
    
    return phone


def send_sms_via_smsc(phone, code):
    """
    Отправка SMS через API smsc.ru
    
    Возвращает словарь с результатом:
    - {"error": "текст ошибки"} - при ошибке
    - {"id": "id сообщения", ...} - при успехе
    """
    # Проверка наличия настроек
    if not all([settings.SMSC_LOGIN, settings.SMSC_PASSWORD, settings.SMSC_SENDER]):
        error_msg = "Не настроены параметры SMSC (SMSC_LOGIN, SMSC_PASSWORD, SMSC_SENDER)"
        logger.error(error_msg)
        return {"error": error_msg}
    
    # Нормализация номера телефона
    original_phone = phone
    phone = normalize_phone(phone)
    logger.info(f"Нормализация номера: {original_phone} -> {phone}")
    
    # Формируем сообщение
    message = f"Ваш код: {code}"
    
    params = {
        "login": settings.SMSC_LOGIN,
        "psw": settings.SMSC_PASSWORD,
        "phones": phone,  # Используем нормализованный номер
        "mes": message,
        "sender": settings.SMSC_SENDER,
        "fmt": 3,  # Ответ в JSON
        "charset": "utf-8",
        "translit": 0,  # 0 - кириллица, 1 - транслит (если оператор не поддерживает кириллицу)
    }
    
    logger.info(f"Параметры отправки: номер={phone}, сообщение='{message}', отправитель={settings.SMSC_SENDER}")

    try:
        url = f"https://smsc.ru/sys/send.php?{urlencode(params)}"
        logger.info(f"Отправка SMS на номер {phone} (оригинал: {original_phone}) через smsc.ru")
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Вызовет исключение при HTTP ошибке
        
        result = response.json()
        logger.info(f"Ответ от smsc.ru: {result}")
        
        # API smsc.ru возвращает ошибки в разных форматах
        # Проверяем различные варианты ошибок
        if isinstance(result, dict):
            # Если есть поле "error" или "error_code"
            if "error" in result:
                error_msg = result.get("error", "Неизвестная ошибка")
                logger.error(f"Ошибка отправки SMS: {error_msg}")
                return {"error": error_msg}
            
            # Если есть "error_code" (некоторые версии API)
            if "error_code" in result and result.get("error_code") != "0":
                error_msg = result.get("error", f"Ошибка {result.get('error_code')}")
                logger.error(f"Ошибка отправки SMS (код {result.get('error_code')}): {error_msg}")
                return {"error": error_msg}
            
            # Если есть "id", значит сообщение отправлено успешно
            if "id" in result:
                logger.info(f"SMS успешно отправлено. ID: {result.get('id')}")
                return result
        
        # Если формат ответа неожиданный
        logger.warning(f"Неожиданный формат ответа от smsc.ru: {result}")
        return result
        
    except requests.exceptions.RequestException as e:
        error_msg = f"Ошибка сети при отправке SMS: {str(e)}"
        logger.error(error_msg)
        return {"error": error_msg}
    except ValueError as e:
        error_msg = f"Ошибка парсинга JSON ответа от smsc.ru: {str(e)}"
        logger.error(error_msg)
        return {"error": error_msg}
    except Exception as e:
        error_msg = f"Неожиданная ошибка при отправке SMS: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return {"error": error_msg}
