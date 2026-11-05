from infoMFSS.admin_mixins import ExcelImportMixin
import logging

from django.contrib import admin, messages
from django.contrib.admin import AdminSite
from django.contrib.auth.admin import GroupAdmin, UserAdmin
from django.contrib.auth.models import Group, User
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import path, reverse

from infoMFSS.models import (Beacon, BranchesBox, Cable, CableMagazine,
                             DateUpdate, Equipment, EquipmentInstallation,
                             Execution, InclinedBlocks, NumberMine, PointPhone,
                             Subsystem, Tunnel, Unit, Violations, Visual, DailyNumbersMine, ManualPercentage, Surface)

logger = logging.getLogger(__name__)

# Условный импорт для избежания ошибок при отсутствии openpyxl
try:
    from infoMFSS.admin_import import (
        import_beacons_from_excel,
        import_tunnels_from_excel,
        import_equipment_from_excel,
        import_pointphones_from_excel,
        import_branchesbox_from_excel,
        import_equipmentinstallation_from_excel,
        import_cablemagazine_from_excel,
        import_execution_from_excel,
        import_violations_from_excel,
    )
    OPENPYXL_AVAILABLE = True
except ImportError:
    OPENPYXL_AVAILABLE = False
    logger.warning("openpyxl не установлен. Импорт Excel недоступен.")
    # Определяем заглушки для функций, чтобы избежать NameError
    import_beacons_from_excel = None
    import_tunnels_from_excel = None
    import_equipment_from_excel = None
    import_pointphones_from_excel = None
    import_branchesbox_from_excel = None
    import_equipmentinstallation_from_excel = None
    import_cablemagazine_from_excel = None
    import_execution_from_excel = None
    import_violations_from_excel = None


class MyAdminSite(AdminSite):

    def get_app_list(self, request, app_label=None):
        """
        Return a sorted list of all the installed apps that have been
        registered in this site.
        """
        app_dict = self._build_app_dict(request, app_label)

        # Сортируем список в алфавитном порядке.
        app_list = sorted(app_dict.values(), key=lambda x: x["name"].lower())

        return app_list


admin.site = MyAdminSite()


# @admin.register(NumberMine)
class NumberMineAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "address_mine", "slug")
    prepopulated_fields = {"slug": ("title",)}
    list_filter = ("title",)
    search_fields = ("title",)


# @admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "description",
    )
    list_filter = ("title",)
    search_fields = ("title",)


# @admin.register(Subsystem)
class SubsystemAdmin(admin.ModelAdmin):
    list_display = ("title", "description", "slug")
    prepopulated_fields = {"slug": ("title",)}
    list_filter = ("title",)
    search_fields = ("title",)


# @admin.register(Tunnel)
class TunnelAdmin(ExcelImportMixin, admin.ModelAdmin):
    import_function = import_tunnels_from_excel
    list_display = (
        "number_mine",
        "title",
        "inclined_blocks",
        "tuf_bool",
        "inclined_bool",
        "description",
    )
    list_filter = (
        "title",
        "number_mine",
        "inclined_blocks",
        "tuf_bool",
        "inclined_bool",
    )
    search_fields = (
        "title",
        "number_mine",
        "inclined_blocks",
        "tuf_bool",
        "inclined_bool",
    )


# @admin.register(InclinedBlocks)
class InclinedBlocksAdmin(admin.ModelAdmin):
    list_display = ("title", "number_mine", "description", "slug")
    prepopulated_fields = {"slug": ("title",)}
    list_filter = ("title", "number_mine")
    search_fields = ("title", "number_mine")


# @admin.register(Equipment)
class EquipmentAdmin(ExcelImportMixin, admin.ModelAdmin):
    import_function = import_equipment_from_excel
    list_display = ("title", "description", "subsystem", "file_pdf", "file_passport", "file_certificate")
    list_filter = ("title",)
    search_fields = ("title",)


# @admin.register(Cable)
class CableAdmin(admin.ModelAdmin):
    list_display = ("title", "device_type", "description", "file_pdf", "file_passport", "file_certificate")
    list_filter = ("title",)
    search_fields = ("title",)


# @admin.register(PointPhone)
class PointPhoneAdmin(ExcelImportMixin, admin.ModelAdmin):
    import_function = import_pointphones_from_excel
    list_display = (
        "id",
        "title",
        "device_type",
        "number_mine",
        "tunnel",
        "inclined_blocks",
        "subscriber_number",
        "description",
        "picket",
        "serial_number",
    )
    list_filter = (
        "title",
        "number_mine",
        "subscriber_number",
    )
    search_fields = ("title", "number_mine", "subscriber_number")


