"""
Утилиты для универсального импорта данных из Excel
"""
import logging
from datetime import datetime

from django.db import transaction

logger = logging.getLogger(__name__)


def normalize_header(header):
    """Нормализация заголовка колонки"""
    if header is None:
        return None
    header_normalized = str(header).replace('\n', ' ').replace('\r', ' ').strip()
    while '  ' in header_normalized:
        header_normalized = header_normalized.replace('  ', ' ')
    return header_normalized.lower()


def find_column_mapping(headers, column_mapping):
    """
    Находит маппинг колонок по заголовкам

    Args:
        headers: Список заголовков из Excel
        column_mapping: Словарь {field_name: [список возможных названий]}

    Returns:
        dict: {field_name: column_index}
    """
    header_map = {}

    for col_idx, header in enumerate(headers):
        if header is None:
            continue
        header_normalized = normalize_header(header)

        for field_name, possible_names in column_mapping.items():
            if field_name in header_map:
                continue

            for name in possible_names:
                name_lower = name.lower()

                if header_normalized == name_lower:
                    header_map[field_name] = col_idx
                    logger.info(
                        f"Найдена колонка '{field_name}' в позиции {col_idx} (заголовок: '{header}' -> точное совпадение с '{name_lower}')")
                    break
                elif name_lower in header_normalized:
                    header_map[field_name] = col_idx
                    logger.info(
                        f"Найдена колонка '{field_name}' в позиции {col_idx} (заголовок: '{header}' -> нормализован: '{header_normalized}', совпадение: '{name_lower}')")
                    break

            if field_name in header_map:
                break

    return header_map


def parse_date(data_value):
    """Парсинг даты из различных форматов"""
    if not data_value:
        return None

    if isinstance(data_value, datetime):
        return data_value.date()
    elif hasattr(data_value, 'date'):
        return data_value.date()
    elif isinstance(data_value, str):
        for date_format in ['%d.%m.%Y', '%d/%m/%Y', '%Y-%m-%d', '%d.%m.%y', '%d/%m/%y']:
            try:
                return datetime.strptime(data_value.strip(), date_format).date()
            except ValueError:
                continue
    else:
        try:
            data_str = str(data_value).strip()
            for date_format in ['%d.%m.%Y', '%d/%m/%Y', '%Y-%m-%d', '%d.%m.%y', '%d/%m/%y']:
                try:
                    return datetime.strptime(data_str, date_format).date()
                except ValueError:
                    continue
        except Exception:
            pass

    return None


def get_foreign_key_object(model_class, search_field, value, filter_kwargs=None, row_idx=None):
    """
    Получение объекта ForeignKey по значению

    Args:
        model_class: Класс модели
        search_field: Поле для поиска
        value: Значение для поиска
        filter_kwargs: Дополнительные фильтры
        row_idx: Номер строки для логирования

    Returns:
        Объект модели или None
    """
    if not value:
        return None

    value_str = str(value).strip()
    if not value_str:
        return None

    filter_kwargs = filter_kwargs or {}
    filter_kwargs[f"{search_field}__icontains"] = value_str

    obj = model_class.objects.filter(**filter_kwargs).first()
    if not obj and row_idx:
        logger.warning(f"Строка {row_idx}: {model_class.__name__} '{value_str}' не найден")

    return obj


def truncate_field(value, max_length):
    """Обрезка значения поля до максимальной длины"""
    if not value:
        return ""

    value_str = str(value).strip()
    if len(value_str) > max_length:
        logger.warning(
            f"Значение обрезано с {len(value_str)} до {max_length} символов: '{value_str}' -> '{value_str[:max_length]}'")
        return value_str[:max_length]
    return value_str
