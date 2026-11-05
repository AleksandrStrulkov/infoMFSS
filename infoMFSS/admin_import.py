"""
Утилиты для импорта данных из Excel в админке Django
"""
import logging
from datetime import datetime

from django.db import transaction
from openpyxl import load_workbook

from infoMFSS.models import (
    Beacon, BranchesBox, Cable, CableMagazine, Equipment, EquipmentInstallation,
    Execution, InclinedBlocks, NumberMine, PointPhone, Subsystem, Tunnel, Unit, Violations
)
from infoMFSS.admin_import_utils import find_column_mapping, normalize_header, parse_date, get_foreign_key_object, truncate_field

logger = logging.getLogger(__name__)


def import_beacons_from_excel(excel_file):
    """
    Импорт биконов из Excel файла

    Ожидаемые колонки в Excel (первая строка - заголовки):
    - Обозн. в проекте (designation)
    - Подсистема (subsystem) - опционально, по умолчанию "Позиционирование"
    - Шахта (number_mine) - название шахты, например "Нефтешахта №1"
    - Выработка (tunnel) - название выработки - опционально
    - Уклонный блок (inclined_blocks) - название уклонного блока - опционально
    - Пикет (picket) - опционально
    - MAC-адрес (mac_address)
    - Зав. № (serial_number)
    - МИНОР (minor)
    - Установлен (execution_bool) - "Да"/"Нет" или True/False - опционально, по умолчанию False
    - Дата монтажа (data) - в формате ДД.ММ.ГГГГ или ДД/ММ/ГГГГ

    Args:
        excel_file: Загруженный Excel файл

    Returns:
        tuple: (success_count, error_count, errors_list)
    """
    success_count = 0
    error_count = 0
    errors_list = []

    try:
        # Загружаем Excel файл
        logger.info(f"Начало импорта файла: {excel_file.name}")
        workbook = load_workbook(excel_file, data_only=True)
        sheet = workbook.active
        logger.info(f"Активный лист: {sheet.title}, размер: {sheet.max_row} строк, {sheet.max_column} колонок")

        # Определяем индексы колонок по первой строке (заголовкам)
        headers_row = list(sheet.iter_rows(min_row=1, max_row=1, values_only=True))[0]
        # Преобразуем заголовки в строки и очищаем от None
        headers = [str(h).strip() if h is not None else None for h in headers_row]
        logger.info(f"Заголовки найдены (сырые): {headers_row}")
        logger.info(f"Заголовки найдены (обработанные): {headers}")
        header_map = {}

        # Пропускаем первую строку (заголовки)
        rows = list(sheet.iter_rows(min_row=2, values_only=True))
        logger.info(f"Найдено строк данных: {len(rows)}")

        if not rows:
            return 0, 0, ["Файл пуст или не содержит данных (нет строк после заголовков)"]

        # Маппинг возможных названий колонок
        column_mapping = {
            'designation': ['обозн. в проекте', 'обозначение', 'designation', 'обозначение в проекте', 'обозн в проекте'],
            'subsystem': ['подсистема', 'subsystem'],
            'number_mine': ['шахта', 'number_mine', 'нефтешахта', 'numbermine', 'number_mine', 'mine'],
            'tunnel': ['выработка', 'tunnel', 'наименование горной выработки', 'горная выработка', 'выработка'],
            'inclined_blocks': ['уклонный блок', 'inclined_blocks', 'уклонный', 'уклонный блок', 'inclinedblocks', 'nclined_blocks'],
            'picket': ['пикет', 'picket'],
            'mac_address': ['mac-адрес', 'mac адрес', 'mac_address', 'mac', 'мас-адрес', 'мас адрес', 'мас-адресс', 'мас адресс', 'macaddress'],
            'serial_number': ['зав. №', 'зав №', 'serial_number', 'серийный номер', 'зав.№', 'зав№', 'зав. номер', 'зав номер', 'serialnumber'],
            'minor': ['минор', 'minor'],
            'execution_bool': ['установлен', 'execution_bool', 'установка', 'executionbool', 'execution'],
            'data': ['дата монтажа', 'data', 'дата', 'дата установки', 'date'],
        }

        # Находим индексы колонок
        for col_idx, header in enumerate(headers):
            if header is None:
                continue
            # Нормализуем заголовок: убираем переносы строк, лишние пробелы, приводим к нижнему регистру
            header_normalized = str(header).replace('\n', ' ').replace('\r', ' ').strip()
            # Убираем множественные пробелы
            while '  ' in header_normalized:
                header_normalized = header_normalized.replace('  ', ' ')
            header_normalized = header_normalized.lower()

            for field_name, possible_names in column_mapping.items():
                # Пропускаем, если уже найдено
                if field_name in header_map:
                    continue

                # Проверяем вхождение каждого варианта названия в нормализованный заголовок
                for name in possible_names:
                    name_lower = name.lower()

                    # Сначала проверяем точное совпадение
                    if header_normalized == name_lower:
                        header_map[field_name] = col_idx
                        logger.info(
                            f"Найдена колонка '{field_name}' в позиции {col_idx} (заголовок: '{header}' -> точное совпадение с '{name_lower}')")
                        break
                    # Затем проверяем вхождение подстроки (более гибкая проверка)
                    elif name_lower in header_normalized:
                        header_map[field_name] = col_idx
                        logger.info(
                            f"Найдена колонка '{field_name}' в позиции {col_idx} (заголовок: '{header}' -> нормализован: '{header_normalized}', совпадение: '{name_lower}')")
                        break

                if field_name in header_map:
                    break

        logger.info(f"Найдено колонок: {len(header_map)}, маппинг: {header_map}")
        logger.info(f"Все заголовки: {headers}")
        logger.info(f"Нормализованные заголовки: {[str(h).lower().strip() if h else None for h in headers]}")

        # Проверяем обязательные поля
        required_fields = ['designation', 'number_mine', 'mac_address', 'serial_number', 'minor', 'data']
        missing_fields = [field for field in required_fields if field not in header_map]
        if missing_fields:
            found_headers = [str(headers[header_map[f]]) if f in header_map else None for f in required_fields]
            error_msg = f"Отсутствуют обязательные колонки: {', '.join(missing_fields)}. Найденные заголовки: {[h for h in headers if h]}"
            logger.error(error_msg)
            return 0, 0, [error_msg]

        # Импортируем данные
        rows_processed = 0
        rows_skipped_empty = 0
        # Используем savepoints для обработки ошибок по строкам
        for row_idx, row in enumerate(rows, start=2):
            # Создаем savepoint для каждой строки
            savepoint_id = None
            try:
                # Пропускаем пустые строки
                if not any(row):
                    rows_skipped_empty += 1
                    continue

                rows_processed += 1

                # Создаем savepoint перед обработкой строки
                savepoint_id = transaction.savepoint()

                # Извлекаем данные из строки - Обозн. в проекте (обязательное поле)
                designation_value = row[header_map['designation']]

                # Проверяем, что ячейка не пустая (None, пустая строка, только пробелы)
                if designation_value is None:
                    if savepoint_id is not None:
                        transaction.savepoint_rollback(savepoint_id)
                    continue

                # Преобразуем в строку и убираем пробелы
                designation = str(designation_value).strip()

                # Если после удаления пробелов строка пустая, пропускаем строку
                if not designation:
                    if savepoint_id is not None:
                        transaction.savepoint_rollback(savepoint_id)
                    continue

                # Шахта
                number_mine_str = str(row[header_map['number_mine']]).strip(
                ) if row[header_map['number_mine']] else None
                number_mine = None
                if number_mine_str:
                    # Ищем шахту по названию
                    number_mine = NumberMine.objects.filter(title__icontains=number_mine_str).first()
                    if not number_mine:
                        error_count += 1
                        errors_list.append(f"Строка {row_idx}: Шахта '{number_mine_str}' не найдена")
                        if savepoint_id is not None:
                            transaction.savepoint_rollback(savepoint_id)
                        continue

                # Выработка (опционально)
                tunnel = None
                if 'tunnel' in header_map and row[header_map['tunnel']]:
                    tunnel_str = str(row[header_map['tunnel']]).strip()
                    if tunnel_str:
                        tunnel = Tunnel.objects.filter(
                            title__icontains=tunnel_str,
                            number_mine=number_mine
                        ).first()
                        if not tunnel:
                            logger.warning(f"Строка {row_idx}: Выработка '{tunnel_str}' не найдена, будет пропущена")

                # Уклонный блок (опционально)
                inclined_blocks = None
                if 'inclined_blocks' in header_map and row[header_map['inclined_blocks']]:
                    inclined_blocks_str = str(row[header_map['inclined_blocks']]).strip()
                    if inclined_blocks_str:
                        inclined_blocks = InclinedBlocks.objects.filter(
                            title__icontains=inclined_blocks_str,
                            number_mine=number_mine
                        ).first()
                        if not inclined_blocks:
                            logger.warning(
                                f"Строка {row_idx}: Уклонный блок '{inclined_blocks_str}' не найден, будет пропущен")

                # Подсистема
                subsystem = "Позиционирование"
                if 'subsystem' in header_map and row[header_map['subsystem']]:
                    subsystem = str(row[header_map['subsystem']]).strip()

                # Пикет (опционально)
                picket = None
                if 'picket' in header_map and row[header_map['picket']]:
                    picket = str(row[header_map['picket']]).strip()

                # MAC-адрес (ограничиваем до 17 символов)
                mac_address_raw = str(row[header_map['mac_address']]).strip() if row[header_map['mac_address']] else ""
                mac_address = mac_address_raw[:17] if mac_address_raw else ""
                if len(mac_address_raw) > 17:
                    logger.warning(
                        f"Строка {row_idx}: MAC-адрес обрезан с {len(mac_address_raw)} до 17 символов: '{mac_address_raw}' -> '{mac_address}'")

                # Серийный номер (ограничиваем до 10 символов)
                serial_number_raw = str(row[header_map['serial_number']]).strip(
                ) if row[header_map['serial_number']] else ""
                serial_number = serial_number_raw[:10] if serial_number_raw else ""
                if len(serial_number_raw) > 10:
                    logger.warning(
                        f"Строка {row_idx}: Серийный номер обрезан с {len(serial_number_raw)} до 10 символов: '{serial_number_raw}' -> '{serial_number}'")

                # МИНОР (ограничиваем до 10 символов)
                minor_raw = str(row[header_map['minor']]).strip() if row[header_map['minor']] else ""
                minor = minor_raw[:10] if minor_raw else ""
                if len(minor_raw) > 10:
                    logger.warning(
                        f"Строка {row_idx}: МИНОР обрезан с {len(minor_raw)} до 10 символов: '{minor_raw}' -> '{minor}'")

                # Установлен (опционально)
                execution_bool = False
                if 'execution_bool' in header_map and row[header_map['execution_bool']]:
                    execution_value = str(row[header_map['execution_bool']]).strip().lower()
                    execution_bool = execution_value in ['да', 'yes', 'true', '1', 'установлен']

                # Дата монтажа
                data_value = row[header_map['data']]
                data = None
                if data_value:
                    if isinstance(data_value, datetime):
                        data = data_value.date()
                    elif hasattr(data_value, 'date'):  # datetime объект из openpyxl
                        data = data_value.date()
                    elif isinstance(data_value, str):
                        # Пробуем разные форматы даты
                        for date_format in ['%d.%m.%Y', '%d/%m/%Y', '%Y-%m-%d', '%d.%m.%y', '%d/%m/%y']:
                            try:
                                data = datetime.strptime(data_value.strip(), date_format).date()
                                break
                            except ValueError:
                                continue
                    else:
                        # Пробуем преобразовать в строку и распарсить
                        try:
                            data_str = str(data_value).strip()
                            for date_format in ['%d.%m.%Y', '%d/%m/%Y', '%Y-%m-%d', '%d.%m.%y', '%d/%m/%y']:
                                try:
                                    data = datetime.strptime(data_str, date_format).date()
                                    break
                                except ValueError:
                                    continue
                        except Exception:
                            pass

                if not data:
                    error_count += 1
                    errors_list.append(f"Строка {row_idx}: Дата монтажа не указана или неверный формат: {data_value}")
                    if savepoint_id is not None:
                        transaction.savepoint_rollback(savepoint_id)
                    continue

                # Проверяем, существует ли бикон с таким designation
                existing_beacon = Beacon.objects.filter(designation=designation).first()

                if existing_beacon:
                    # Бикон уже существует - обновляем его
                    # Проверяем конфликты уникальности перед обновлением
                    conflicts = []

                    # Проверяем mac_address (если он не пустой и отличается от текущего)
                    if mac_address and mac_address != existing_beacon.mac_address:
                        if Beacon.objects.filter(mac_address=mac_address).exclude(designation=designation).exists():
                            conflicts.append(f"MAC-адрес '{mac_address}' уже используется другим биконом")

                    # Проверяем serial_number (если он не пустой и отличается от текущего)
                    if serial_number and serial_number != existing_beacon.serial_number:
                        if Beacon.objects.filter(serial_number=serial_number).exclude(designation=designation).exists():
                            conflicts.append(f"Серийный номер '{serial_number}' уже используется другим биконом")

                    # Проверяем minor (если он не пустой и отличается от текущего)
                    if minor and minor != existing_beacon.minor:
                        if Beacon.objects.filter(minor=minor).exclude(designation=designation).exists():
                            conflicts.append(f"МИНОР '{minor}' уже используется другим биконом")

                    if conflicts:
                        error_count += 1
                        errors_list.append(f"Строка {row_idx}: {designation} - {', '.join(conflicts)}")
                        if savepoint_id is not None:
                            transaction.savepoint_rollback(savepoint_id)
                        continue

                    # Обновляем существующий бикон
                    existing_beacon.subsystem = subsystem
                    existing_beacon.number_mine = number_mine
                    existing_beacon.tunnel = tunnel
                    existing_beacon.inclined_blocks = inclined_blocks
                    existing_beacon.picket = picket
                    existing_beacon.mac_address = mac_address
                    existing_beacon.serial_number = serial_number
                    existing_beacon.minor = minor
                    existing_beacon.execution_bool = execution_bool
                    existing_beacon.data = data
                    existing_beacon.save()

                    success_count += 1
                    logger.info(f"Обновлен бикон: {designation}")
                else:
                    # Бикон не существует - создаем новый
                    # Проверяем конфликты уникальности перед созданием
                    conflicts = []

                    # Проверяем mac_address (если он не пустой)
                    if mac_address:
                        if Beacon.objects.filter(mac_address=mac_address).exists():
                            conflicts.append(f"MAC-адрес '{mac_address}' уже используется")

                    # Проверяем serial_number (если он не пустой)
                    if serial_number:
                        if Beacon.objects.filter(serial_number=serial_number).exists():
                            conflicts.append(f"Серийный номер '{serial_number}' уже используется")

                    # Проверяем minor (если он не пустой)
                    if minor:
                        if Beacon.objects.filter(minor=minor).exists():
                            conflicts.append(f"МИНОР '{minor}' уже используется")

                    if conflicts:
                        error_count += 1
                        errors_list.append(f"Строка {row_idx}: {designation} - {', '.join(conflicts)}")
                        if savepoint_id is not None:
                            transaction.savepoint_rollback(savepoint_id)
                        continue

                    # Создаем новый бикон
                    Beacon.objects.create(
                        designation=designation,
                        subsystem=subsystem,
                        number_mine=number_mine,
                        tunnel=tunnel,
                        inclined_blocks=inclined_blocks,
                        picket=picket,
                        mac_address=mac_address,
                        serial_number=serial_number,
                        minor=minor,
                        execution_bool=execution_bool,
                        data=data,
                    )

                    success_count += 1
                    logger.info(f"Создан бикон: {designation}")

                # Сохраняем изменения для этой строки
                if savepoint_id is not None:
                    transaction.savepoint_commit(savepoint_id)

            except Exception as e:
                error_count += 1
                error_msg = f"Строка {row_idx}: {str(e)}"
                errors_list.append(error_msg)
                logger.error(error_msg, exc_info=True)

                # Откатываем savepoint при ошибке
                if savepoint_id is not None:
                    try:
                        transaction.savepoint_rollback(savepoint_id)
                    except Exception:
                        pass

        logger.info(
            f"Импорт завершен. Обработано строк: {rows_processed}, пропущено пустых: {rows_skipped_empty}, успешно: {success_count}, ошибок: {error_count}")

        # Если не было обработано ни одной строки, возвращаем ошибку
        if rows_processed == 0 and success_count == 0 and error_count == 0:
            return 0, 0, ["Не удалось обработать данные. Возможно, все строки пустые или не содержат обязательных полей."]

        return success_count, error_count, errors_list

    except Exception as e:
        error_msg = f"Ошибка при чтении Excel файла: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return 0, 0, [error_msg]


