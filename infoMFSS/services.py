from django.db.models import Q, Sum

from .models import (Beacon, BranchesBox, Cable, CableMagazine, DateUpdate,
                     Equipment, EquipmentInstallation, Execution,
                     InclinedBlocks, NumberMine, Subsystem, Visual)


class BaseFilterService:
    """
    Универсальный сервис для фильтрации.
    Наследники должны определить:
    - model: Модель Django
    - filter_config: Словарь с конфигурацией полей
    - default_order: Поле для сортировки
    - base_filter: Базовое условие (например, Q(execution_bool=True))
    """

    model = None
    filter_config = {}
    default_order = None
    base_filter = Q()

    @classmethod
    def get_filtered_queryset(cls, filter_params):
        if not filter_params.is_form_submitted:
            return cls.model.objects.none()

        # Начальный фильтр (базовое условие)
        filters = cls.base_filter

        # Применяем фильтры из конфига
        for param_key, (field_path, ignore_value) in cls.filter_config.items():
            value = filter_params.get(param_key, ignore_value)
            if value != ignore_value:
                filters &= Q(**{field_path: value})

        return cls.model.objects.filter(filters).order_by(cls.default_order)


class PercentService:
    @staticmethod
    def calculate_percent(mine="Все шахты", subsystem="Все подсистемы", incl_blocks="Все уклонные блоки"):
        """Вычисляет процент выполнения на основе фильтров."""
        filters = Q()

        if mine != "Все шахты":
            filters &= Q(equipment_install__number_mine__title=mine) | Q(cable_magazine__number_mine__title=mine)

        if subsystem != "Все подсистемы":
            filters &= Q(equipment_install__subsystem__title=subsystem) | Q(cable_magazine__subsystem__title=subsystem)

        if incl_blocks != "Все уклонные блоки":
            filters &= Q(equipment_install__inclined_blocks__title=incl_blocks) | Q(
                cable_magazine__inclined_blocks__title=incl_blocks
            )

        # Общее количество записей
        total_count = Execution.objects.filter(filters).count()

        # Количество выполненных записей
        true_count = Execution.objects.filter(filters, execution_bool=True).count()

        try:
            percent = int(true_count * 100 / total_count)
        except ZeroDivisionError:
            percent = 0

        return {
            "total_count": total_count,
            "true_count": true_count,
            "percent": percent,
        }

    @staticmethod
    def get_mines_subsystems_incl_blocks():
        """Получает списки шахт, подсистем и уклонных блоков для формирования выборки."""
        mines = [obj.title for obj in NumberMine.objects.exclude(title="Все шахты")]
        subsystems = [obj.title for obj in Subsystem.objects.exclude(title="Все подсистемы")]
        incl_blocks = [obj.title for obj in InclinedBlocks.objects.exclude(title="Все уклонные блоки")]

        return {
            "mines": mines,
            "subsystems": subsystems,
            "incl_blocks": incl_blocks,
        }

    @staticmethod
    def get_latest_update():
        """Получает или создает начальную запись обновления."""
        try:
            return DateUpdate.objects.latest("update")
        except DateUpdate.DoesNotExist:
            from django.utils import timezone

            return DateUpdate.objects.create(update=timezone.now())


class EquipmentFilterService(BaseFilterService):
    model = Execution
    default_order = "equipment_install__number_mine__title"
    base_filter = Q(execution_bool=True)

    filter_config = {
        "mine": ("equipment_install__number_mine__title", "Все шахты"),
        "subsystem": ("equipment_install__subsystem__title", "Все подсистемы"),
        "incl_blocks": ("equipment_install__inclined_blocks__title", "Все уклонные блоки"),
        "equipment": ("equipment_install__title__title", "Все оборудование"),
    }


