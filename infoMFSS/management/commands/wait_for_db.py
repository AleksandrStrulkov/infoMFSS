import time
from django.core.management.base import BaseCommand
from django.db import connections
from django.db.utils import OperationalError


class Command(BaseCommand):
    help = 'Ожидает доступности базы данных'

    def handle(self, *args, **options):
        self.stdout.write('Ожидание базы данных...')
        max_retries = 20
        retry_delay = 5  # seconds

        for i in range(max_retries):
            try:
                connections['default'].ensure_connection()
                self.stdout.write(self.style.SUCCESS('База данных доступна!'))
                return
            except OperationalError:
                self.stdout.write(f'Попытка {i+1}/{max_retries}: База данных недоступна, ожидание...')
                time.sleep(retry_delay)

        self.stdout.write(self.style.ERROR('Не удалось подключиться к базе данных'))
        raise OperationalError('Сбой подключения к базе данных')