def import_tunnels_from_excel(excel_file):
    """
    Импорт выработок (Tunnel) из Excel файла

    Ожидаемые колонки в Excel (первая строка - заголовки):
    - Выработка (title) - обязательное
    - Шахта (number_mine) - название шахты, например "Нефтешахта №1" - обязательное
    - Уклонный блок (inclined_blocks) - название уклонного блока - опционально
    - Признак туффитового горизонта (tuf_bool) - "Да"/"Нет" или True/False - опционально, по умолчанию False
    - Признак уклонного блока (inclined_bool) - "Да"/"Нет" или True/False - опционально, по умолчанию False
    - Описание (description) - опционально

    Args:
        excel_file: Загруженный Excel файл

    Returns:
        tuple: (success_count, error_count, errors_list)
    """
    success_count = 0
    error_count = 0
    errors_list = []

    try:
        workbook = load_workbook(excel_file, data_only=True)
        sheet = workbook.active
        logger.info(f"Начало импорта выработок из файла: {excel_file.name}")

        headers_row = list(sheet.iter_rows(min_row=1, max_row=1, values_only=True))[0]
        headers = [str(h).strip() if h is not None else None for h in headers_row]
        rows = list(sheet.iter_rows(min_row=2, values_only=True))

        if not rows:
            return 0, 0, ["Файл пуст или не содержит данных"]

        column_mapping = {
            'title': ['выработка', 'title', 'название', 'наименование'],
            'number_mine': ['шахта', 'number_mine', 'нефтешахта', 'mine'],
            'inclined_blocks': ['уклонный блок', 'inclined_blocks', 'уклонный', 'блок'],
            'tuf_bool': ['признак туффитового горизонта', 'tuf_bool', 'туффит', 'туффитовый'],
            'inclined_bool': ['признак уклонного блока', 'inclined_bool', 'уклонный блок признак'],
            'description': ['описание', 'description', 'комментарий'],
        }

        header_map = find_column_mapping(headers, column_mapping)
        logger.info(f"Найдено колонок: {len(header_map)}, маппинг: {header_map}")

        required_fields = ['title', 'number_mine']
        missing_fields = [field for field in required_fields if field not in header_map]
        if missing_fields:
            error_msg = f"Отсутствуют обязательные колонки: {', '.join(missing_fields)}"
            logger.error(error_msg)
            return 0, 0, [error_msg]

        rows_processed = 0
        rows_skipped_empty = 0

        for row_idx, row in enumerate(rows, start=2):
            savepoint_id = None
            try:
                if not any(row):
                    rows_skipped_empty += 1
                    continue

                rows_processed += 1
                savepoint_id = transaction.savepoint()

                # Выработка (обязательное)
                title_value = row[header_map['title']]
                if not title_value:
                    transaction.savepoint_rollback(savepoint_id)
                    continue
                title = str(title_value).strip()
                if not title:
                    transaction.savepoint_rollback(savepoint_id)
                    continue

                # Шахта (обязательное)
                number_mine_str = str(row[header_map['number_mine']]).strip(
                ) if row[header_map['number_mine']] else None
                if not number_mine_str:
                    error_count += 1
                    errors_list.append(f"Строка {row_idx}: Шахта не указана")
                    transaction.savepoint_rollback(savepoint_id)
                    continue

                number_mine = NumberMine.objects.filter(title__icontains=number_mine_str).first()
                if not number_mine:
                    error_count += 1
                    errors_list.append(f"Строка {row_idx}: Шахта '{number_mine_str}' не найдена")
                    transaction.savepoint_rollback(savepoint_id)
                    continue

                # Уклонный блок (опционально)
                inclined_blocks = None
                if 'inclined_blocks' in header_map and row[header_map['inclined_blocks']]:
                    inclined_blocks_str = str(row[header_map['inclined_blocks']]).strip()
                    if inclined_blocks_str:
                        inclined_blocks = InclinedBlocks.objects.filter(
                            title__icontains=inclined_blocks_str,
                            number_mine=number_mine
                        ).first()
                        if not inclined_blocks:
                            logger.warning(f"Строка {row_idx}: Уклонный блок '{inclined_blocks_str}' не найден")

                # Признак туффитового горизонта (опционально)
                tuf_bool = False
                if 'tuf_bool' in header_map and row[header_map['tuf_bool']]:
                    tuf_value = str(row[header_map['tuf_bool']]).strip().lower()
                    tuf_bool = tuf_value in ['да', 'yes', 'true', '1']

                # Признак уклонного блока (опционально)
                inclined_bool = False
                if 'inclined_bool' in header_map and row[header_map['inclined_bool']]:
                    inclined_value = str(row[header_map['inclined_bool']]).strip().lower()
                    inclined_bool = inclined_value in ['да', 'yes', 'true', '1']

                # Описание (опционально)
                description = None
                if 'description' in header_map and row[header_map['description']]:
                    description = str(row[header_map['description']]).strip()

                # Создаем или обновляем выработку
                tunnel, created = Tunnel.objects.update_or_create(
                    title=title,
                    number_mine=number_mine,
                    defaults={
                        'inclined_blocks': inclined_blocks,
                        'tuf_bool': tuf_bool,
                        'inclined_bool': inclined_bool,
                        'description': description,
                    }
                )

                success_count += 1
                logger.info(f"{'Создана' if created else 'Обновлена'} выработка: {tunnel}")

                if savepoint_id is not None:
                    transaction.savepoint_commit(savepoint_id)

            except Exception as e:
                error_count += 1
                error_msg = f"Строка {row_idx}: {str(e)}"
                errors_list.append(error_msg)
                logger.error(error_msg, exc_info=True)
                if savepoint_id is not None:
                    try:
                        transaction.savepoint_rollback(savepoint_id)
                    except Exception:
                        pass

        logger.info(f"Импорт завершен. Обработано: {rows_processed}, успешно: {success_count}, ошибок: {error_count}")
        if rows_processed == 0 and success_count == 0 and error_count == 0:
            return 0, 0, ["Не удалось обработать данные"]

        return success_count, error_count, errors_list

    except Exception as e:
        error_msg = f"Ошибка при чтении Excel файла: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return 0, 0, [error_msg]