# @admin.register(BranchesBox)
class BranchesBoxAdmin(ExcelImportMixin, admin.ModelAdmin):
    import_function = import_branchesbox_from_excel
    list_display = (
        "title",
        "device_type",
        "number_mine",
        "tunnel",
        "inclined_blocks",
        "subsystem",
        "equipment",
        "picket",
        "description",
        "ip_address",
        "serial_number",
    )
    list_filter = (
        "title",
        "number_mine",
        "subsystem",
        "description",
    )
    search_fields = (
        "title",
        "number_mine",
        "subsystem",
        "description",
    )


class BeaconAdmin(admin.ModelAdmin):
    list_display = (
        "designation",
        "number_mine",
        "tunnel",
        "inclined_blocks",
        "picket",
        "mac_address",
        "serial_number",
        "minor",
        "execution_bool",
        "data",
    )
    list_filter = ("designation", "number_mine", "tunnel", "inclined_blocks", "serial_number", "minor", "data")
    search_fields = (
        "designation",
        "number_mine__title",
        "tunnel__title",
        "inclined_blocks__title",
        "picket",
        "mac_address",
        "serial_number",
        "minor",
    )

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('import-excel/', self.admin_site.admin_view(self.import_excel_view), name='infoMFSS_beacon_import_excel'),
        ]
        return custom_urls + urls

    def import_excel_view(self, request):
        """
        Представление для импорта биконов из Excel файла
        """
        if not OPENPYXL_AVAILABLE:
            self.message_user(
                request,
                "Модуль openpyxl не установлен. Установите его командой: pip install openpyxl",
                level=messages.ERROR
            )
            return HttpResponseRedirect(reverse('admin:infoMFSS_beacon_changelist'))

        if request.method == 'POST':
            excel_file = request.FILES.get('excel_file')
            if not excel_file:
                self.message_user(request, "Файл не выбран", level=messages.ERROR)
                return HttpResponseRedirect(reverse('admin:infoMFSS_beacon_changelist'))

            # Проверяем расширение файла
            if not excel_file.name.endswith(('.xlsx', '.xls')):
                self.message_user(request, "Поддерживаются только файлы Excel (.xlsx, .xls)", level=messages.ERROR)
                return HttpResponseRedirect(reverse('admin:infoMFSS_beacon_changelist'))

            # Проверяем размер файла (максимум 50 MB)
            if excel_file.size > 50 * 1024 * 1024:
                self.message_user(request, "Размер файла превышает 50 MB", level=messages.ERROR)
                return HttpResponseRedirect(reverse('admin:infoMFSS_beacon_changelist'))

            try:
                # Импортируем данные
                success_count, error_count, errors_list = import_beacons_from_excel(excel_file)
            except Exception as e:
                logger.error(f"Ошибка при импорте Excel файла: {str(e)}", exc_info=True)
                self.message_user(
                    request,
                    f"Произошла ошибка при импорте файла: {str(e)}",
                    level=messages.ERROR
                )
                return HttpResponseRedirect(reverse('admin:infoMFSS_beacon_changelist'))

            # Формируем сообщения
            if success_count > 0:
                self.message_user(
                    request,
                    f"Успешно импортировано биконов: {success_count}",
                    level=messages.SUCCESS
                )

            if error_count > 0:
                error_msg = f"Ошибок при импорте: {error_count}"
                if errors_list:
                    error_msg += f". Первые ошибки: {', '.join(errors_list[:5])}"
                self.message_user(request, error_msg, level=messages.WARNING)

            if success_count == 0 and error_count == 0:
                error_msg = "Не удалось импортировать данные."
                if errors_list:
                    error_msg += f" {errors_list[0]}"
                else:
                    error_msg += " Проверьте формат файла и наличие данных."
                self.message_user(request, error_msg, level=messages.ERROR)

            return HttpResponseRedirect(reverse('admin:infoMFSS_beacon_changelist'))

        # GET запрос - показываем форму загрузки
        context = {
            **self.admin_site.each_context(request),
            'title': 'Импорт биконов из Excel',
            'opts': self.model._meta,
            'has_view_permission': self.has_view_permission(request, None),
        }
        return render(request, 'admin/infoMFSS/beacon/import_excel.html', context)

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_import_button'] = True
        return super().changelist_view(request, extra_context)


@admin.register(Visual)
class VisualAdmin(admin.ModelAdmin):
    list_display = (
        "number_mine",
        "subsystem",
        "equipment",
        "cable",
        "file_pdf",
        "data",
    )
    list_filter = ("number_mine", "subsystem", "equipment", "cable", "data")
    search_fields = ("number_mine", "subsystem", "equipment", "cable", "data")


