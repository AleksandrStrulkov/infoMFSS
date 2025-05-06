import django_filters
from django.db.models import Q
from django_filters import Filter

from infoMFSS.models import Execution, InclinedBlocks, NumberMine, Subsystem


class CustomEquipmentFilter(Filter):
    def filter(self, qs, *subsystem):
        if subsystem is not None:
            # Ваша кастомная логика фильтрации
            qs = qs.filter(
                Q(equipment_install__number_mine__title=subsystem)
                | Q(equipment_install__subsystem__title=subsystem)
                | Q(equipment_install__inclined_blocks__title=subsystem)
            )
        return qs


class MineSabInclFilter(django_filters.FilterSet):
    # mine_sub_incl = CustomEquipmentFilter()
    mine = django_filters.ModelChoiceFilter(
        queryset=NumberMine.objects.all(), to_field_name="title", label="Шахта", initial="Все шахты"
    )
    subsystem = django_filters.ModelChoiceFilter(
        queryset=Subsystem.objects.all(), to_field_name="title", label="Подсистема", initial="Все подсистемы"
    )

    incl_blocks = django_filters.ModelChoiceFilter(
        queryset=InclinedBlocks.objects.all(),
        to_field_name="title",
        label="Уклонный блок",
        initial="Все уклонные блоки",
    )

    class Meta:
        model = Execution
        fields = ["subsystem", "incl_blocks"]