def import_equipment_from_excel(excel_file):
    """
    Импорт оборудования из Excel файла

    Ожидаемые колонки в Excel (первая строка - заголовки):
    - Оборудование (title) - обязательное
    - Тип (device_type) - опционально
    - Подсистема (subsystem) - название подсистемы - опционально
    - Описание (description) - опционально

    Args:
        excel_file: Загруженный Excel файл

    Returns:
        tuple: (success_count, error_count, errors_list)
    """
    success_count = 0
    error_count = 0
    errors_list = []

    try:
        workbook = load_workbook(excel_file, data_only=True)
        sheet = workbook.active
        logger.info(f"Начало импорта оборудования из файла: {excel_file.name}")

        headers_row = list(sheet.iter_rows(min_row=1, max_row=1, values_only=True))[0]
        headers = [str(h).strip() if h is not None else None for h in headers_row]
        rows = list(sheet.iter_rows(min_row=2, values_only=True))

        if not rows:
            return 0, 0, ["Файл пуст или не содержит данных"]

        column_mapping = {
            'title': ['оборудование', 'title', 'название', 'наименование'],
            'device_type': ['тип', 'device_type', 'тип оборудования'],
            'subsystem': ['подсистема', 'subsystem'],
            'description': ['описание', 'description', 'комментарий'],
        }

        header_map = find_column_mapping(headers, column_mapping)
        logger.info(f"Найдено колонок: {len(header_map)}, маппинг: {header_map}")

        required_fields = ['title']
        missing_fields = [field for field in required_fields if field not in header_map]
        if missing_fields:
            error_msg = f"Отсутствуют обязательные колонки: {', '.join(missing_fields)}"
            logger.error(error_msg)
            return 0, 0, [error_msg]

        rows_processed = 0
        rows_skipped_empty = 0

        for row_idx, row in enumerate(rows, start=2):
            savepoint_id = None
            try:
                if not any(row):
                    rows_skipped_empty += 1
                    continue

                rows_processed += 1
                savepoint_id = transaction.savepoint()

                # Оборудование (обязательное)
                title_value = row[header_map['title']]
                if not title_value:
                    transaction.savepoint_rollback(savepoint_id)
                    continue
                title = truncate_field(title_value, 150)
                if not title:
                    transaction.savepoint_rollback(savepoint_id)
                    continue

                # Тип (опционально)
                device_type = None
                if 'device_type' in header_map and row[header_map['device_type']]:
                    device_type = truncate_field(row[header_map['device_type']], 50)

                # Подсистема (опционально)
                subsystem = None
                if 'subsystem' in header_map and row[header_map['subsystem']]:
                    subsystem_str = str(row[header_map['subsystem']]).strip()
                    if subsystem_str:
                        subsystem = Subsystem.objects.filter(title__icontains=subsystem_str).first()
                        if not subsystem:
                            logger.warning(f"Строка {row_idx}: Подсистема '{subsystem_str}' не найдена")

                # Описание (опционально)
                description = None
                if 'description' in header_map and row[header_map['description']]:
                    description = str(row[header_map['description']]).strip()

                # Создаем или обновляем оборудование
                equipment, created = Equipment.objects.update_or_create(
                    title=title,
                    defaults={
                        'device_type': device_type,
                        'subsystem': subsystem,
                        'description': description,
                    }
                )

                success_count += 1
                logger.info(f"{'Создано' if created else 'Обновлено'} оборудование: {equipment}")

                if savepoint_id is not None:
                    transaction.savepoint_commit(savepoint_id)

            except Exception as e:
                error_count += 1
                error_msg = f"Строка {row_idx}: {str(e)}"
                errors_list.append(error_msg)
                logger.error(error_msg, exc_info=True)
                if savepoint_id is not None:
                    try:
                        transaction.savepoint_rollback(savepoint_id)
                    except Exception:
                        pass

        logger.info(f"Импорт завершен. Обработано: {rows_processed}, успешно: {success_count}, ошибок: {error_count}")
        if rows_processed == 0 and success_count == 0 and error_count == 0:
            return 0, 0, ["Не удалось обработать данные"]

        return success_count, error_count, errors_list

    except Exception as e:
        error_msg = f"Ошибка при чтении Excel файла: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return 0, 0, [error_msg]


def import_pointphones_from_excel(excel_file):
    """
    Импорт точек телефонии из Excel файла

    Ожидаемые колонки в Excel (первая строка - заголовки):
    - Обозначение в проекте (title) - обязательное
    - Шахта (number_mine) - название шахты, например "Нефтешахта №1" - обязательное
    - Абонентский номер (subscriber_number) - обязательное
    - Выработка (tunnel) - название выработки - опционально
    - Уклонный блок (inclined_blocks) - название уклонного блока - опционально
    - Пикет (picket) - опционально
    - Зав. № (serial_number) - опционально
    - Тип (device_type) - опционально
    - Описание (description) - опционально

    Args:
        excel_file: Загруженный Excel файл

    Returns:
        tuple: (success_count, error_count, errors_list)
    """
    success_count = 0
    error_count = 0
    errors_list = []

    try:
        workbook = load_workbook(excel_file, data_only=True)
        sheet = workbook.active
        logger.info(f"Начало импорта точек телефонии из файла: {excel_file.name}")

        headers_row = list(sheet.iter_rows(min_row=1, max_row=1, values_only=True))[0]
        headers = [str(h).strip() if h is not None else None for h in headers_row]
        rows = list(sheet.iter_rows(min_row=2, values_only=True))

        if not rows:
            return 0, 0, ["Файл пуст или не содержит данных"]

        column_mapping = {
            'title': ['обозначение в проекте', 'title', 'обозначение', 'название'],
            'number_mine': ['шахта', 'number_mine', 'нефтешахта', 'mine'],
            'subscriber_number': ['абонентский номер', 'subscriber_number', 'номер', 'абонентский'],
            'tunnel': ['выработка', 'tunnel', 'горная выработка'],
            'inclined_blocks': ['уклонный блок', 'inclined_blocks', 'уклонный', 'блок'],
            'picket': ['пикет', 'picket'],
            'serial_number': ['зав. №', 'зав №', 'serial_number', 'серийный номер', 'зав.№', 'зав№'],
            'device_type': ['тип', 'device_type', 'тип устройства'],
            'description': ['описание', 'description', 'комментарий'],
        }

        header_map = find_column_mapping(headers, column_mapping)
        logger.info(f"Найдено колонок: {len(header_map)}, маппинг: {header_map}")

        required_fields = ['title', 'number_mine', 'subscriber_number']
        missing_fields = [field for field in required_fields if field not in header_map]
        if missing_fields:
            error_msg = f"Отсутствуют обязательные колонки: {', '.join(missing_fields)}"
            logger.error(error_msg)
            return 0, 0, [error_msg]

        rows_processed = 0
        rows_skipped_empty = 0

        for row_idx, row in enumerate(rows, start=2):
            savepoint_id = None
            try:
                if not any(row):
                    rows_skipped_empty += 1
                    continue

                rows_processed += 1
                savepoint_id = transaction.savepoint()

                # Обозначение в проекте (обязательное)
                title_value = row[header_map['title']]
                if not title_value:
                    transaction.savepoint_rollback(savepoint_id)
                    continue
                title = truncate_field(title_value, 100)
                if not title:
                    transaction.savepoint_rollback(savepoint_id)
                    continue

                # Шахта (обязательное)
                number_mine_str = str(row[header_map['number_mine']]).strip(
                ) if row[header_map['number_mine']] else None
                if not number_mine_str:
                    error_count += 1
                    errors_list.append(f"Строка {row_idx}: Шахта не указана")
                    transaction.savepoint_rollback(savepoint_id)
                    continue

                number_mine = NumberMine.objects.filter(title__icontains=number_mine_str).first()
                if not number_mine:
                    error_count += 1
                    errors_list.append(f"Строка {row_idx}: Шахта '{number_mine_str}' не найдена")
                    transaction.savepoint_rollback(savepoint_id)
                    continue

                # Абонентский номер (обязательное)
                subscriber_number_value = row[header_map['subscriber_number']]
                if not subscriber_number_value:
                    error_count += 1
                    errors_list.append(f"Строка {row_idx}: Абонентский номер не указан")
                    transaction.savepoint_rollback(savepoint_id)
                    continue
                subscriber_number = truncate_field(subscriber_number_value, 10)

                # Выработка (опционально)
                tunnel = None
                if 'tunnel' in header_map and row[header_map['tunnel']]:
                    tunnel_str = str(row[header_map['tunnel']]).strip()
                    if tunnel_str:
                        tunnel = Tunnel.objects.filter(
                            title__icontains=tunnel_str,
                            number_mine=number_mine
                        ).first()
                        if not tunnel:
                            logger.warning(f"Строка {row_idx}: Выработка '{tunnel_str}' не найдена")

                # Уклонный блок (опционально)
                inclined_blocks = None
                if 'inclined_blocks' in header_map and row[header_map['inclined_blocks']]:
                    inclined_blocks_str = str(row[header_map['inclined_blocks']]).strip()
                    if inclined_blocks_str:
                        inclined_blocks = InclinedBlocks.objects.filter(
                            title__icontains=inclined_blocks_str,
                            number_mine=number_mine
                        ).first()
                        if not inclined_blocks:
                            logger.warning(f"Строка {row_idx}: Уклонный блок '{inclined_blocks_str}' не найден")

                # Пикет (опционально)
                picket = None
                if 'picket' in header_map and row[header_map['picket']]:
                    picket = truncate_field(row[header_map['picket']], 100)

                # Зав. № (опционально)
                serial_number = None
                if 'serial_number' in header_map and row[header_map['serial_number']]:
                    serial_number = truncate_field(row[header_map['serial_number']], 50)

                # Тип (опционально)
                device_type = None
                if 'device_type' in header_map and row[header_map['device_type']]:
                    device_type = truncate_field(row[header_map['device_type']], 50)

                # Описание (опционально)
                description = None
                if 'description' in header_map and row[header_map['description']]:
                    description = str(row[header_map['description']]).strip()

                # Проверяем уникальность по title и subscriber_number
                existing = PointPhone.objects.filter(title=title, subscriber_number=subscriber_number).first()

                if existing:
                    # Обновляем существующую запись
                    existing.number_mine = number_mine
                    existing.tunnel = tunnel
                    existing.inclined_blocks = inclined_blocks
                    existing.picket = picket
                    existing.serial_number = serial_number
                    existing.device_type = device_type
                    existing.description = description
                    existing.save()
                    success_count += 1
                    logger.info(f"Обновлена точка телефонии: {existing}")
                else:
                    # Создаем новую запись
                    PointPhone.objects.create(
                        title=title,
                        number_mine=number_mine,
                        subscriber_number=subscriber_number,
                        tunnel=tunnel,
                        inclined_blocks=inclined_blocks,
                        picket=picket,
                        serial_number=serial_number,
                        device_type=device_type,
                        description=description,
                    )
                    success_count += 1
                    logger.info(f"Создана точка телефонии: {title}/{subscriber_number}")

                if savepoint_id is not None:
                    transaction.savepoint_commit(savepoint_id)

            except Exception as e:
                error_count += 1
                error_msg = f"Строка {row_idx}: {str(e)}"
                errors_list.append(error_msg)
                logger.error(error_msg, exc_info=True)
                if savepoint_id is not None:
                    try:
                        transaction.savepoint_rollback(savepoint_id)
                    except Exception:
                        pass

        logger.info(f"Импорт завершен. Обработано: {rows_processed}, успешно: {success_count}, ошибок: {error_count}")
        if rows_processed == 0 and success_count == 0 and error_count == 0:
            return 0, 0, ["Не удалось обработать данные"]

        return success_count, error_count, errors_list

    except Exception as e:
        error_msg = f"Ошибка при чтении Excel файла: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return 0, 0, [error_msg]


