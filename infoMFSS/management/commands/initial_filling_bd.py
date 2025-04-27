from django.core.management.base import BaseCommand
from django.db import transaction
from infoMFSS.models import (
    NumberMine,
    InclinedBlocks,
    Unit,
    Subsystem,
    Tunnel,
    Cable,
    PointPhone,
    Equipment,
    EquipmentInstallation,
    BranchesBox,
    CableMagazine,
)

def all_data_from_models(model):
    datas = {data.title: data for data in model.objects.all()}
    return datas


def all_mines():
    mines = {mine.title: mine for mine in NumberMine.objects.all()}
    return mines


def all_subsystems():
    subsystems = {subsystem.title: subsystem for subsystem in Subsystem.objects.all()}
    return subsystems


def all_blocks():
    inclined_blocks = {inclined_block.title: inclined_block for inclined_block in InclinedBlocks.objects.all()}
    return inclined_blocks


def all_tunnels():
    tunnels = {tunnel.title: tunnel for tunnel in Tunnel.objects.all()}
    return tunnels


def all_equipments():
    equipments = {equipment.title: equipment for equipment in EquipmentInstallation.objects.all()}
    return equipments


def all_cables():
    cables = {cable.title: cable for cable in Cable.objects.all()}
    return cables


def all_boxs():
    boxs = {box.title: box for box in BranchesBox.objects.all()}
    return boxs


def all_points_phones():
    phones = {phone.title: phone for phone in PointPhone.objects.all()}
    return phones


def all_branches_box():
    branches_box = {box.title: box for box in BranchesBox.objects.all()}
    return branches_box


def all_units():
    units = {unit.title: unit for unit in Unit.objects.all()}
    return units


def all_cable_magazine():
    cable_magazine = {magazine.title: magazine for magazine in CableMagazine.objects.all()}
    return cable_magazine