# @admin.register(Violations)
class ViolationsAdmin(ExcelImportMixin, admin.ModelAdmin):
    import_function = import_violations_from_excel
    list_display = (
        "number_act",
        "date_act",
        "issued_by_act",
        "number_mine",
        "title",
        "execution_bool",
        "file_act",
        "file_notification",
    )
    list_filter = ("number_act", "date_act", "issued_by_act", "number_mine", "execution_bool")
    search_fields = ("number_act", "date_act", "issued_by_act", "number_mine__title", "execution_bool")


# @admin.register(CableMagazine)
class CableMagazineAdmin(ExcelImportMixin, admin.ModelAdmin):
    import_function = import_cablemagazine_from_excel
    list_display = (
        "cable",
        "name",
        "subsystem",
        "number_mine",
        "inclined_blocks",
        "track_from",
        "track_to",
        "distance",
        "unit",
        "slug",
    )
    # prepopulated_fields = {'slug': ('track_from')}
    prepopulated_fields = {"slug": ("track_from", "track_to")}
    list_filter = (
        "cable",
        "name",
        "subsystem",
        "number_mine",
        "inclined_blocks",
    )
    search_fields = (
        "cable",
        "name",
        "subsystem",
        "number_mine",
        "inclined_blocks",
    )


# @admin.register(EquipmentInstallation)
class EquipmentInstallationAdmin(ExcelImportMixin, admin.ModelAdmin):
    import_function = import_equipmentinstallation_from_excel
    list_display = (
        "title",
        "name",
        "point_phone",
        "point_phone__subscriber_number",
        "branches_box",
        "number_mine",
        "tunnel",
        "inclined_blocks",
        "subsystem",
        "picket",
        "description",
        "ip_address",
        "serial_number",
        "device_type",
    )
    list_filter = ("title", "subsystem", "number_mine", "tunnel", "inclined_blocks", "point_phone")
    search_fields = ("title", "subsystem", "number_mine", "tunnel", "inclined_blocks", "point_phone")


# @admin.register(Execution)
class ExecutionAdmin(ExcelImportMixin, admin.ModelAdmin):
    import_function = import_execution_from_excel
    list_display = ("equipment_install", "cable_magazine", "execution_bool", "date_start", "date_end", "description")
    # prepopulated_fields = {'slug': ['description']}
    list_filter = ("equipment_install", "cable_magazine", "execution_bool", "date_start", "date_end")
    search_fields = ("equipment_install", "cable_magazine", "execution_bool", "date_start", "date_end")


# @admin.register(DateUpdate)
class DateUpdateAdmin(admin.ModelAdmin):
    list_display = (
        "update",
        "description",
    )


# ВРЕМЕННОЕ РЕШЕНИЕ УДАЛИТЬ ПОСЛЕ ЗАПОЛНЕНИЯ БД
class DailyNumbersMineMineAdmin(admin.ModelAdmin):
    list_display = (
        "date",
        "nsh1",
        "nsh2",
        "nsh3",
        "total",
    )
    readonly_fields = ('date',)
    search_fields = ("date", "nsh1", "nsh2", "nsh3", "total",)

    list_filter = ("date",)


# ВРЕМЕННОЕ РЕШЕНИЕ УДАЛИТЬ ПОСЛЕ ЗАПОЛНЕНИЯ БД
class ManualPercentageAdmin(admin.ModelAdmin):
    list_display = (
        "mine",
        "surface",
        "inclined_block",
        "subsystem",
        "percent",
        "date",
    )
    search_fields = ("mine", "surface", "inclined_block", "subsystem", "percent", "date",)
    list_filter = ("date",)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "incl_blocks":
            kwargs["empty_label"] = "Отсутствует"
            kwargs["required"] = False
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class SurfaceAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "mine",
    )


admin.site.register(NumberMine, NumberMineAdmin)
admin.site.register(Unit, UnitAdmin)
admin.site.register(Subsystem, SubsystemAdmin)
admin.site.register(Tunnel, TunnelAdmin)
admin.site.register(InclinedBlocks, InclinedBlocksAdmin)
admin.site.register(Equipment, EquipmentAdmin)
admin.site.register(Cable, CableAdmin)
admin.site.register(Beacon, BeaconAdmin)
admin.site.register(PointPhone, PointPhoneAdmin)
admin.site.register(BranchesBox, BranchesBoxAdmin)
admin.site.register(Visual, VisualAdmin)
admin.site.register(Violations, ViolationsAdmin)
admin.site.register(CableMagazine, CableMagazineAdmin)
admin.site.register(EquipmentInstallation, EquipmentInstallationAdmin)
admin.site.register(Execution, ExecutionAdmin)
admin.site.register(DateUpdate, DateUpdateAdmin)
admin.site.register(DailyNumbersMine, DailyNumbersMineMineAdmin)
admin.site.register(ManualPercentage, ManualPercentageAdmin)
admin.site.register(Surface, SurfaceAdmin)


admin.site.register(Group, GroupAdmin)
admin.site.register(User, UserAdmin)