def import_branchesbox_from_excel(excel_file):
    """
    Импорт распределительных коробок из Excel файла

    Ожидаемые колонки в Excel (первая строка - заголовки):
    - Обозначение в проекте (title) - обязательное
    - Шахта (number_mine) - название шахты, например "Нефтешахта №1" - обязательное
    - Выработка (tunnel) - название выработки - опционально
    - Уклонный блок (inclined_blocks) - название уклонного блока - опционально
    - Подсистема (subsystem) - название подсистемы - опционально
    - Связанное оборудование (equipment) - обозначение оборудования (name из EquipmentInstallation) - опционально
    - Пикет (picket) - опционально
    - Признак уклонного блока (boolean_block) - "Да"/"Нет" или True/False - опционально, по умолчанию False
    - IP адрес (ip_address) - опционально
    - Зав. № (serial_number) - опционально
    - Тип (device_type) - опционально
    - Описание (description) - опционально

    Args:
        excel_file: Загруженный Excel файл

    Returns:
        tuple: (success_count, error_count, errors_list)
    """
    success_count = 0
    error_count = 0
    errors_list = []

    try:
        workbook = load_workbook(excel_file, data_only=True)
        sheet = workbook.active
        logger.info(f"Начало импорта распределительных коробок из файла: {excel_file.name}")

        headers_row = list(sheet.iter_rows(min_row=1, max_row=1, values_only=True))[0]
        headers = [str(h).strip() if h is not None else None for h in headers_row]
        rows = list(sheet.iter_rows(min_row=2, values_only=True))

        if not rows:
            return 0, 0, ["Файл пуст или не содержит данных"]

        column_mapping = {
            'title': ['обозначение в проекте', 'title', 'обозначение', 'название'],
            'number_mine': ['шахта', 'number_mine', 'нефтешахта', 'mine'],
            'tunnel': ['выработка', 'tunnel', 'горная выработка'],
            'inclined_blocks': ['уклонный блок', 'inclined_blocks', 'уклонный', 'блок'],
            'subsystem': ['подсистема', 'subsystem'],
            'equipment': ['связанное оборудование', 'equipment', 'оборудование', 'место установки'],
            'picket': ['пикет', 'picket'],
            'boolean_block': ['признак уклонного блока', 'boolean_block', 'признак блока'],
            'ip_address': ['ip адрес', 'ip_address', 'ip', 'адрес'],
            'serial_number': ['зав. №', 'зав №', 'serial_number', 'серийный номер', 'зав.№', 'зав№'],
            'device_type': ['тип', 'device_type', 'тип устройства'],
            'description': ['описание', 'description', 'комментарий'],
        }

        header_map = find_column_mapping(headers, column_mapping)
        logger.info(f"Найдено колонок: {len(header_map)}, маппинг: {header_map}")

        required_fields = ['title', 'number_mine']
        missing_fields = [field for field in required_fields if field not in header_map]
        if missing_fields:
            error_msg = f"Отсутствуют обязательные колонки: {', '.join(missing_fields)}"
            logger.error(error_msg)
            return 0, 0, [error_msg]

        rows_processed = 0
        rows_skipped_empty = 0

        for row_idx, row in enumerate(rows, start=2):
            savepoint_id = None
            try:
                if not any(row):
                    rows_skipped_empty += 1
                    continue

                rows_processed += 1
                savepoint_id = transaction.savepoint()

                # Обозначение в проекте (обязательное)
                title_value = row[header_map['title']]
                if not title_value:
                    transaction.savepoint_rollback(savepoint_id)
                    continue
                title = truncate_field(title_value, 100)
                if not title:
                    transaction.savepoint_rollback(savepoint_id)
                    continue

                # Шахта (обязательное)
                number_mine_str = str(row[header_map['number_mine']]).strip(
                ) if row[header_map['number_mine']] else None
                if not number_mine_str:
                    error_count += 1
                    errors_list.append(f"Строка {row_idx}: Шахта не указана")
                    transaction.savepoint_rollback(savepoint_id)
                    continue

                number_mine = NumberMine.objects.filter(title__icontains=number_mine_str).first()
                if not number_mine:
                    error_count += 1
                    errors_list.append(f"Строка {row_idx}: Шахта '{number_mine_str}' не найдена")
                    transaction.savepoint_rollback(savepoint_id)
                    continue

                # Выработка (опционально)
                tunnel = None
                if 'tunnel' in header_map and row[header_map['tunnel']]:
                    tunnel_str = str(row[header_map['tunnel']]).strip()
                    if tunnel_str:
                        tunnel = Tunnel.objects.filter(
                            title__icontains=tunnel_str,
                            number_mine=number_mine
                        ).first()
                        if not tunnel:
                            logger.warning(f"Строка {row_idx}: Выработка '{tunnel_str}' не найдена")

                # Уклонный блок (опционально)
                inclined_blocks = None
                if 'inclined_blocks' in header_map and row[header_map['inclined_blocks']]:
                    inclined_blocks_str = str(row[header_map['inclined_blocks']]).strip()
                    if inclined_blocks_str:
                        inclined_blocks = InclinedBlocks.objects.filter(
                            title__icontains=inclined_blocks_str,
                            number_mine=number_mine
                        ).first()
                        if not inclined_blocks:
                            logger.warning(f"Строка {row_idx}: Уклонный блок '{inclined_blocks_str}' не найден")

                # Подсистема (опционально)
                subsystem = None
                if 'subsystem' in header_map and row[header_map['subsystem']]:
                    subsystem_str = str(row[header_map['subsystem']]).strip()
                    if subsystem_str:
                        subsystem = Subsystem.objects.filter(title__icontains=subsystem_str).first()
                        if not subsystem:
                            logger.warning(f"Строка {row_idx}: Подсистема '{subsystem_str}' не найдена")

                # Связанное оборудование (опционально)
                equipment = None
                if 'equipment' in header_map and row[header_map['equipment']]:
                    equipment_name = str(row[header_map['equipment']]).strip()
                    if equipment_name:
                        equipment = EquipmentInstallation.objects.filter(name__icontains=equipment_name).first()
                        if not equipment:
                            logger.warning(f"Строка {row_idx}: Оборудование '{equipment_name}' не найдено")

                # Пикет (опционально)
                picket = None
                if 'picket' in header_map and row[header_map['picket']]:
                    picket = truncate_field(row[header_map['picket']], 100)

                # Признак уклонного блока (опционально)
                boolean_block = False
                if 'boolean_block' in header_map and row[header_map['boolean_block']]:
                    block_value = str(row[header_map['boolean_block']]).strip().lower()
                    boolean_block = block_value in ['да', 'yes', 'true', '1']

                # IP адрес (опционально)
                ip_address = None
                if 'ip_address' in header_map and row[header_map['ip_address']]:
                    ip_address = truncate_field(row[header_map['ip_address']], 13)

                # Зав. № (опционально)
                serial_number = None
                if 'serial_number' in header_map and row[header_map['serial_number']]:
                    serial_number = truncate_field(row[header_map['serial_number']], 50)

                # Тип (опционально)
                device_type = None
                if 'device_type' in header_map and row[header_map['device_type']]:
                    device_type = truncate_field(row[header_map['device_type']], 50)

                # Описание (опционально)
                description = None
                if 'description' in header_map and row[header_map['description']]:
                    description = str(row[header_map['description']]).strip()

                # Создаем или обновляем распределительную коробку
                branches_box, created = BranchesBox.objects.update_or_create(
                    title=title,
                    number_mine=number_mine,
                    defaults={
                        'tunnel': tunnel,
                        'inclined_blocks': inclined_blocks,
                        'subsystem': subsystem,
                        'equipment': equipment,
                        'picket': picket,
                        'boolean_block': boolean_block,
                        'ip_address': ip_address,
                        'serial_number': serial_number,
                        'device_type': device_type,
                        'description': description,
                    }
                )

                success_count += 1
                logger.info(f"{'Создана' if created else 'Обновлена'} распределительная коробка: {branches_box}")

                if savepoint_id is not None:
                    transaction.savepoint_commit(savepoint_id)

            except Exception as e:
                error_count += 1
                error_msg = f"Строка {row_idx}: {str(e)}"
                errors_list.append(error_msg)
                logger.error(error_msg, exc_info=True)
                if savepoint_id is not None:
                    try:
                        transaction.savepoint_rollback(savepoint_id)
                    except Exception:
                        pass

        logger.info(f"Импорт завершен. Обработано: {rows_processed}, успешно: {success_count}, ошибок: {error_count}")
        if rows_processed == 0 and success_count == 0 and error_count == 0:
            return 0, 0, ["Не удалось обработать данные"]

        return success_count, error_count, errors_list

    except Exception as e:
        error_msg = f"Ошибка при чтении Excel файла: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return 0, 0, [error_msg]