class Command(BaseCommand):
    help = "Заполняет базу данных начальными данными"

    def handle(self, *args, **options):
        try:
            with transaction.atomic():
                self.create_mines()
                self.create_blocks()
                self.create_units()
                self.create_subsystems()
                self.create_tunnels()
                self.create_equipments()
                self.create_cables()
                self.create_points_phone()
                self.create_branches_box()
                self.create_cable_magazine()
            self.stdout.write(self.style.SUCCESS("Данные успешно добавлены!"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Ошибка: {e}"))

    # Создание начальных объектов в таблице 'NumberMine'
    def create_mines(self):
        mine_list = [
            {
                "title": "Нефтешахта №1",
                "address_mine": "Республика Коми, г. Ухта пгт Ярега ул. Шахтинская д.9",
                "slug": "nefteshahta-1",
            },
            {
                "title": "Нефтешахта №2",
                "address_mine": "Республика Коми, г. Ухта п. Первомайский",
                "slug": "nefteshahta-2",
            },
            {"title": "Нефтешахта №3", "address_mine": "Республика Коми, г. Ухта п. Доманик", "slug": "nefteshahta-3"},
            {"title": "Все шахты", "address_mine": None, "slug": "vse-shahty"},
        ]

        # Создаём только несуществующие шахты
        existing_titles = set(NumberMine.objects.values_list("title", flat=True))
        mines_to_create = [NumberMine(**item) for item in mine_list if item["title"] not in existing_titles]

        if mines_to_create:
            NumberMine.objects.bulk_create(mines_to_create)
        self.stdout.write(f"Создано {len(mines_to_create)} нефтешахт")

    # Создание начальных объектов в таблице 'InclinedBlocks'
    def create_blocks(self):

        blocks_list = [
            {"title": "3Т-9", "number_mine": all_mines().get("Нефтешахта №1"), "description": "", "slug": None},
            {"title": "1Т-4", "number_mine": all_mines().get("Нефтешахта №1"), "description": "", "slug": None},
            {"title": "4Т-4", "number_mine": all_mines().get("Нефтешахта №1"), "description": "", "slug": None},
            {"title": '1-3Д "Юг"', "number_mine": all_mines().get("Нефтешахта №1"), "description": "", "slug": None},
            {
                "title": '1-3Д "Север"',
                "number_mine": all_mines().get("Нефтешахта №1"),
                "description": "",
                "slug": None,
            },
            {"title": "2-3Д", "number_mine": all_mines().get("Нефтешахта №2"), "description": "", "slug": None},
            {"title": "2-1Д", "number_mine": all_mines().get("Нефтешахта №2"), "description": "", "slug": None},
            {"title": "2Т-1", "number_mine": all_mines().get("Нефтешахта №3"), "description": "", "slug": None},
            {"title": "3Т-4", "number_mine": all_mines().get("Нефтешахта №3"), "description": "", "slug": None},
            {"title": "2Т-4", "number_mine": all_mines().get("Нефтешахта №3"), "description": "", "slug": None},
            {"title": "1Т-1", "number_mine": all_mines().get("Нефтешахта №3"), "description": "", "slug": None},
            {"title": "Все уклонные блоки", "number_mine": None, "description": "", "slug": None},
        ]

        # Создаём только несуществующие объекты
        existing_blocks = set(InclinedBlocks.objects.values_list("title", flat=True))
        blocks_to_create = [InclinedBlocks(**item) for item in blocks_list if item["title"] not in existing_blocks]

        if blocks_to_create:
            InclinedBlocks.objects.bulk_create(blocks_to_create)
        self.stdout.write(f"Создано {len(blocks_to_create)} уклонных блоков")

    # Создание начальных объектов в таблице 'Unit'
    def create_units(self):
        units_list = [
            {
                "title": "м.",
                "description": "метр",
            },
            {
                "title": "км.",
                "description": "километр",
            },
            {
                "title": "шт.",
                "description": "штук",
            },
        ]
        # Создаём только несуществующие объекты
        existing_units = set(Unit.objects.values_list("title", flat=True))
        units_to_create = [Unit(**item) for item in units_list if item["title"] not in existing_units]

        if units_to_create:
            Unit.objects.bulk_create(units_to_create)
        self.stdout.write(f"Создано {len(units_to_create)} единиц измерения")

    # Создание начальных объектов в таблице 'Subsystem'
    def create_subsystems(self):

        subsystems_list = [
            {"title": "АТС", "description": "Подсистема шахтной связи", "slug": "ats"},
            {"title": "ППИТ", "description": "Подсистема позиционирования и передачи данных", "slug": "ppit"},
            {"title": "АГК", "description": "Подсистема аэрогазового контроля", "slug": "agk"},
            {"title": "ВН", "description": "Подсистема видеонаблюдения", "slug": "vn"},
            {"title": "ПЖ", "description": "Подсистема контроля и управления пожарным водоснабжением", "slug": "pz"},
            {"title": "ВМП", "description": "Подсистема контроля и управления ВМП", "slug": "vmp"},
            {
                "title": "АСКТП",
                "description": "Автоматизированная система контроля технологическими процессами",
                "slug": "asktp",
            },
            {
                "title": "КРУ",
                "description": "Подсистема управления комплектными распределительными устройствами",
                "slug": "kur",
            },
            {"title": "Все подсистемы", "description": "", "slug": "allsubsystems"},
            {"title": "Различные", "description": "АГК, ВН, ПЖ, ВМП, АСКТП, КРУ", "slug": "subsystems"},
        ]
        # Создаём только несуществующие объекты
        existing_subsystems = set(Subsystem.objects.values_list("title", flat=True))
        subsystems_to_create = [
            Subsystem(**item) for item in subsystems_list if item["title"] not in existing_subsystems
        ]

        if subsystems_to_create:
            Subsystem.objects.bulk_create(subsystems_to_create)
        self.stdout.write(f"Создано {len(subsystems_to_create)} подсистем")

    # Создание начальных объектов в таблице 'Tunnel'
    def create_tunnels(self):

        tunnels_list = [
            {
                "title": "СОШ-1эт.",
                "number_mine": all_mines().get("Нефтешахта №1"),
                "inclined_blocks": None,
                "tuf_bool": True,
                "inclined_bool": False,
                "description": "",
                "name_slag": "",
            },
            {
                "title": "ЮОШ-1эт.",
                "number_mine": all_mines().get("Нефтешахта №1"),
                "inclined_blocks": None,
                "tuf_bool": True,
                "inclined_bool": False,
                "description": "",
                "name_slag": "",
            },
            {
                "title": "СКБ",
                "number_mine": all_mines().get("Нефтешахта №1"),
                "inclined_blocks": None,
                "tuf_bool": True,
                "inclined_bool": False,
                "description": "",
                "name_slag": "",
            },
            {
                "title": "ЮКБ-1",
                "number_mine": all_mines().get("Нефтешахта №1"),
                "inclined_blocks": None,
                "tuf_bool": True,
                "inclined_bool": False,
                "description": "",
                "name_slag": "",
            },
            {
                "title": "ЮКБ-2",
                "number_mine": all_mines().get("Нефтешахта №1"),
                "inclined_blocks": None,
                "tuf_bool": True,
                "inclined_bool": False,
                "description": "",
                "name_slag": "",
            },
            {
                "title": "СОШ-2эт.",
                "number_mine": all_mines().get("Нефтешахта №1"),
                "inclined_blocks": None,
                "tuf_bool": True,
                "inclined_bool": False,
                "description": "",
                "name_slag": "",
            },
            {
                "title": "СОШ-3эт.",
                "number_mine": all_mines().get("Нефтешахта №1"),
                "inclined_blocks": None,
                "tuf_bool": True,
                "inclined_bool": False,
                "description": "",
                "name_slag": "",
            },
            {
                "title": "ВПП ходка",
                "number_mine": all_mines().get("Нефтешахта №1"),
                "inclined_blocks": all_blocks().get("1Т-4"),
                "tuf_bool": False,
                "inclined_bool": True,
                "description": "",
                "name_slag": "",
            },
            {
                "title": "ВПП уклона",
                "number_mine": all_mines().get("Нефтешахта №1"),
                "inclined_blocks": all_blocks().get("1Т-4"),
                "tuf_bool": False,
                "inclined_bool": True,
                "description": "",
                "name_slag": "",
            },
            {
                "title": "Ходок",
                "number_mine": all_mines().get("Нефтешахта №1"),
                "inclined_blocks": all_blocks().get("1Т-4"),
                "tuf_bool": False,
                "inclined_bool": True,
                "description": "",
                "name_slag": "",
            },
            {
                "title": "Уклон",
                "number_mine": all_mines().get("Нефтешахта №1"),
                "inclined_blocks": all_blocks().get("1Т-4"),
                "tuf_bool": False,
                "inclined_bool": True,
                "description": "",
                "name_slag": "",
            },
            {
                "title": "НПП уклона",
                "number_mine": all_mines().get("Нефтешахта №1"),
                "inclined_blocks": all_blocks().get("1Т-4"),
                "tuf_bool": False,
                "inclined_bool": True,
                "description": "",
                "name_slag": "",
            },
            {
                "title": "НПП ходка",
                "number_mine": all_mines().get("Нефтешахта №1"),
                "inclined_blocks": all_blocks().get("1Т-4"),
                "tuf_bool": False,
                "inclined_bool": True,
                "description": "",
                "name_slag": "",
            },
            {
                "title": "Сбойка №5",
                "number_mine": all_mines().get("Нефтешахта №1"),
                "inclined_blocks": all_blocks().get("1Т-4"),
                "tuf_bool": False,
                "inclined_bool": True,
                "description": "",
                "name_slag": "",
            },
            {
                "title": "ЗКБ",
                "number_mine": all_mines().get("Нефтешахта №2"),
                "inclined_blocks": None,
                "tuf_bool": True,
                "inclined_bool": False,
                "description": "",
                "name_slag": "",
            },
            {
                "title": "СОШ-2эт.",
                "number_mine": all_mines().get("Нефтешахта №2"),
                "inclined_blocks": None,
                "tuf_bool": True,
                "inclined_bool": False,
                "description": "",
                "name_slag": "",
            },
            {
                "title": "КБ",
                "number_mine": all_mines().get("Нефтешахта №2"),
                "inclined_blocks": None,
                "tuf_bool": True,
                "inclined_bool": False,
                "description": "",
                "name_slag": "",
            },
            {
                "title": "ЮВВШ-1эт.",
                "number_mine": all_mines().get("Нефтешахта №2"),
                "inclined_blocks": None,
                "tuf_bool": True,
                "inclined_bool": False,
                "description": "",
                "name_slag": "",
            },
            {
                "title": "ЮВВШ-2эт.",
                "number_mine": all_mines().get("Нефтешахта №2"),
                "inclined_blocks": None,
                "tuf_bool": True,
                "inclined_bool": False,
                "description": "",
                "name_slag": "",
            },
            {
                "title": "ЮНВШ-1эт.",
                "number_mine": all_mines().get("Нефтешахта №2"),
                "inclined_blocks": None,
                "tuf_bool": True,
                "inclined_bool": False,
                "description": "",
                "name_slag": "",
            },
            {
                "title": "ЮОШ-1эт.",
                "number_mine": all_mines().get("Нефтешахта №2"),
                "inclined_blocks": None,
                "tuf_bool": True,
                "inclined_bool": False,
                "description": "",
                "name_slag": "",
            },
            {
                "title": "ВПП ходка",
                "number_mine": all_mines().get("Нефтешахта №2"),
                "inclined_blocks": all_blocks().get("2-1Д"),
                "tuf_bool": False,
                "inclined_bool": True,
                "description": "",
                "name_slag": "",
            },
            {
                "title": "ВПП уклона",
                "number_mine": all_mines().get("Нефтешахта №2"),
                "inclined_blocks": all_blocks().get("2-1Д"),
                "tuf_bool": False,
                "inclined_bool": True,
                "description": "",
                "name_slag": "",
            },
            {
                "title": "Ходок",
                "number_mine": all_mines().get("Нефтешахта №2"),
                "inclined_blocks": all_blocks().get("2-1Д"),
                "tuf_bool": False,
                "inclined_bool": True,
                "description": "",
                "name_slag": "",
            },
            {
                "title": "Уклон",
                "number_mine": all_mines().get("Нефтешахта №2"),
                "inclined_blocks": all_blocks().get("2-1Д"),
                "tuf_bool": False,
                "inclined_bool": True,
                "description": "",
                "name_slag": "",
            },
            {
                "title": "НПП ходка",
                "number_mine": all_mines().get("Нефтешахта №2"),
                "inclined_blocks": all_blocks().get("2-1Д"),
                "tuf_bool": False,
                "inclined_bool": True,
                "description": "",
                "name_slag": "",
            },
            {
                "title": "НПП уклона",
                "number_mine": all_mines().get("Нефтешахта №2"),
                "inclined_blocks": all_blocks().get("2-1Д"),
                "tuf_bool": False,
                "inclined_bool": True,
                "description": "",
                "name_slag": "",
            },
            {
                "title": "Насосная",
                "number_mine": all_mines().get("Нефтешахта №2"),
                "inclined_blocks": all_blocks().get("2-1Д"),
                "tuf_bool": False,
                "inclined_bool": True,
                "description": "",
                "name_slag": "",
            },
            {
                "title": "КБ",
                "number_mine": all_mines().get("Нефтешахта №3"),
                "inclined_blocks": None,
                "tuf_bool": True,
                "inclined_bool": False,
                "description": "",
                "name_slag": "",
            },
            {
                "title": "301 п.ш.",
                "number_mine": all_mines().get("Нефтешахта №3"),
                "inclined_blocks": None,
                "tuf_bool": True,
                "inclined_bool": False,
                "description": "",
                "name_slag": "",
            },
            {
                "title": "ВПрШ-0эт.",
                "number_mine": all_mines().get("Нефтешахта №3"),
                "inclined_blocks": None,
                "tuf_bool": True,
                "inclined_bool": False,
                "description": "",
                "name_slag": "",
            },
            {
                "title": "ЗПдШ-1эт.",
                "number_mine": all_mines().get("Нефтешахта №3"),
                "inclined_blocks": None,
                "tuf_bool": True,
                "inclined_bool": False,
                "description": "",
                "name_slag": "",
            },
            {
                "title": "ВОШ-1эт.",
                "number_mine": all_mines().get("Нефтешахта №3"),
                "inclined_blocks": None,
                "tuf_bool": True,
                "inclined_bool": False,
                "description": "",
                "name_slag": "",
            },
            {
                "title": "Порожняковая ветвь ПС",
                "number_mine": all_mines().get("Нефтешахта №3"),
                "inclined_blocks": None,
                "tuf_bool": True,
                "inclined_bool": False,
                "description": "",
                "name_slag": "",
            },
            {
                "title": "Вент.сбойка ВС №1",
                "number_mine": all_mines().get("Нефтешахта №3"),
                "inclined_blocks": None,
                "tuf_bool": True,
                "inclined_bool": False,
                "description": "",
                "name_slag": "",
            },
            {
                "title": "Ходок на ПС",
                "number_mine": all_mines().get("Нефтешахта №3"),
                "inclined_blocks": None,
                "tuf_bool": True,
                "inclined_bool": False,
                "description": "",
                "name_slag": "",
            },
            {
                "title": "101 п.ш.",
                "number_mine": all_mines().get("Нефтешахта №3"),
                "inclined_blocks": None,
                "tuf_bool": True,
                "inclined_bool": False,
                "description": "",
                "name_slag": "",
            },
            {
                "title": "ВПдШ-3эт.",
                "number_mine": all_mines().get("Нефтешахта №3"),
                "inclined_blocks": None,
                "tuf_bool": True,
                "inclined_bool": False,
                "description": "",
                "name_slag": "",
            },
            {
                "title": "217 п.ш.",
                "number_mine": all_mines().get("Нефтешахта №3"),
                "inclined_blocks": None,
                "tuf_bool": True,
                "inclined_bool": False,
                "description": "",
                "name_slag": "",
            },
            {
                "title": "ВПП ходка",
                "number_mine": all_mines().get("Нефтешахта №3"),
                "inclined_blocks": all_blocks().get("2Т-4"),
                "tuf_bool": False,
                "inclined_bool": True,
                "description": "",
                "name_slag": "",
            },
            {
                "title": "ВПП уклона",
                "number_mine": all_mines().get("Нефтешахта №3"),
                "inclined_blocks": all_blocks().get("2Т-4"),
                "tuf_bool": False,
                "inclined_bool": True,
                "description": "",
                "name_slag": "",
            },
            {
                "title": "Ходок",
                "number_mine": all_mines().get("Нефтешахта №3"),
                "inclined_blocks": all_blocks().get("2Т-4"),
                "tuf_bool": False,
                "inclined_bool": True,
                "description": "",
                "name_slag": "",
            },
            {
                "title": "Уклон",
                "number_mine": all_mines().get("Нефтешахта №3"),
                "inclined_blocks": all_blocks().get("2Т-4"),
                "tuf_bool": False,
                "inclined_bool": True,
                "description": "",
                "name_slag": "",
            },
            {
                "title": "НПП ходка",
                "number_mine": all_mines().get("Нефтешахта №3"),
                "inclined_blocks": all_blocks().get("2Т-4"),
                "tuf_bool": False,
                "inclined_bool": True,
                "description": "",
                "name_slag": "",
            },
            {
                "title": "НПП уклона",
                "number_mine": all_mines().get("Нефтешахта №3"),
                "inclined_blocks": all_blocks().get("2Т-4"),
                "tuf_bool": False,
                "inclined_bool": True,
                "description": "",
                "name_slag": "",
            },
            {
                "title": "Насосная",
                "number_mine": all_mines().get("Нефтешахта №3"),
                "inclined_blocks": all_blocks().get("2Т-4"),
                "tuf_bool": False,
                "inclined_bool": True,
                "description": "",
                "name_slag": "",
            },
        ]

        # Создаём только несуществующие объекты
        existing_tunnels = set(Tunnel.objects.values_list("title", flat=True))
        tunnels_to_create = [Tunnel(**item) for item in tunnels_list if item["title"] not in existing_tunnels]

        if tunnels_to_create:
            Tunnel.objects.bulk_create(tunnels_to_create)
        self.stdout.write(f"Создано {len(tunnels_to_create)} выработок")

    # Создание начальных объектов в таблице 'Equipment'
    def create_equipments(self):

        equipment_list = [
            {
                "title": "Телефон",
                "device_type": "Эльтон-Ex231",
                "description": "Телефонный аппарат рудничного исполнения, взрывозащищенный",
                "subsystem": all_subsystems().get("АТС"),
                "slug": None,
                "file_pdf": "",
                "file_passport": "",
                "file_certificate": "",
            },
            {
                "title": "Станция связи",
                "device_type": "Ethertex V4.11",
                "description": "Станция связи позиционирования",
                "subsystem": all_subsystems().get("ППИТ"),
                "slug": None,
                "file_pdf": "",
                "file_passport": "",
                "file_certificate": "",
            },
            {
                "title": "Станция связи",
                "device_type": "Ethertex V4",
                "description": "Станция связи магистральная МС12.18-34",
                "subsystem": all_subsystems().get("ВН"),
                "slug": None,
                "file_pdf": "",
                "file_passport": "",
                "file_certificate": "",
            },
            {
                "title": "Источник питания",
                "device_type": "МС 41.01",
                "description": "Источник питания для станции связи позиционирования",
                "subsystem": all_subsystems().get("ППИТ"),
                "slug": None,
                "file_pdf": "",
                "file_passport": "",
                "file_certificate": "",
            },
            {
                "title": "Источник питания",
                "device_type": "МС 41.02",
                "description": "Источник питания для станции связи магистральная",
                "subsystem": all_subsystems().get("Различные"),
                "slug": None,
                "file_pdf": "",
                "file_passport": "",
                "file_certificate": "",
            },
            {
                "title": "Видеокамера",
                "device_type": "УТЗШ-МР-32 (22)",
                "description": "Видеокамера",
                "subsystem": all_subsystems().get("ВН"),
                "slug": None,
                "file_pdf": "",
                "file_passport": "",
                "file_certificate": "",
            },
            {
                "title": "Прожектор ИК",
                "device_type": "СЗВ2",
                "description": "Прожектор инфракрасный взрывозащищенный",
                "subsystem": all_subsystems().get("ВН"),
                "slug": None,
                "file_pdf": "",
                "file_passport": "",
                "file_certificate": "",
            },
            {
                "title": "Датчик положения",
                "device_type": "ДПМГ-2-200",
                "description": "Датчик положения магнитогерконовый ДПМГ-2 исп. 200 с кронштейном К-ДПМ1 для монтажа",
                "subsystem": all_subsystems().get("АГК"),
                "slug": None,
                "file_pdf": "",
                "file_passport": "",
                "file_certificate": "",
            },
            {
                "title": "Датчик кислорода",
                "device_type": "СД-1.Т.О2",
                "description": "Датчик кислорода стационарный СД-1.Т.О2",
                "subsystem": all_subsystems().get("АГК"),
                "slug": None,
                "file_pdf": "",
                "file_passport": "",
                "file_certificate": "",
            },
        ]
        # Создаём только несуществующие объекты
        existing_equipments = set(Equipment.objects.values_list("title", flat=True))
        equipments_to_create = [
            Equipment(**item) for item in equipment_list if item["title"] not in existing_equipments
        ]

        if equipments_to_create:
            Equipment.objects.bulk_create(equipments_to_create)
        self.stdout.write(f"Создано {len(equipments_to_create)} шт. оборудования")

    # Создание начальных объектов в таблице 'Cable'
    def create_cables(self):
        # Предварительно получаем все шахты одним запросом
        cables_list = [
            {
                "title": "Все кабели",
                "device_type": None,
                "description": None,
                "file_pdf": None,
                "file_passport": None,
                "file_certificate": None,
            },
            {
                "title": "Многопарный (4 пары)",
                "device_type": "Parlan 4х2х0,57",
                "description": "Кабель предназначен для систем цифровой связи с параметрами передачи до 250 МГц",
                "file_pdf": None,
                "file_passport": None,
                "file_certificate": None,
            },
            {
                "title": "Многопарный (20 пар)",
                "device_type": "SКAРU 20х2х0,64",
                "description": "Кабель предназначен для систем цифровой связи с параметрами передачи до 250 МГц",
                "file_pdf": None,
                "file_passport": None,
                "file_certificate": None,
            },
            {
                "title": "Многопарный (50 пар)",
                "device_type": "SКAРU 50х2х0,64",
                "description": "Кабель предназначен для систем цифровой связи с параметрами передачи до 250 МГц",
                "file_pdf": None,
                "file_passport": None,
                "file_certificate": None,
            },
            {
                "title": "Многопарный (100 пар)",
                "device_type": "SКAРU 100х2х0,64",
                "description": "Кабель предназначен для систем цифровой связи с параметрами передачи до 250 МГц",
                "file_pdf": None,
                "file_passport": None,
                "file_certificate": None,
            },
            {
                "title": "Оптический",
                "device_type": "ОКЛСт-нг(А)-HF-01-16-10/125-2,7",
                "description": "Кабель предназначен для прокладки оптических линий связи.",
                "file_pdf": None,
                "file_passport": None,
                "file_certificate": None,
            },
        ]

        # Создаём только несуществующие объекты
        existing_cables = set(Cable.objects.values_list("title", flat=True))
        cables_to_create = [Cable(**item) for item in cables_list if item["title"] not in existing_cables]

        if cables_to_create:
            Cable.objects.bulk_create(cables_to_create)
        self.stdout.write(f"Создано {len(cables_to_create)} кабелей")

    # Создание начальных объектов в таблице 'PointPhone'
    def create_points_phone(self):

        points_list = [
            {
                "title": "Т#2-6",
                "number_mine": all_mines().get("Нефтешахта №1"),
                "tunnel": all_tunnels().get("СКБ"),
                "inclined_blocks": None,
                "subscriber_number": "8132",
                "picket": "34",
                "description": "",
                "slug": None,
                "serial_number": "",
                "device_type": "Эльтон-Ex231",
            },
            {
                "title": "Т#2-52",
                "number_mine": all_mines().get("Нефтешахта №1"),
                "tunnel": all_tunnels().get("ЮОШ-1эт."),
                "inclined_blocks": None,
                "subscriber_number": "8408",
                "picket": "55",
                "description": "",
                "slug": None,
                "serial_number": "",
                "device_type": "Эльтон-Ex231",
            },
            {
                "title": "Т#2-8",
                "number_mine": all_mines().get("Нефтешахта №1"),
                "tunnel": all_tunnels().get("СОШ-1эт."),
                "inclined_blocks": None,
                "subscriber_number": "8446",
                "picket": "55",
                "description": "",
                "slug": None,
                "serial_number": "",
                "device_type": "Эльтон-Ex231",
            },
            {
                "title": "Т#1-65",
                "number_mine": all_mines().get("Нефтешахта №2"),
                "tunnel": all_tunnels().get("ЗКБ"),
                "inclined_blocks": None,
                "subscriber_number": "5132",
                "picket": "48",
                "description": "",
                "slug": None,
                "serial_number": "",
                "device_type": "Эльтон-Ex231",
            },
            {
                "title": "Т#1-17",
                "number_mine": all_mines().get("Нефтешахта №2"),
                "tunnel": all_tunnels().get("СОШ-2эт."),
                "inclined_blocks": None,
                "subscriber_number": "5408",
                "picket": "4",
                "description": "",
                "slug": None,
                "serial_number": "",
                "device_type": "Эльтон-Ex231",
            },
            {
                "title": "Т#2-89",
                "number_mine": all_mines().get("Нефтешахта №2"),
                "tunnel": all_tunnels().get("ЮВВШ-1эт."),
                "inclined_blocks": None,
                "subscriber_number": "5446",
                "picket": "75",
                "description": "",
                "slug": None,
                "serial_number": "",
                "device_type": "Эльтон-Ex231",
            },
            {
                "title": "Т#1-12",
                "number_mine": all_mines().get("Нефтешахта №3"),
                "tunnel": all_tunnels().get("КБ"),
                "inclined_blocks": None,
                "subscriber_number": "6132",
                "picket": "98",
                "description": "",
                "slug": None,
                "serial_number": "",
                "device_type": "Эльтон-Ex231",
            },
            {
                "title": "Т#1-25",
                "number_mine": all_mines().get("Нефтешахта №3"),
                "tunnel": all_tunnels().get("301 п.ш."),
                "inclined_blocks": None,
                "subscriber_number": "6408",
                "picket": "53+3",
                "description": "",
                "slug": None,
                "serial_number": "",
                "device_type": "Эльтон-Ex231",
            },
            {
                "title": "Т#2-74",
                "number_mine": all_mines().get("Нефтешахта №3"),
                "tunnel": all_tunnels().get("ВПрШ-0эт."),
                "inclined_blocks": None,
                "subscriber_number": "6446",
                "picket": "83",
                "description": "",
                "slug": None,
                "serial_number": "",
                "device_type": "Эльтон-Ex231",
            },
        ]

        # Создаём только несуществующие объекты
        existing_points = set(PointPhone.objects.values_list("title", flat=True))
        points_to_create = [PointPhone(**item) for item in points_list if item["title"] not in existing_points]

        if points_to_create:
            PointPhone.objects.bulk_create(points_to_create)
        self.stdout.write(f"Создано {len(points_to_create)} точек связи")

    # Создание начальных объектов в таблице 'BranchesBox'
    def create_branches_box(self):

        branches_box_list = [
            {
                "title": "1ССП32",
                "inclined_blocks": None,
                "name_slag": None,
                "number_mine": all_mines().get("Нефтешахта №1"),
                "tunnel": all_tunnels().get("СОШ-3эт."),
                "subsystem": all_subsystems().get("ППИТ"),
                "equipment": None,
                "picket": "5",
                "boolean_block": False,
                "description": "Станция связи позиционирования",
                "ip_address": "10.32.012.040",
                "serial_number": "192",
                "device_type": "Ethertex V4.11",
            },
            {
                "title": "1ССП55",
                "inclined_blocks": None,
                "name_slag": None,
                "number_mine": all_mines().get("Нефтешахта №1"),
                "tunnel": all_tunnels().get("СОШ-2эт."),
                "subsystem": all_subsystems().get("ППИТ"),
                "equipment": None,
                "picket": "1",
                "boolean_block": False,
                "description": "Станция связи позиционирования",
                "ip_address": "10.32.012.010",
                "serial_number": "162",
                "device_type": "Ethertex V4.11",
            },
            {
                "title": "1ССП34",
                "inclined_blocks": None,
                "name_slag": None,
                "number_mine": all_mines().get("Нефтешахта №1"),
                "tunnel": all_tunnels().get("СОШ-2эт."),
                "subsystem": all_subsystems().get("ППИТ"),
                "equipment": None,
                "picket": "1",
                "boolean_block": False,
                "description": "Станция связи позиционирования",
                "ip_address": "10.32.012.040",
                "serial_number": "199",
                "device_type": "Ethertex V4.11",
            },
            {
                "title": "50#12",
                "inclined_blocks": None,
                "name_slag": None,
                "number_mine": all_mines().get("Нефтешахта №1"),
                "tunnel": all_tunnels().get("СОШ-3эт."),
                "subsystem": all_subsystems().get("АТС"),
                "equipment": None,
                "picket": "2",
                "boolean_block": False,
                "description": "Клеммная коробка на 50 пар",
                "ip_address": None,
                "serial_number": "2687889654",
                "device_type": "КСРВ-Н",
            },
            {
                "title": "2ССП29",
                "inclined_blocks": None,
                "name_slag": None,
                "number_mine": all_mines().get("Нефтешахта №2"),
                "tunnel": all_tunnels().get("ЮОШ-1эт."),
                "subsystem": all_subsystems().get("ППИТ"),
                "equipment": None,
                "picket": "15",
                "boolean_block": False,
                "description": "Станция связи позиционирования",
                "ip_address": "10.32.023.040",
                "serial_number": "287",
                "device_type": "Ethertex V4.11",
            },
            {
                "title": "2ССП16",
                "inclined_blocks": None,
                "name_slag": None,
                "number_mine": all_mines().get("Нефтешахта №2"),
                "tunnel": all_tunnels().get("ЮНВШ-1эт."),
                "subsystem": all_subsystems().get("ППИТ"),
                "equipment": None,
                "picket": "35",
                "boolean_block": False,
                "description": "Станция связи позиционирования",
                "ip_address": "10.32.022.020",
                "serial_number": "274",
                "device_type": "Ethertex V4.11",
            },
            {
                "title": "2ССП09",
                "inclined_blocks": None,
                "name_slag": None,
                "number_mine": all_mines().get("Нефтешахта №2"),
                "tunnel": all_tunnels().get("ЮВВШ-2эт."),
                "subsystem": all_subsystems().get("ППИТ"),
                "equipment": None,
                "picket": "1",
                "boolean_block": False,
                "description": "Станция связи позиционирования",
                "ip_address": "10.32.021.090",
                "serial_number": "267",
                "device_type": "Ethertex V4.11",
            },
            {
                "title": "50#4",
                "inclined_blocks": None,
                "name_slag": None,
                "number_mine": all_mines().get("Нефтешахта №2"),
                "tunnel": all_tunnels().get("ЗКБ"),
                "subsystem": all_subsystems().get("АТС"),
                "equipment": None,
                "picket": "44",
                "boolean_block": False,
                "description": "Клеммная коробка на 50 пар",
                "ip_address": None,
                "serial_number": "2536548754",
                "device_type": "КСРВ-Н",
            },
            {
                "title": "3ССП51",
                "inclined_blocks": None,
                "name_slag": None,
                "number_mine": all_mines().get("Нефтешахта №3"),
                "tunnel": all_tunnels().get("301 п.ш."),
                "subsystem": all_subsystems().get("ППИТ"),
                "equipment": None,
                "picket": "67+4",
                "boolean_block": False,
                "description": "Станция связи позиционирования",
                "ip_address": "10.32.035.030",
                "serial_number": "258",
                "device_type": "Ethertex V4.11",
            },
            {
                "title": "3ССП38",
                "inclined_blocks": None,
                "name_slag": None,
                "number_mine": all_mines().get("Нефтешахта №3"),
                "tunnel": all_tunnels().get("ВПрШ-0эт."),
                "subsystem": all_subsystems().get("ППИТ"),
                "equipment": None,
                "picket": "2+5",
                "boolean_block": False,
                "description": "Станция связи позиционирования",
                "ip_address": "10.32.034.020",
                "serial_number": "245",
                "device_type": "Ethertex V4.11",
            },
            {
                "title": "3ССП39",
                "inclined_blocks": None,
                "name_slag": None,
                "number_mine": all_mines().get("Нефтешахта №3"),
                "tunnel": all_tunnels().get("ВОШ-1эт."),
                "subsystem": all_subsystems().get("ППИТ"),
                "equipment": None,
                "picket": "15",
                "boolean_block": False,
                "description": "Станция связи позиционирования",
                "ip_address": "10.32.034.030",
                "serial_number": "246",
                "device_type": "Ethertex V4.11",
            },
            {
                "title": "50#10",
                "inclined_blocks": None,
                "name_slag": None,
                "number_mine": all_mines().get("Нефтешахта №3"),
                "tunnel": all_tunnels().get("КБ"),
                "subsystem": all_subsystems().get("АТС"),
                "equipment": None,
                "picket": "1",
                "boolean_block": False,
                "description": "Клеммная коробка на 50 пар",
                "ip_address": None,
                "serial_number": "2536556451",
                "device_type": "КСРВ-Н",
            },
        ]

        # Создаём только несуществующие объекты
        existing_branches_box = set(BranchesBox.objects.values_list("title", flat=True))
        branches_box_to_create = [
            BranchesBox(**item) for item in branches_box_list if item["title"] not in existing_branches_box
        ]

        if branches_box_to_create:
            BranchesBox.objects.bulk_create(branches_box_to_create)
        self.stdout.write(f"Создано {len(branches_box_to_create)} распределительных коробок")

    # Создание начальных объектов в таблице 'Unit'
    def create_cable_magazine(self):
        cable_magazine_list = [
            {
                "cable": all_cables().get("10"),
                "name": "",
                "subsystem": all_subsystems().get("СОШ-2эт."),
                "number_mine": all_mines().get("Нефтешахта №1"),
                "inclined_blocks": all_blocks().get(""),
                "track_from_box": all_boxs().get(""),  # Если это коробка, то указываем  от all_boxs().get(""). ForeignKey
                "track_from": "",  # Если нет коробки, то указываем от .(str)
                "track_to_box": all_boxs().get(""),  # Если есть коробка, то указываем до  all_boxs().get(""). (ForeignKey)
                "track_to_phone": all_points_phones().get(""),  # Если это телефон, то указываем до all_points_phones().get(""). (ForeignKey)
                "track_to": "",  # Если нет телефона, то указываем. (str)
                "distance": "",
                "unit": all_units().get("м."),
                "cable_bool": True,
                "slug": None,
            }
        ]
        # Создаём только несуществующие объекты
        existing_cable_magazine = set(CableMagazine.objects.values_list("name", flat=True))
        cable_magazine_to_create = [
            CableMagazine(**item) for item in cable_magazine_list if item["name"] not in existing_cable_magazine
        ]

        if cable_magazine_to_create:
            CableMagazine.objects.bulk_create(cable_magazine_to_create)
        self.stdout.write(f"Создано {len(cable_magazine_to_create)} объектов")
