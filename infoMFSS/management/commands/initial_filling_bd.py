from django.core.management.base import BaseCommand
from django.db import transaction
from infoMFSS.models import NumberMine, InclinedBlocks, Unit, Subsystem


class Command(BaseCommand):
    help = 'Заполняет базу данных начальными данными'

    def handle(self, *args, **options):
        try:
            with transaction.atomic():
                self.create_mines()
                self.create_blocks()
                self.create_units()
                self.create_subsystems()
            self.stdout.write(self.style.SUCCESS('Данные успешно добавлены!'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Ошибка: {e}'))

    # Создание начальных объектов в таблице 'NumberMine'
    def create_mines(self):
        mine_list = [
                {'title': 'Нефтешахта №1', 'address_mine': 'Республика Коми, г. Ухта пгт Ярега ул. Шахтинская д.9',
                 'slug': 'nefteshahta-1'},
                {'title': 'Нефтешахта №2', 'address_mine': 'Республика Коми, г. Ухта п. Первомайский',
                 'slug': 'nefteshahta-2'},
                {'title': 'Нефтешахта №3', 'address_mine': 'Республика Коми, г. Ухта п. Доманик',
                 'slug': 'nefteshahta-3'},
                {'title': 'Все шахты', 'address_mine': None, 'slug': 'vse-shahty'},
        ]

        # Создаём только несуществующие шахты
        existing_titles = set(NumberMine.objects.values_list('title', flat=True))
        mines_to_create = [
                NumberMine(**item)
                for item in mine_list
                if item['title'] not in existing_titles
        ]

        if mines_to_create:
            NumberMine.objects.bulk_create(mines_to_create)
            self.stdout.write(f'Создано {len(mines_to_create)} нефтешахт')

    # Создание начальных объектов в таблице 'InclinedBlocks'
    def create_blocks(self):
        # Предварительно получаем все шахты одним запросом
        mines = {mine.title: mine for mine in NumberMine.objects.all()}

        blocks_list = [
                {'title': '3Т-9', 'number_mine': mines.get('Нефтешахта №1'), 'description': '', 'slug': None},
                {'title': '1Т-4', 'number_mine': mines.get('Нефтешахта №1'), 'description': '', 'slug': None},
                {'title': '4Т-4', 'number_mine': mines.get('Нефтешахта №1'), 'description': '', 'slug': None},
                {'title': '1-3Д "Юг"', 'number_mine': mines.get('Нефтешахта №1'), 'description': '', 'slug': None},
                {'title': '1-3Д "Север"', 'number_mine': mines.get('Нефтешахта №1'), 'description': '', 'slug': None},
                {'title': '2-3Д', 'number_mine': mines.get('Нефтешахта №2'), 'description': '', 'slug': None},
                {'title': '2-1Д', 'number_mine': mines.get('Нефтешахта №2'), 'description': '', 'slug': None},
                {'title': '2Т-1', 'number_mine': mines.get('Нефтешахта №3'), 'description': '', 'slug': None},
                {'title': '3Т-4', 'number_mine': mines.get('Нефтешахта №3'), 'description': '', 'slug': None},
                {'title': '2Т-4', 'number_mine': mines.get('Нефтешахта №3'), 'description': '', 'slug': None},
                {'title': '1Т-1', 'number_mine': mines.get('Нефтешахта №3'), 'description': '', 'slug': None},
                {'title': 'Все уклонные блоки', 'number_mine': None, 'description': '', 'slug': None},
        ]

        # Создаём только несуществующие объекты
        existing_blocks = set(InclinedBlocks.objects.values_list('title', flat=True))
        blocks_to_create = [
                InclinedBlocks(**item)
                for item in blocks_list
                if item['title'] not in existing_blocks
        ]

        if blocks_to_create:
            InclinedBlocks.objects.bulk_create(blocks_to_create)
            self.stdout.write(f'Создано {len(blocks_to_create)} уклонных блоков')

    # Создание начальных объектов в таблице 'Unit'
    def create_units(self):
        units_list = [
                {'title': 'м.', 'description': 'метр',},
                {'title': 'км.', 'description': 'километр',},
                {'title': 'шт.', 'description': 'штук',},
        ]
        # Создаём только несуществующие объекты
        existing_units = set(Unit.objects.values_list('title', flat=True))
        units_to_create = [
                Unit(**item)
                for item in units_list
                if item['title'] not in existing_units
        ]

        if units_to_create:
            Unit.objects.bulk_create(units_to_create)
            self.stdout.write(f'Создано {len(units_to_create)} единиц измерения')

    # Создание начальных объектов в таблице 'Subsystem'
    def create_subsystems(self):
        subsystems_list = [
                {'title': 'АТС', 'description': 'Подсистема шахтной связи', 'slug': 'ats'},
                {'title': 'ППИТ', 'description': 'Подсистема позиционирования и передачи данных', 'slug': 'ppit'},
                {'title': 'АГК', 'description': 'Подсистема аэрогазового контроля', 'slug': 'agk'},
                {'title': 'ВН', 'description': 'Подсистема видеонаблюдения', 'slug': 'vn'},
                {'title': 'ПЖ', 'description': 'Подсистема контроля и управления пожарным водоснабжением',
                 'slug': 'pz'},
                {'title': 'ВМП', 'description': 'Подсистема контроля и управления ВМП', 'slug': 'vmp'},
                {'title': 'АСКТП', 'description': 'Автоматизированная система контроля технологическими процессами',
                 'slug': 'asktp'},
                {'title': 'КРУ', 'description': 'Подсистема управления комплектными распределительными устройствами',
                 'slug': 'kur'},
                {'title': 'Все подсистемы', 'description': '', 'slug': 'allsubsystems'},
        ]
        # Создаём только несуществующие объекты
        existing_subsystems = set(Subsystem.objects.values_list('title', flat=True))
        subsystems_to_create = [
                Subsystem(**item)
                for item in subsystems_list
                if item['title'] not in existing_subsystems
        ]

        if subsystems_to_create:
            Subsystem.objects.bulk_create(subsystems_to_create)
            self.stdout.write(f'Создано {len(subsystems_to_create)} подсистем')

        # Создание начальных объектов в таблице 'Subsystem'


