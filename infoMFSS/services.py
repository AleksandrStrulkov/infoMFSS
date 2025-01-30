from django.db.models import Q
from .models import Execution


# class ExecutionFilterService:
#     @staticmethod
#     def get_filtered_queryset(params, is_form_submitted):
#         """
#         Возвращает:
#         - Пустой queryset, если форма не отправлена.
#         - Фильтрованный queryset, если форма отправлена.
#         """
#         if not is_form_submitted:
#             return Execution.objects.none()
#
#         filters = Q(execution_bool=True)
#
        # # Обработка шахты
        # mine = params.get("mine")
        # if mine and mine != "Все шахты":
        #     filters &= Q(equipment_install__number_mine__title=mine)
        #
        # # Обработка подсистемы
        # subsystem = params.get("subsystem")
        # if subsystem and subsystem != "Все подсистемы":
        #     filters &= Q(equipment_install__subsystem__title=subsystem)
        #
        # # Обработка уклонных блоков
        # incl_blocks = params.get("incl_blocks")
        # if incl_blocks and incl_blocks != "Все уклонные блоки":
        #     filters &= Q(equipment_install__inclined_blocks__title=incl_blocks)
        #
        # # Обработка оборудования
        # equipment = params.get("equipment")
        # if equipment and equipment != "Все оборудование":
        #     filters &= Q(equipment_install__title__title=equipment)
        #
        # return Execution.objects.filter(filters).order_by("equipment_install__number_mine__title")

class EquipmentFilterService:
    @staticmethod
    def get_filtered_queryset(filter_params):
        """
        Фильтрует данные на основе параметров из FilterParams.
        - Если форма не отправлена, возвращает пустой queryset.
        """
        if not filter_params.is_form_submitted:
            return None

        # Получаем параметры через метод get()
        mine = filter_params.get("mine",)
        subsystem = filter_params.get("subsystem",)
        incl_blocks = filter_params.get("incl_blocks",)
        equipment = filter_params.get("equipment",)

        # Строим фильтры
        filters = Q(execution_bool=True)

        # Обработка шахты
        if mine != "Все шахты":
            filters &= Q(equipment_install__number_mine__title=mine)

        # Обработка подсистемы
        if subsystem != "Все подсистемы":
            filters &= Q(equipment_install__subsystem__title=subsystem)

        # Обработка уклонных блоков
        if incl_blocks != "Все уклонные блоки":
            filters &= Q(equipment_install__inclined_blocks__title=incl_blocks)

        # Обработка оборудования
        if equipment != "Все оборудование":
            filters &= Q(equipment_install__title__title=equipment)

        return Execution.objects.filter(filters).order_by("equipment_install__number_mine__title")


