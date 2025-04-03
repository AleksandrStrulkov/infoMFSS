from django.core.management import BaseCommand
from users.models import User, AllowedPerson
import os
from dotenv import load_dotenv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / '.env')


class Command(BaseCommand):

    def handle(self, *args, **options):
        user = User.objects.create(
                # email='admin@infomfss.ru',
                email=os.getenv('ADMIN_EMAIL'),
                # first_name='Иван',
                first_name=os.getenv('ADMIN_FIRST_NAME'),
                # middle_name='Иванович',
                middle_name=os.getenv('ADMIN_MIDDLE_NAME'),
                # last_name='Иванов',
                last_name=os.getenv('ADMIN_LAST_NAME'),
                is_staff=True,
                is_superuser=True,
                is_active=True
        )
        user.set_password(os.getenv('ADMIN_PASSWORD'))
        allowed_person = AllowedPerson.objects.create(
                first_name=os.getenv('ADMIN_FIRST_NAME'),
                middle_name=os.getenv('ADMIN_MIDDLE_NAME'),
                last_name=os.getenv('ADMIN_LAST_NAME'),
        )
        user.save()
        allowed_person.save()