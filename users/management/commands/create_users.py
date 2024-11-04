from django.core.management import BaseCommand

from users.models import User


class Command(BaseCommand):

    def handle(self, *args, **options):
        user = User.objects.create(
            email='astrulkov@ya.ru',
            first_name='Александр',
            last_name='Струльков',
            is_staff=True,
            is_superuser=True,
            is_active=True
        )

        user.set_password('gizn1247')
        user.save()