def import_equipmentinstallation_from_excel(excel_file):
    """
    Импорт мест установки оборудования из Excel файла

    Ожидаемые колонки в Excel (первая строка - заголовки):
    - Оборудование (title) - название оборудования из таблицы Equipment - обязательное
    - Обозначение в проекте (name) - опционально (может быть заполнено из point_phone или branches_box)
    - Шахта (number_mine) - название шахты - опционально (может быть заполнено из point_phone или branches_box)
    - Выработка (tunnel) - название выработки - опционально
    - Уклонный блок (inclined_blocks) - название уклонного блока - опционально
    - Подсистема (subsystem) - название подсистемы - опционально (по умолчанию "АТС" если указан point_phone)
    - Точка телефонии (point_phone) - обозначение точки телефонии (title из PointPhone) - опционально
    - Распределительная коробка (branches_box) - обозначение коробки (title из BranchesBox) - опционально
    - Пикет (picket) - опционально
    - IP адрес (ip_address) - опционально
    - Зав. № (serial_number) - опционально
    - Тип (device_type) - опционально
    - Описание (description) - опционально

    Примечание:
    - Если указана point_phone, многие поля будут автоматически заполнены из неё
    - Если указана branches_box, многие поля будут автоматически заполнены из неё
    - Приоритет: point_phone > branches_box > прямые значения

    Args:
        excel_file: Загруженный Excel файл

    Returns:
        tuple: (success_count, error_count, errors_list)
    """
    success_count = 0
    error_count = 0
    errors_list = []

    try:
        workbook = load_workbook(excel_file, data_only=True)
        sheet = workbook.active
        logger.info(f"Начало импорта мест установки оборудования из файла: {excel_file.name}")

        headers_row = list(sheet.iter_rows(min_row=1, max_row=1, values_only=True))[0]
        headers = [str(h).strip() if h is not None else None for h in headers_row]
        rows = list(sheet.iter_rows(min_row=2, values_only=True))

        if not rows:
            return 0, 0, ["Файл пуст или не содержит данных"]

        column_mapping = {
            'title': ['оборудование', 'title', 'тип оборудования', 'equipment'],
            'name': ['обозначение в проекте', 'name', 'обозначение'],
            'number_mine': ['шахта', 'number_mine', 'нефтешахта', 'mine'],
            'tunnel': ['выработка', 'tunnel', 'горная выработка'],
            'inclined_blocks': ['уклонный блок', 'inclined_blocks', 'уклонный', 'блок'],
            'subsystem': ['подсистема', 'subsystem'],
            'point_phone': ['точка телефонии', 'point_phone', 'телефония', 'точка'],
            'branches_box': ['распределительная коробка', 'branches_box', 'коробка', 'распред.коробка'],
            'picket': ['пикет', 'picket'],
            'ip_address': ['ip адрес', 'ip_address', 'ip', 'адрес'],
            'serial_number': ['зав. №', 'зав №', 'serial_number', 'серийный номер', 'зав.№', 'зав№'],
            'device_type': ['тип', 'device_type', 'тип устройства'],
            'description': ['описание', 'description', 'комментарий'],
        }

        header_map = find_column_mapping(headers, column_mapping)
        logger.info(f"Найдено колонок: {len(header_map)}, маппинг: {header_map}")

        required_fields = ['title']
        missing_fields = [field for field in required_fields if field not in header_map]
        if missing_fields:
            error_msg = f"Отсутствуют обязательные колонки: {', '.join(missing_fields)}"
            logger.error(error_msg)
            return 0, 0, [error_msg]

        rows_processed = 0
        rows_skipped_empty = 0

        for row_idx, row in enumerate(rows, start=2):
            savepoint_id = None
            try:
                if not any(row):
                    rows_skipped_empty += 1
                    continue

                rows_processed += 1
                savepoint_id = transaction.savepoint()

                # Оборудование (обязательное)
                title_str = str(row[header_map['title']]).strip() if row[header_map['title']] else None
                if not title_str:
                    transaction.savepoint_rollback(savepoint_id)
                    continue

                title = Equipment.objects.filter(title__icontains=title_str).first()
                if not title:
                    error_count += 1
                    errors_list.append(f"Строка {row_idx}: Оборудование '{title_str}' не найдено")
                    transaction.savepoint_rollback(savepoint_id)
                    continue

                # Точка телефонии (опционально)
                point_phone = None
                if 'point_phone' in header_map and row[header_map['point_phone']]:
                    point_phone_str = str(row[header_map['point_phone']]).strip()
                    if point_phone_str:
                        point_phone = PointPhone.objects.filter(title__icontains=point_phone_str).first()
                        if not point_phone:
                            logger.warning(f"Строка {row_idx}: Точка телефонии '{point_phone_str}' не найдена")

                # Распределительная коробка (опционально)
                branches_box = None
                if 'branches_box' in header_map and row[header_map['branches_box']]:
                    branches_box_str = str(row[header_map['branches_box']]).strip()
                    if branches_box_str:
                        branches_box = BranchesBox.objects.filter(title__icontains=branches_box_str).first()
                        if not branches_box:
                            logger.warning(
                                f"Строка {row_idx}: Распределительная коробка '{branches_box_str}' не найдена")

                # Если указаны и point_phone и branches_box, используем point_phone (приоритет)
                if point_phone and branches_box:
                    logger.warning(
                        f"Строка {row_idx}: Указаны и точка телефонии, и коробка. Используется точка телефонии.")
                    branches_box = None

                # Если указана point_phone или branches_box, многие поля заполнятся автоматически в save()
                # Но мы можем указать дополнительные поля напрямую

                # Обозначение в проекте (опционально, если не указана point_phone/branches_box)
                name = None
                if not point_phone and not branches_box:
                    if 'name' in header_map and row[header_map['name']]:
                        name = truncate_field(row[header_map['name']], 100)

                # Шахта (опционально, если не указана point_phone/branches_box)
                number_mine = None
                if not point_phone and not branches_box:
                    if 'number_mine' in header_map and row[header_map['number_mine']]:
                        number_mine_str = str(row[header_map['number_mine']]).strip()
                        if number_mine_str:
                            number_mine = NumberMine.objects.filter(title__icontains=number_mine_str).first()
                            if not number_mine:
                                logger.warning(f"Строка {row_idx}: Шахта '{number_mine_str}' не найдена")

                # Выработка (опционально, если не указана point_phone/branches_box)
                tunnel = None
                if not point_phone and not branches_box:
                    if 'tunnel' in header_map and row[header_map['tunnel']]:
                        tunnel_str = str(row[header_map['tunnel']]).strip()
                        if tunnel_str:
                            tunnel = Tunnel.objects.filter(title__icontains=tunnel_str).first()
                            if not tunnel:
                                logger.warning(f"Строка {row_idx}: Выработка '{tunnel_str}' не найдена")

                # Уклонный блок (опционально, если не указана point_phone/branches_box)
                inclined_blocks = None
                if not point_phone and not branches_box:
                    if 'inclined_blocks' in header_map and row[header_map['inclined_blocks']]:
                        inclined_blocks_str = str(row[header_map['inclined_blocks']]).strip()
                        if inclined_blocks_str:
                            # Нужна шахта для поиска уклонного блока
                            if number_mine:
                                inclined_blocks = InclinedBlocks.objects.filter(
                                    title__icontains=inclined_blocks_str,
                                    number_mine=number_mine
                                ).first()
                                if not inclined_blocks:
                                    logger.warning(
                                        f"Строка {row_idx}: Уклонный блок '{inclined_blocks_str}' не найден")

                # Подсистема (опционально, если не указана point_phone/branches_box)
                subsystem = None
                if not point_phone and not branches_box:
                    if 'subsystem' in header_map and row[header_map['subsystem']]:
                        subsystem_str = str(row[header_map['subsystem']]).strip()
                        if subsystem_str:
                            subsystem = Subsystem.objects.filter(title__icontains=subsystem_str).first()
                            if not subsystem:
                                logger.warning(f"Строка {row_idx}: Подсистема '{subsystem_str}' не найдена")

                # Пикет (опционально, если не указана point_phone/branches_box)
                picket = None
                if not point_phone and not branches_box:
                    if 'picket' in header_map and row[header_map['picket']]:
                        picket = truncate_field(row[header_map['picket']], 100)

                # IP адрес (опционально, если не указана branches_box)
                ip_address = None
                if not branches_box:
                    if 'ip_address' in header_map and row[header_map['ip_address']]:
                        ip_address = truncate_field(row[header_map['ip_address']], 13)

                # Зав. № (опционально, если не указана point_phone/branches_box)
                serial_number = None
                if not point_phone and not branches_box:
                    if 'serial_number' in header_map and row[header_map['serial_number']]:
                        serial_number = truncate_field(row[header_map['serial_number']], 50)

                # Тип (опционально, если не указана point_phone/branches_box)
                device_type = None
                if not point_phone and not branches_box:
                    if 'device_type' in header_map and row[header_map['device_type']]:
                        device_type = truncate_field(row[header_map['device_type']], 50)

                # Описание (опционально)
                description = None
                if 'description' in header_map and row[header_map['description']]:
                    description = str(row[header_map['description']]).strip()

                # Создаем или обновляем место установки оборудования
                # Используем title и name как уникальные идентификаторы
                defaults = {
                    'point_phone': point_phone,
                    'branches_box': branches_box,
                    'description': description,
                }

                # Добавляем поля только если не указаны point_phone/branches_box
                if not point_phone and not branches_box:
                    defaults.update({
                        'name': name,
                        'number_mine': number_mine,
                        'tunnel': tunnel,
                        'inclined_blocks': inclined_blocks,
                        'subsystem': subsystem,
                        'picket': picket,
                        'ip_address': ip_address,
                        'serial_number': serial_number,
                        'device_type': device_type,
                    })

                equipment_install, created = EquipmentInstallation.objects.update_or_create(
                    title=title,
                    name=name if not point_phone and not branches_box else None,
                    defaults=defaults
                )

                success_count += 1
                logger.info(f"{'Создано' if created else 'Обновлено'} место установки оборудования: {equipment_install}")

                if savepoint_id is not None:
                    transaction.savepoint_commit(savepoint_id)

            except Exception as e:
                error_count += 1
                error_msg = f"Строка {row_idx}: {str(e)}"
                errors_list.append(error_msg)
                logger.error(error_msg, exc_info=True)
                if savepoint_id is not None:
                    try:
                        transaction.savepoint_rollback(savepoint_id)
                    except Exception:
                        pass

        logger.info(f"Импорт завершен. Обработано: {rows_processed}, успешно: {success_count}, ошибок: {error_count}")
        if rows_processed == 0 and success_count == 0 and error_count == 0:
            return 0, 0, ["Не удалось обработать данные"]

        return success_count, error_count, errors_list

    except Exception as e:
        error_msg = f"Ошибка при чтении Excel файла: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return 0, 0, [error_msg]