class CableFilterService(BaseFilterService):
    model = Execution
    default_order = "cable_magazine__number_mine__title"
    base_filter = Q(execution_bool=True)

    filter_config = {
        "mine": ("cable_magazine__number_mine__title", "Все шахты"),
        "subsystem": ("cable_magazine__subsystem__title", "Все подсистемы"),
        "incl_blocks": ("cable_magazine__inclined_blocks__title", "Все уклонные блоки"),
        "cable": ("cable_magazine__cable__title", "Все кабели"),
    }


class BoxFilterService(BaseFilterService):
    model = BranchesBox
    default_order = "number_mine"

    filter_config = {
        "mine": ("number_mine__title", "Все шахты"),
        "subsystem": ("subsystem__title", "Все подсистемы"),
        "incl_blocks": ("inclined_blocks__title", "Все уклонные блоки"),
    }


class BeaconFilterService(BaseFilterService):
    model = Beacon
    default_order = "number_mine"

    filter_config = {
        "mine": ("number_mine__title", "Все шахты"),
        "incl_blocks": ("inclined_blocks__title", "Все уклонные блоки"),
    }


class VisualFilterService(BaseFilterService):
    model = Visual
    default_order = "number_mine"

    filter_config = {
        "mine": ("number_mine__title", None),
        "equipment": ("equipment__title", None),
        "cable": ("cable__title", None),
    }

    @classmethod
    def get_filtered_queryset(cls, filter_params):
        if not filter_params.is_form_submitted:
            return cls.model.objects.none()

        # Получаем параметры
        mine = filter_params.get("mine", None)
        equipment = filter_params.get("equipment", None)
        cable = filter_params.get("cable", None)

        # Базовый фильтр
        filters = Q()

        # Фильтр по шахте (обязательное условие)
        if mine is not None:
            filters &= Q(number_mine__title=mine)

        # Фильтр по оборудованию или кабелю
        if equipment is not None or cable is not None:
            # Создаем два отдельных фильтра
            equipment_filter = Q(equipment__title=equipment) if equipment is not None else Q()
            cable_filter = Q(cable__title=cable) if cable is not None else Q()

            # Объединяем их через ИЛИ
            filters &= equipment_filter | cable_filter

        return cls.model.objects.filter(filters).order_by(cls.default_order)


class ProjectEquipmentFilterService(BaseFilterService):
    model = EquipmentInstallation
    default_order = "number_mine__title"

    filter_config = {
        "mine": ("number_mine__title", "Все шахты"),
        "subsystem": ("subsystem__title", "Все подсистемы"),
    }


class ProjectCableFilterService(ProjectEquipmentFilterService, BaseFilterService):
    model = CableMagazine


class QuantityEqCabFilterService:
    @staticmethod
    def calculate_quantity(equipment=None, cable=None, mine="Все шахты"):
        """Вычисляет количество установленного оборудования"""
        filters = Q()

        if mine != "Все шахты":
            filters &= Q(equipment_install__number_mine__title=mine) | Q(cable_magazine__number_mine__title=mine)

        if equipment is not None:
            filters &= Q(equipment_install__title__title=equipment)

        if cable is not None:
            filters &= Q(cable_magazine__cable__device_type=cable)

        # Общее количество записей
        quantity = Execution.objects.filter(filters, execution_bool=True).count()

        # Вычисляем сумму длины кабеля
        total_length = (
            Execution.objects.filter(filters, execution_bool=True).aggregate(total=Sum("cable_magazine__distance"))[
                "total"
            ]
            or 0
        )

        return {
            "quantity": quantity,
            "total_length": total_length,
        }

    @staticmethod
    def get_mines_subsystems_incl_blocks():
        """Получает списки шахт, оборудования и кабельной продукции"""
        mines = [obj.title for obj in NumberMine.objects.exclude(title="Все шахты")]
        equipment = [obj.title for obj in Equipment.objects.exclude(title="Все оборудование")]
        cable = [obj.title for obj in Cable.objects.exclude(title="Все кабели")]

        return {
            "mines": mines,
            "equipment": equipment,
            "cable": cable,
        }

    @staticmethod
    def get_latest_update():
        """Получает последнее обновление данных."""
        return DateUpdate.objects.latest("update")
