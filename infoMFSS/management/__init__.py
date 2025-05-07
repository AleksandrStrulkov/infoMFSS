import sys
import time

from django.core.management.base import BaseCommand
from django.db import connections
from django.db.utils import OperationalError


class Command(BaseCommand):
    """Django команда для ожидания доступности базы данных"""

    def handle(self, *args, **options):
        self.stdout.write("Ожидание базы данных...")
        db_conn = None
        max_retries = 20
        retry_delay = 5  # секунд

        for i in range(max_retries):
            try:
                db_conn = connections["default"]
                db_conn.ensure_connection()
                self.stdout.write(self.style.SUCCESS("База данных доступна!"))
                return
            except OperationalError as e:
                self.stdout.write(
                    f"Попытка {i + 1}/{max_retries}: База данных недоступна, ожидает {retry_delay}секунд...Ошибка: {e}"
                )
                time.sleep(retry_delay)

        self.stdout.write(self.style.ERROR("Не удалось подключиться к базе данных"))
        sys.exit(1)