def import_cablemagazine_from_excel(excel_file):
    """
    Импорт кабельного журнала из Excel файла

    Ожидаемые колонки в Excel (первая строка - заголовки):
    - Кабель (cable) - название кабеля из таблицы Cable - обязательное
    - Подсистема (subsystem) - название подсистемы - обязательное
    - Шахта (number_mine) - название шахты, например "Нефтешахта №1" - обязательное
    - Протяженность (distance) - обязательное
    - Единица измерения (unit) - например "м." или "км." - обязательное
    - Уклонный блок (inclined_blocks) - название уклонного блока - опционально
    - От оборудования (track_from) - обозначение оборудования (name из EquipmentInstallation) - опционально
    - До оборудования (track_to) - обозначение оборудования (name из EquipmentInstallation) - опционально

    Примечание:
    - Поле "Трасса от - до" (name) будет автоматически сгенерировано из track_from и track_to
    - Формат: "от/до" или "от/?" или "?/до" или "?/?" если не указаны

    Args:
        excel_file: Загруженный Excel файл

    Returns:
        tuple: (success_count, error_count, errors_list)
    """
    success_count = 0
    error_count = 0
    errors_list = []

    try:
        workbook = load_workbook(excel_file, data_only=True)
        sheet = workbook.active
        logger.info(f"Начало импорта кабельного журнала из файла: {excel_file.name}")

        headers_row = list(sheet.iter_rows(min_row=1, max_row=1, values_only=True))[0]
        headers = [str(h).strip() if h is not None else None for h in headers_row]
        rows = list(sheet.iter_rows(min_row=2, values_only=True))

        if not rows:
            return 0, 0, ["Файл пуст или не содержит данных"]

        column_mapping = {
            'cable': ['кабель', 'cable', 'тип кабеля', 'название кабеля'],
            'subsystem': ['подсистема', 'subsystem'],
            'number_mine': ['шахта', 'number_mine', 'нефтешахта', 'mine'],
            'distance': ['протяженность', 'distance', 'длина', 'расстояние'],
            'unit': ['единица измерения', 'unit', 'единица', 'ед.изм'],
            'inclined_blocks': ['уклонный блок', 'inclined_blocks', 'уклонный', 'блок'],
            'track_from': ['от оборудования', 'track_from', 'от', 'от оборудования', 'от точки'],
            'track_to': ['до оборудования', 'track_to', 'до', 'до оборудования', 'до точки'],
        }

        header_map = find_column_mapping(headers, column_mapping)
        logger.info(f"Найдено колонок: {len(header_map)}, маппинг: {header_map}")

        required_fields = ['cable', 'subsystem', 'number_mine', 'distance', 'unit']
        missing_fields = [field for field in required_fields if field not in header_map]
        if missing_fields:
            error_msg = f"Отсутствуют обязательные колонки: {', '.join(missing_fields)}"
            logger.error(error_msg)
            return 0, 0, [error_msg]

        rows_processed = 0
        rows_skipped_empty = 0

        for row_idx, row in enumerate(rows, start=2):
            savepoint_id = None
            try:
                if not any(row):
                    rows_skipped_empty += 1
                    continue

                rows_processed += 1
                savepoint_id = transaction.savepoint()

                # Кабель (обязательное)
                cable_str = str(row[header_map['cable']]).strip() if row[header_map['cable']] else None
                if not cable_str:
                    error_count += 1
                    errors_list.append(f"Строка {row_idx}: Кабель не указан")
                    transaction.savepoint_rollback(savepoint_id)
                    continue

                # Ищем кабель
                cable = Cable.objects.filter(title__icontains=cable_str).first()
                if not cable:
                    error_count += 1
                    errors_list.append(f"Строка {row_idx}: Кабель '{cable_str}' не найден")
                    transaction.savepoint_rollback(savepoint_id)
                    continue

                # Подсистема (обязательное)
                subsystem_str = str(row[header_map['subsystem']]).strip() if row[header_map['subsystem']] else None
                if not subsystem_str:
                    error_count += 1
                    errors_list.append(f"Строка {row_idx}: Подсистема не указана")
                    transaction.savepoint_rollback(savepoint_id)
                    continue

                subsystem = Subsystem.objects.filter(title__icontains=subsystem_str).first()
                if not subsystem:
                    error_count += 1
                    errors_list.append(f"Строка {row_idx}: Подсистема '{subsystem_str}' не найдена")
                    transaction.savepoint_rollback(savepoint_id)
                    continue

                # Шахта (обязательное)
                number_mine_str = str(row[header_map['number_mine']]).strip(
                ) if row[header_map['number_mine']] else None
                if not number_mine_str:
                    error_count += 1
                    errors_list.append(f"Строка {row_idx}: Шахта не указана")
                    transaction.savepoint_rollback(savepoint_id)
                    continue

                number_mine = NumberMine.objects.filter(title__icontains=number_mine_str).first()
                if not number_mine:
                    error_count += 1
                    errors_list.append(f"Строка {row_idx}: Шахта '{number_mine_str}' не найдена")
                    transaction.savepoint_rollback(savepoint_id)
                    continue

                # Протяженность (обязательное)
                distance_value = row[header_map['distance']]
                if distance_value is None:
                    error_count += 1
                    errors_list.append(f"Строка {row_idx}: Протяженность не указана")
                    transaction.savepoint_rollback(savepoint_id)
                    continue

                try:
                    distance = int(float(str(distance_value).strip() or 0))
                    if distance < 0:
                        raise ValueError("Протяженность не может быть отрицательной")
                except (ValueError, TypeError):
                    error_count += 1
                    errors_list.append(f"Строка {row_idx}: Неверное значение протяженности: {distance_value}")
                    transaction.savepoint_rollback(savepoint_id)
                    continue

                # Единица измерения (обязательное)
                unit_str = str(row[header_map['unit']]).strip() if row[header_map['unit']] else None
                if not unit_str:
                    error_count += 1
                    errors_list.append(f"Строка {row_idx}: Единица измерения не указана")
                    transaction.savepoint_rollback(savepoint_id)
                    continue

                unit = Unit.objects.filter(title__icontains=unit_str).first()
                if not unit:
                    error_count += 1
                    errors_list.append(
                        f"Строка {row_idx}: Единица измерения '{unit_str}' не найдена. Доступные: {', '.join([u.title for u in Unit.objects.all()])}")
                    transaction.savepoint_rollback(savepoint_id)
                    continue

                # Уклонный блок (опционально)
                inclined_blocks = None
                if 'inclined_blocks' in header_map and row[header_map['inclined_blocks']]:
                    inclined_blocks_str = str(row[header_map['inclined_blocks']]).strip()
                    if inclined_blocks_str:
                        inclined_blocks = InclinedBlocks.objects.filter(
                            title__icontains=inclined_blocks_str,
                            number_mine=number_mine
                        ).first()
                        if not inclined_blocks:
                            logger.warning(f"Строка {row_idx}: Уклонный блок '{inclined_blocks_str}' не найден")

                # От оборудования (опционально)
                track_from = None
                if 'track_from' in header_map and row[header_map['track_from']]:
                    track_from_str = str(row[header_map['track_from']]).strip()
                    if track_from_str:
                        track_from = EquipmentInstallation.objects.filter(name__icontains=track_from_str).first()
                        if not track_from:
                            logger.warning(f"Строка {row_idx}: Оборудование 'от' '{track_from_str}' не найдено")

                # До оборудования (опционально)
                track_to = None
                if 'track_to' in header_map and row[header_map['track_to']]:
                    track_to_str = str(row[header_map['track_to']]).strip()
                    if track_to_str:
                        track_to = EquipmentInstallation.objects.filter(name__icontains=track_to_str).first()
                        if not track_to:
                            logger.warning(f"Строка {row_idx}: Оборудование 'до' '{track_to_str}' не найдено")

                # Создаем или обновляем запись кабельного журнала
                # Поле name будет автоматически сгенерировано в save() из track_from и track_to
                cable_magazine, created = CableMagazine.objects.update_or_create(
                    cable=cable,
                    subsystem=subsystem,
                    number_mine=number_mine,
                    track_from=track_from,
                    track_to=track_to,
                    defaults={
                        'inclined_blocks': inclined_blocks,
                        'distance': distance,
                        'unit': unit,
                    }
                )

                success_count += 1
                logger.info(f"{'Создана' if created else 'Обновлена'} запись кабельного журнала: {cable_magazine}")

                if savepoint_id is not None:
                    transaction.savepoint_commit(savepoint_id)

            except Exception as e:
                error_count += 1
                error_msg = f"Строка {row_idx}: {str(e)}"
                errors_list.append(error_msg)
                logger.error(error_msg, exc_info=True)
                if savepoint_id is not None:
                    try:
                        transaction.savepoint_rollback(savepoint_id)
                    except Exception:
                        pass

        logger.info(f"Импорт завершен. Обработано: {rows_processed}, успешно: {success_count}, ошибок: {error_count}")
        if rows_processed == 0 and success_count == 0 and error_count == 0:
            return 0, 0, ["Не удалось обработать данные"]

        return success_count, error_count, errors_list

    except Exception as e:
        error_msg = f"Ошибка при чтении Excel файла: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return 0, 0, [error_msg]


