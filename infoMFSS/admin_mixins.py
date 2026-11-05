"""
Миксины для админки Django
"""
import logging

from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import path, reverse

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


class ExcelImportMixin:
    """Миксин для добавления функционала импорта Excel в админку"""

    import_function = None  # Должна быть переопределена в дочернем классе
    model_name = None  # Должна быть переопределена в дочернем классе
    template_name = 'admin/infoMFSS/import_excel.html'  # Универсальный шаблон

    def get_urls(self):
        urls = super().get_urls()
        if self.import_function:
            model_name_lower = self.model._meta.model_name
            custom_urls = [
                path('import-excel/',
                     self.admin_site.admin_view(self.import_excel_view),
                     name=f'infoMFSS_{model_name_lower}_import_excel'),
            ]
            return custom_urls + urls
        return urls

    def import_excel_view(self, request):
        """Представление для импорта из Excel файла"""
        if not OPENPYXL_AVAILABLE:
            self.message_user(
                request,
                "Модуль openpyxl не установлен. Установите его командой: pip install openpyxl",
                level=messages.ERROR
            )
            return HttpResponseRedirect(self.get_changelist_url())

        if request.method == 'POST':
            excel_file = request.FILES.get('excel_file')
            if not excel_file:
                self.message_user(request, "Файл не выбран", level=messages.ERROR)
                return HttpResponseRedirect(self.get_changelist_url())

            # Проверяем расширение файла
            if not excel_file.name.endswith(('.xlsx', '.xls')):
                self.message_user(request, "Поддерживаются только файлы Excel (.xlsx, .xls)", level=messages.ERROR)
                return HttpResponseRedirect(self.get_changelist_url())

            # Проверяем размер файла (максимум 50 MB)
            if excel_file.size > 50 * 1024 * 1024:
                self.message_user(request, "Размер файла превышает 50 MB", level=messages.ERROR)
                return HttpResponseRedirect(self.get_changelist_url())

            try:
                # Импортируем данные
                success_count, error_count, errors_list = self.import_function(excel_file)
            except Exception as e:
                logger.error(f"Ошибка при импорте Excel файла: {str(e)}", exc_info=True)
                self.message_user(
                    request,
                    f"Произошла ошибка при импорте файла: {str(e)}",
                    level=messages.ERROR
                )
                return HttpResponseRedirect(self.get_changelist_url())

            # Формируем сообщения
            if success_count > 0:
                model_verbose_name = self.model._meta.verbose_name_plural or self.model._meta.verbose_name
                self.message_user(
                    request,
                    f"Успешно импортировано {model_verbose_name}: {success_count}",
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

            return HttpResponseRedirect(self.get_changelist_url())

        # GET запрос - показываем форму загрузки
        model_verbose_name = self.model._meta.verbose_name_plural or self.model._meta.verbose_name
        context = {
            **self.admin_site.each_context(request),
            'title': f'Импорт {model_verbose_name} из Excel',
            'opts': self.model._meta,
            'has_view_permission': self.has_view_permission(request, None),
        }
        return render(request, self.template_name, context)

    def get_changelist_url(self):
        """Получить URL списка объектов"""
        model_name = self.model._meta.model_name
        return reverse(f'admin:infoMFSS_{model_name}_changelist')

    def changelist_view(self, request, extra_context=None):
        """Переопределяем для добавления кнопки импорта"""
        extra_context = extra_context or {}
        if self.import_function:
            extra_context['show_import_button'] = True
        return super().changelist_view(request, extra_context=extra_context)