def import_execution_from_excel(excel_file):
    """
    Импорт отчетов выполнения работ из Excel файла

    Ожидаемые колонки в Excel (первая строка - заголовки):
    - Оборудование (equipment_install) - обозначение оборудования в проекте (поле name из EquipmentInstallation) - опционально
      Примеры значений: "ОБ-1", "ТТ-5", "РК-3" (значение должно существовать в таблице EquipmentInstallation)
    - Шахта (number_mine) - название шахты для уточнения поиска оборудования - опционально, но рекомендуется
      Примеры значений: "Нефтешахта №1", "Нефтешахта №2", "Нефтешахта №3"
    - Тип оборудования (equipment_title) - тип оборудования для уточнения поиска - опционально, но рекомендуется
      Примеры значений: "Оборудование А", "Оборудование Б" (значение должно существовать в таблице Equipment)
      ВАЖНО: Если в таблице EquipmentInstallation есть одинаковые значения "name" для разных шахт или типов оборудования, 
             обязательно укажите колонки "Шахта" и/или "Тип оборудования" для точного поиска
    - Кабель (cable_magazine) - трасса кабеля в формате "от/до" (поле name из CableMagazine) - опционально
      Примеры значений: "ОБ-1/ОБ-2", "РК-3/ТТ-5" (значение должно существовать в таблице CableMagazine)
    - Установка выполнена (execution_bool) - "Да"/"Нет" или True/False - опционально, по умолчанию False
    - Дата начала (date_start) - в формате ДД.ММ.ГГГГ или ДД/ММ/ГГГГ - опционально
    - Дата завершения (date_end) - в формате ДД.ММ.ГГГГ или ДД/ММ/ГГГГ - опционально
    - Описание (description) - опционально

    Примечание: 
    - Должно быть указано либо equipment_install, либо cable_magazine (хотя бы одно)
    - Для equipment_install указывайте значение поля "name" (Обозначение в проекте) из таблицы EquipmentInstallation
    - Если есть несколько записей с одинаковым "name" для разных шахт или типов оборудования, 
      обязательно укажите колонки "Шахта" и/или "Тип оборудования" для точного поиска
    - Для cable_magazine указывайте значение поля "name" (Трасса от - до) из таблицы CableMagazine в формате "от/до"

    Args:
        excel_file: Загруженный Excel файл

    Returns:
        tuple: (success_count, error_count, errors_list)
    """
    success_count = 0
    error_count = 0
    errors_list = []

    try:
        # Загружаем Excel файл
        logger.info(f"Начало импорта файла: {excel_file.name}")
        workbook = load_workbook(excel_file, data_only=True)
        sheet = workbook.active
        logger.info(f"Активный лист: {sheet.title}, размер: {sheet.max_row} строк, {sheet.max_column} колонок")

        # Определяем индексы колонок по первой строке (заголовкам)
        headers_row = list(sheet.iter_rows(min_row=1, max_row=1, values_only=True))[0]
        headers = [str(h).strip() if h is not None else None for h in headers_row]
        logger.info(f"Заголовки найдены: {headers}")

        # Пропускаем первую строку (заголовки)
        rows = list(sheet.iter_rows(min_row=2, values_only=True))
        logger.info(f"Найдено строк данных: {len(rows)}")

        if not rows:
            return 0, 0, ["Файл пуст или не содержит данных (нет строк после заголовков)"]

        # Маппинг возможных названий колонок
        column_mapping = {
            'equipment_install': ['оборудование', 'equipment_install', 'место установки', 'обозначение оборудования', 'обозначение в проекте'],
            # Добавлено для уточнения поиска
            'number_mine': ['шахта', 'number_mine', 'нефтешахта', 'numbermine', 'mine'],
            # Для поиска по типу оборудования
            'equipment_title': ['тип оборудования', 'equipment_title', 'equipment', 'тип', 'название оборудования'],
            'cable_magazine': ['кабель', 'cable_magazine', 'трасса кабеля', 'кабельный журнал'],
            'execution_bool': ['установка выполнена', 'execution_bool', 'выполнено', 'установка', 'execution'],
            'date_start': ['дата начала', 'date_start', 'дата старта', 'начало'],
            'date_end': ['дата завершения', 'date_end', 'дата окончания', 'завершение', 'окончание'],
            'description': ['описание', 'description', 'комментарий', 'примечание'],
        }

        # Находим индексы колонок
        header_map = find_column_mapping(headers, column_mapping)
        logger.info(f"Найдено колонок: {len(header_map)}, маппинг: {header_map}")

        # Импортируем данные
        rows_processed = 0
        rows_skipped_empty = 0

        for row_idx, row in enumerate(rows, start=2):
            savepoint_id = None
            try:
                # Пропускаем пустые строки
                if not any(row):
                    rows_skipped_empty += 1
                    continue

                rows_processed += 1
                savepoint_id = transaction.savepoint()

                # Оборудование (опционально)
                # Поиск по полю "name" (Обозначение в проекте) из EquipmentInstallation
                # Если указана шахта и/или тип оборудования, используем их для уточнения поиска
                equipment_install = None
                if 'equipment_install' in header_map and row[header_map['equipment_install']]:
                    equipment_name = str(row[header_map['equipment_install']]).strip()
                    if equipment_name:
                        # Получаем дополнительные фильтры для уточнения поиска
                        number_mine = None
                        equipment_title = None

                        if 'number_mine' in header_map and row[header_map['number_mine']]:
                            number_mine_str = str(row[header_map['number_mine']]).strip()
                            if number_mine_str:
                                number_mine = NumberMine.objects.filter(title__icontains=number_mine_str).first()

                        if 'equipment_title' in header_map and row[header_map['equipment_title']]:
                            equipment_title_str = str(row[header_map['equipment_title']]).strip()
                            if equipment_title_str:
                                equipment_title = Equipment.objects.filter(
                                    title__icontains=equipment_title_str).first()
                                if not equipment_title:
                                    logger.warning(
                                        f"Строка {row_idx}: Тип оборудования '{equipment_title_str}' не найден. "
                                        f"Поиск будет выполнен без учета типа оборудования."
                                    )

                        # Формируем фильтры для поиска
                        filters = {'name__icontains': equipment_name}
                        if number_mine:
                            filters['number_mine'] = number_mine
                        if equipment_title:
                            filters['title'] = equipment_title

                        # Ищем с учетом всех указанных фильтров
                        equipment_install = EquipmentInstallation.objects.filter(**filters).first()

                        # Если не найдено с полными фильтрами, пробуем с меньшим количеством фильтров
                        if not equipment_install:
                            # Пробуем без типа оборудования
                            if equipment_title:
                                filters_without_title = {k: v for k, v in filters.items() if k != 'title'}
                                equipment_install = EquipmentInstallation.objects.filter(
                                    **filters_without_title).first()
                                if equipment_install:
                                    logger.warning(
                                        f"Строка {row_idx}: Найдено оборудование '{equipment_name}' без учета типа '{equipment_title_str}'. "
                                        f"Найдена запись с типом '{equipment_install.title.title if equipment_install.title else 'не указан'}'"
                                    )

                            # Пробуем без шахты
                            if not equipment_install and number_mine:
                                filters_without_mine = {k: v for k, v in filters.items() if k != 'number_mine'}
                                equipment_install = EquipmentInstallation.objects.filter(
                                    **filters_without_mine).first()
                                if equipment_install:
                                    logger.warning(
                                        f"Строка {row_idx}: Найдено оборудование '{equipment_name}' без учета шахты. "
                                        f"Найдена запись для шахты '{equipment_install.number_mine.title if equipment_install.number_mine else 'не указана'}'"
                                    )

                            # Пробуем только по имени
                            if not equipment_install:
                                equipment_install = EquipmentInstallation.objects.filter(
                                    name__icontains=equipment_name).first()

                                # Если найдено несколько записей, предупреждаем
                                count = EquipmentInstallation.objects.filter(name__icontains=equipment_name).count()
                                if count > 1:
                                    logger.warning(
                                        f"Строка {row_idx}: Найдено {count} записей оборудования с именем '{equipment_name}'. "
                                        f"Используется первая найденная. Рекомендуется указать колонки 'Шахта' и/или 'Тип оборудования' для точного поиска."
                                    )

                        if not equipment_install:
                            error_count += 1
                            error_msg_parts = [f"Строка {row_idx}: Оборудование '{equipment_name}'"]
                            if number_mine:
                                error_msg_parts.append(f"для шахты '{number_mine.title}'")
                            if equipment_title:
                                error_msg_parts.append(f"типа '{equipment_title.title}'")
                            error_msg_parts.append("не найдено.")
                            error_msg = " ".join(error_msg_parts)
                            error_msg += " Укажите правильные значения полей 'Обозначение в проекте' (name), 'Шахта' (number_mine) и/или 'Тип оборудования' (title) из таблицы EquipmentInstallation."
                            errors_list.append(error_msg)
                            transaction.savepoint_rollback(savepoint_id)
                            continue

                # Кабель (опционально)
                # Поиск по полю "name" (Трасса от - до) из CableMagazine в формате "от/до"
                cable_magazine = None
                if 'cable_magazine' in header_map and row[header_map['cable_magazine']]:
                    cable_name = str(row[header_map['cable_magazine']]).strip()
                    if cable_name:
                        # Ищем по полю name (трасса от - до, формат "от/до", например "ОБ-1/ОБ-2")
                        cable_magazine = CableMagazine.objects.filter(name__icontains=cable_name).first()
                        if not cable_magazine:
                            error_count += 1
                            errors_list.append(
                                f"Строка {row_idx}: Трасса кабеля '{cable_name}' не найдена. "
                                f"Укажите значение поля 'Трасса от - до' (name) из таблицы CableMagazine в формате 'от/до' (например: ОБ-1/ОБ-2)."
                            )
                            transaction.savepoint_rollback(savepoint_id)
                            continue

                # Проверяем, что указано хотя бы одно из полей
                if not equipment_install and not cable_magazine:
                    error_count += 1
                    errors_list.append(f"Строка {row_idx}: Должно быть указано либо оборудование, либо трасса кабеля")
                    transaction.savepoint_rollback(savepoint_id)
                    continue

                # Установка выполнена (опционально)
                execution_bool = False
                if 'execution_bool' in header_map and row[header_map['execution_bool']]:
                    exec_value = str(row[header_map['execution_bool']]).strip().lower()
                    execution_bool = exec_value in ['да', 'yes', 'true', '1', 'выполнено']

                # Дата начала (опционально)
                date_start = None
                if 'date_start' in header_map and row[header_map['date_start']]:
                    date_start = parse_date(row[header_map['date_start']])

                # Дата завершения (опционально)
                date_end = None
                if 'date_end' in header_map and row[header_map['date_end']]:
                    date_end = parse_date(row[header_map['date_end']])

                # Описание (опционально)
                description = None
                if 'description' in header_map and row[header_map['description']]:
                    description = str(row[header_map['description']]).strip()

                # Создаем или обновляем запись
                Execution.objects.update_or_create(
                    equipment_install=equipment_install,
                    cable_magazine=cable_magazine,
                    defaults={
                        'execution_bool': execution_bool,
                        'date_start': date_start,
                        'date_end': date_end,
                        'description': description,
                    }
                )

                success_count += 1
                logger.info(
                    f"Создан/обновлен отчет выполнения: equipment_install={equipment_install}, cable_magazine={cable_magazine}")

                if savepoint_id is not None:
                    transaction.savepoint_commit(savepoint_id)

            except Exception as e:
                error_count += 1
                error_msg = f"Строка {row_idx}: {str(e)}"
                errors_list.append(error_msg)
                logger.error(error_msg, exc_info=True)

                if savepoint_id is not None:
                    try:
                        transaction.savepoint_rollback(savepoint_id)
                    except Exception:
                        pass

        logger.info(
            f"Импорт завершен. Обработано строк: {rows_processed}, пропущено пустых: {rows_skipped_empty}, успешно: {success_count}, ошибок: {error_count}")

        if rows_processed == 0 and success_count == 0 and error_count == 0:
            return 0, 0, ["Не удалось обработать данные. Возможно, все строки пустые или не содержат обязательных полей."]

        return success_count, error_count, errors_list

    except Exception as e:
        error_msg = f"Ошибка при чтении Excel файла: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return 0, 0, [error_msg]


def import_violations_from_excel(excel_file):
    """
    Импорт нарушений из Excel файла

    Ожидаемые колонки в Excel (первая строка - заголовки):
    - Номер акта (number_act) - опционально
    - Дата проверки (date_act) - в формате ДД.ММ.ГГГГ или ДД/ММ/ГГГГ - опционально
    - Кем выдано (issued_by_act) - опционально
    - Шахта (number_mine) - название шахты, например "Нефтешахта №1" - обязательное
    - Описание нарушения (title) - опционально
    - Нарушение устранено (execution_bool) - "Да"/"Нет" или True/False - опционально, по умолчанию False

    Args:
        excel_file: Загруженный Excel файл

    Returns:
        tuple: (success_count, error_count, errors_list)
    """
    success_count = 0
    error_count = 0
    errors_list = []

    try:
        # Загружаем Excel файл
        logger.info(f"Начало импорта файла: {excel_file.name}")
        workbook = load_workbook(excel_file, data_only=True)
        sheet = workbook.active
        logger.info(f"Активный лист: {sheet.title}, размер: {sheet.max_row} строк, {sheet.max_column} колонок")

        # Определяем индексы колонок по первой строке (заголовкам)
        headers_row = list(sheet.iter_rows(min_row=1, max_row=1, values_only=True))[0]
        headers = [str(h).strip() if h is not None else None for h in headers_row]
        logger.info(f"Заголовки найдены: {headers}")

        # Пропускаем первую строку (заголовки)
        rows = list(sheet.iter_rows(min_row=2, values_only=True))
        logger.info(f"Найдено строк данных: {len(rows)}")

        if not rows:
            return 0, 0, ["Файл пуст или не содержит данных (нет строк после заголовков)"]

        # Маппинг возможных названий колонок
        column_mapping = {
            'number_act': ['номер акта', 'number_act', 'акт', 'номер'],
            'date_act': ['дата проверки', 'date_act', 'дата акта', 'дата'],
            'issued_by_act': ['кем выдано', 'issued_by_act', 'выдано', 'кем выдан'],
            'number_mine': ['шахта', 'number_mine', 'нефтешахта', 'numbermine', 'mine'],
            'title': ['описание нарушения', 'title', 'описание', 'нарушение', 'текст'],
            'execution_bool': ['нарушение устранено', 'execution_bool', 'устранено', 'исправлено'],
        }

        # Находим индексы колонок
        header_map = find_column_mapping(headers, column_mapping)
        logger.info(f"Найдено колонок: {len(header_map)}, маппинг: {header_map}")

        # Проверяем обязательные поля
        required_fields = ['number_mine']
        missing_fields = [field for field in required_fields if field not in header_map]
        if missing_fields:
            error_msg = f"Отсутствуют обязательные колонки: {', '.join(missing_fields)}. Найденные заголовки: {[h for h in headers if h]}"
            logger.error(error_msg)
            return 0, 0, [error_msg]

        # Импортируем данные
        rows_processed = 0
        rows_skipped_empty = 0

        for row_idx, row in enumerate(rows, start=2):
            savepoint_id = None
            try:
                # Пропускаем пустые строки
                if not any(row):
                    rows_skipped_empty += 1
                    continue

                rows_processed += 1
                savepoint_id = transaction.savepoint()

                # Шахта (обязательное)
                number_mine_str = str(row[header_map['number_mine']]).strip(
                ) if row[header_map['number_mine']] else None
                if not number_mine_str:
                    error_count += 1
                    errors_list.append(f"Строка {row_idx}: Поле 'Шахта' не может быть пустым")
                    transaction.savepoint_rollback(savepoint_id)
                    continue

                number_mine = NumberMine.objects.filter(title__icontains=number_mine_str).first()
                if not number_mine:
                    error_count += 1
                    errors_list.append(f"Строка {row_idx}: Шахта '{number_mine_str}' не найдена")
                    transaction.savepoint_rollback(savepoint_id)
                    continue

                # Номер акта (опционально)
                number_act = None
                if 'number_act' in header_map and row[header_map['number_act']]:
                    number_act = truncate_field(row[header_map['number_act']], 100)

                # Дата проверки (опционально)
                date_act = None
                if 'date_act' in header_map and row[header_map['date_act']]:
                    date_act = parse_date(row[header_map['date_act']])

                # Кем выдано (опционально)
                issued_by_act = None
                if 'issued_by_act' in header_map and row[header_map['issued_by_act']]:
                    issued_by_act = truncate_field(row[header_map['issued_by_act']], 100)

                # Описание нарушения (опционально)
                title = None
                if 'title' in header_map and row[header_map['title']]:
                    title = str(row[header_map['title']]).strip()

                # Нарушение устранено (опционально)
                execution_bool = False
                if 'execution_bool' in header_map and row[header_map['execution_bool']]:
                    exec_value = str(row[header_map['execution_bool']]).strip().lower()
                    execution_bool = exec_value in ['да', 'yes', 'true', '1', 'устранено', 'исправлено']

                # Создаем или обновляем нарушение
                # Используем number_act и date_act как уникальные идентификаторы, если они указаны
                if number_act and date_act:
                    violation, created = Violations.objects.update_or_create(
                        number_act=number_act,
                        date_act=date_act,
                        defaults={
                            'issued_by_act': issued_by_act,
                            'number_mine': number_mine,
                            'title': title,
                            'execution_bool': execution_bool,
                        }
                    )
                else:
                    # Если нет уникальных полей, просто создаем новую запись
                    violation = Violations.objects.create(
                        number_act=number_act,
                        date_act=date_act,
                        issued_by_act=issued_by_act,
                        number_mine=number_mine,
                        title=title,
                        execution_bool=execution_bool,
                    )
                    created = True

                success_count += 1
                logger.info(f"{'Создано' if created else 'Обновлено'} нарушение: {violation}")

                if savepoint_id is not None:
                    transaction.savepoint_commit(savepoint_id)

            except Exception as e:
                error_count += 1
                error_msg = f"Строка {row_idx}: {str(e)}"
                errors_list.append(error_msg)
                logger.error(error_msg, exc_info=True)

                if savepoint_id is not None:
                    try:
                        transaction.savepoint_rollback(savepoint_id)
                    except Exception:
                        pass

        logger.info(
            f"Импорт завершен. Обработано строк: {rows_processed}, пропущено пустых: {rows_skipped_empty}, успешно: {success_count}, ошибок: {error_count}")

        if rows_processed == 0 and success_count == 0 and error_count == 0:
            return 0, 0, ["Не удалось обработать данные. Возможно, все строки пустые или не содержат обязательных полей."]

        return success_count, error_count, errors_list

    except Exception as e:
        error_msg = f"Ошибка при чтении Excel файла: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return 0, 0, [error_msg]
