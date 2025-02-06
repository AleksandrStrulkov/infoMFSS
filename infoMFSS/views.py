import logging

from django.core.mail import send_mail
from django.http import HttpResponseRedirect
from django.core.cache import cache
from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView, FormView
from django.urls import reverse
from infoMFSS.models import Execution, DateUpdate, NumberMine, Subsystem, InclinedBlocks, PointPhone, BranchesBox, \
    Equipment, Cable, Violations, Visual, EquipmentInstallation, CableMagazine
from infoMFSS.forms import PercentForm, EquipmentForm, CableForm, BoxForm, VisualCreateForm, ProjectEquipmentForm, \
    ProjectCableForm, ContactForm, QuantityEquipmentCableForm
from django.shortcuts import render
from django.core.cache import cache
from django.conf import settings
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin, \
    PermissionRequiredMixin
from .services import EquipmentFilterService, CableFilterService, BoxFilterService, VisualFilterService, \
    ProjectEquipmentFilterService, ProjectCableFilterService, PercentService, QuantityEqCabFilterService
from .params import FilterParams


def sass_page_handler(request):
    return render(request, 'mfss/base.html')


class MFSSPercentTemplateView(TemplateView):
    """"
    Вывод процентов выполнения по шахтам
    """
    template_name = 'mfss/home.html'
    extra_context = {
        'title': "МФСС",
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Список всех шахт
        mines = ["Нефтешахта №1", "Нефтешахта №2", "Нефтешахта №3"]

        # Вычисляем проценты для каждой шахты
        for mine in mines:
            result = PercentService.calculate_percent(mine=mine)
            context[f'percent_{mine.lower().replace(" ", "_").replace("нефтешахта_№", "mine")}'] = result['percent']

        # Общий процент для всех шахт
        result_all = PercentService.calculate_percent()
        context['percent_mine123'] = result_all['percent']

        # Последнее обновление
        context['update'] = PercentService.get_latest_update()

        return context


class PercentView(FormView):
    """
    Вывод процентов выполнения c формой и фильтром
    """
    template_name = 'mfss/percents.html'
    form_class = PercentForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Добавляем дополнительные данные в контекст
        context['update'] = PercentService.get_latest_update()
        options = PercentService.get_mines_subsystems_incl_blocks()
        context.update({
            'mines': options['mines'],
            'subsystems': options['subsystems'],
            'incl_blocks': options['incl_blocks'],
        })
        return context

    def form_valid(self, form):
        # Получаем данные из формы
        mine = form.cleaned_data.get("number_mines").title
        subsystem = form.cleaned_data.get("subsystems").title
        incl_blocks = form.cleaned_data.get("incl_blocks").title

        # Вызываем сервис для расчета процента
        result = PercentService.calculate_percent(mine, subsystem, incl_blocks)

        # Обновляем контекст данными из формы и результатами расчета
        context = self.get_context_data(form=form)
        context.update({
            'mine': mine,
            'subsystem': subsystem,
            'incl_blocks': incl_blocks,
            'percent': result['percent'],
            'data': {
                'total_count': result['total_count'],
                'true_count': result['true_count'],
            },
        })

        # Рендерим шаблон с обновленным контекстом
        return self.render_to_response(context)


class EquipmentListView(FormView):
    """
    Вывод списка установленного оборудования
    """
    form_class = EquipmentForm
    model = Execution
    template_name = 'mfss/equipment_list.html'
    context_object_name = 'equipment_list'
    success_url = reverse_lazy('mfss:equipment')
    extra_context = {
            'title': "Просмотр установленного оборудования",
    }
    result = 0

    def form_valid(self, form):
        """
        Метод вызывается, если форма прошла валидацию.
        """
        params = {
                "mine": form.cleaned_data.get("number_mines", ),
                "subsystem": form.cleaned_data.get("subsystems", ),
                "incl_blocks": form.cleaned_data.get("incl_blocks", ),
                "equipment": form.cleaned_data.get("equipment", ),
        }

        url = f"{reverse('mfss:equipment')}?{'&'.join(f'{key}={value}' for key, value in params.items())}"

        return HttpResponseRedirect(url)

    def get_context_data(self, **kwargs):
        """
        Метод для добавления дополнительного контекста в шаблон.
        Здесь выполняется фильтрация данных из базы.
        """
        context = super().get_context_data(**kwargs)
        filter_params = FilterParams(self.request)

        context["equipment_list"] = EquipmentFilterService.get_filtered_queryset(filter_params)

        # Добавляем параметры в контекст для отображения в шаблоне
        context.update(
                {
                        "mine": filter_params.get("mine", ),
                        "subsystem": filter_params.get("subsystem", ),
                        "incl_blocks": filter_params.get("incl_blocks", ),
                        "equipment": filter_params.get("equipment", ),
                }
        )

        return context


class CableListView(FormView):
    """
    Вывод списка проложенных трасс кабелей
    """
    form_class = CableForm
    model = Execution
    template_name = 'mfss/cable_list.html'
    context_object_name = 'cable_list'
    success_url = reverse_lazy('mfss:cable')
    extra_context = {
            'title': "Просмотр проложенных трасс кабелей",
    }
    result = 0

    def form_valid(self, form):
        """
        Метод вызывается, если форма прошла валидацию.
        """

        params = {
                "mine": form.cleaned_data.get("number_mines", ),
                "subsystem": form.cleaned_data.get("subsystems", ),
                "incl_blocks": form.cleaned_data.get("incl_blocks", ),
                "cable": form.cleaned_data.get("cable", ),
        }

        url = f"{reverse('mfss:cable')}?{'&'.join(f'{key}={value}' for key, value in params.items())}"

        return HttpResponseRedirect(url)

    def get_context_data(self, **kwargs):
        """
        Метод для добавления дополнительного контекста в шаблон.
        Здесь выполняется фильтрация данных из базы.
        """
        context = super().get_context_data(**kwargs)
        filter_params = FilterParams(self.request)

        context["cable_list"] = CableFilterService.get_filtered_queryset(filter_params)

        # Добавляем параметры в контекст для отображения в шаблоне
        context.update(
                {
                        "mine": filter_params.get("mine", ),
                        "subsystem": filter_params.get("subsystem", ),
                        "incl_blocks": filter_params.get("incl_blocks", ),
                        "cable": filter_params.get("cable", ),
                }
        )

        return context


class BoxListView(FormView):
    """
    Вывод списка подключенных устройств
    """
    form_class = BoxForm
    model = BranchesBox
    template_name = 'mfss/box_list.html'
    context_object_name = 'box_list'
    success_url = reverse_lazy('mfss:box')
    extra_context = {
            'title': "Просмотр подключенных устройств",
    }
    result = 0

    def form_valid(self, form):
        """
        Метод вызывается, если форма прошла валидацию.
        """

        params = {
                "mine": form.cleaned_data.get("number_mines", ),
                "subsystem": form.cleaned_data.get("subsystems", ),
                "incl_blocks": form.cleaned_data.get("incl_blocks", ),
        }

        url = f"{reverse('mfss:box')}?{'&'.join(f'{key}={value}' for key, value in params.items())}"

        return HttpResponseRedirect(url)

    def get_context_data(self, **kwargs):
        """
        Метод для добавления дополнительного контекста в шаблон.
        Здесь выполняется фильтрация данных из базы.
        """
        context = super().get_context_data(**kwargs)
        filter_params = FilterParams(self.request)

        context["box_list"] = BoxFilterService.get_filtered_queryset(filter_params)

        # Добавляем параметры в контекст для отображения в шаблоне
        context.update(
                {
                        "mine": filter_params.get("mine", ),
                        "subsystem": filter_params.get("subsystem", ),
                        "incl_blocks": filter_params.get("incl_blocks", ),
                }
        )

        return context


class EquipmentFileListView(ListView):
    """
    Вывод списка файлов с документацией по оборудованию
    """
    model = Equipment
    template_name = 'mfss/equipment_file_list.html'
    context_object_name = 'equipment_file_list'
    extra_context = {
            'title': "Документация (оборудование)",
    }


class CableFileListView(ListView):
    """
    Вывод списка файлов с документацией по кабелям
    """
    model = Cable
    template_name = 'mfss/cable_file_list.html'
    context_object_name = 'cable_file_list'
    extra_context = {
            'title': "Документация (кабели)",
    }


class ViolationsListView(ListView):
    """
    Вывод списка замечаний
    """
    model = Violations
    template_name = 'mfss/violations_list.html'
    context_object_name = 'violations_list'
    extra_context = {
            'title': "Обзор выданных замечаний",
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        summ = Violations.objects.all().count()
        mine1_summ = Violations.objects.filter(number_mine__title='Нефтешахта №1').count()
        mine1_true = Violations.objects.filter(number_mine__title='Нефтешахта №1', execution_bool=True).count()

        mine2_summ = Violations.objects.filter(number_mine__title='Нефтешахта №2').count()
        mine2_true = Violations.objects.filter(number_mine__title='Нефтешахта №2', execution_bool=True).count()

        mine3_summ = Violations.objects.filter(number_mine__title='Нефтешахта №3').count()
        mine3_true = Violations.objects.filter(number_mine__title='Нефтешахта №3', execution_bool=True).count()

        update = DateUpdate.objects.latest('update')

        context['summ'] = summ
        context['mine1_summ'] = mine1_summ
        context['mine1_true'] = mine1_true
        context['mine2_summ'] = mine2_summ
        context['mine2_true'] = mine2_true
        context['mine3_summ'] = mine3_summ
        context['mine3_true'] = mine3_true

        try:
            mine1_percent = int(mine1_true * 100 / mine1_summ)
        except ZeroDivisionError:
            mine1_percent = 0

        try:
            mine2_percent = int(mine2_true * 100 / mine2_summ)
        except ZeroDivisionError:
            mine2_percent = 0

        try:
            mine3_percent = int(mine3_true * 100 / mine3_summ)
        except ZeroDivisionError:
            mine3_percent = 0

        context['mine1_percent'] = mine1_percent
        context['mine2_percent'] = mine2_percent
        context['mine3_percent'] = mine3_percent
        context['update'] = update

        return context


class VisualView(FormView):
    """
    Вывод файла pdf для визуализации установленного оборудования
    """
    model = Visual
    form_class = VisualCreateForm
    template_name = 'mfss/visual_list.html'
    context_object_name = 'visual_list'
    success_url = reverse_lazy('mfss:visual')
    extra_context = {
            'title': "Визуализация установленного оборудования",
    }

    def form_valid(self, form):
        """
        Метод вызывается, если форма прошла валидацию.
        """
        params = {
                'mine': form.cleaned_data.get("number_mines", ),
                'equipment': form.cleaned_data.get("equipment", ),
        }

        url = f"{reverse('mfss:visual')}?{'&'.join(f'{key}={value}' for key, value in params.items())}"

        return HttpResponseRedirect(url)

    def get_context_data(self, *args, **kwargs):
        """
        Метод для добавления дополнительного контекста в шаблон.
        Здесь выполняется фильтрация данных из базы.
        """
        context = super().get_context_data(**kwargs)
        filter_params = FilterParams(self.request)

        context["visual_list"] = VisualFilterService.get_filtered_queryset(filter_params)

        context.update(
                {
                        "mine": filter_params.get("mine", ),
                        "equipment": filter_params.get("equipment", ),
                }
        )

        for visual in context["visual_list"]:
            context['pdf_visual'] = visual.file_pdf
        return context


class ProjectEquipmentListView(LoginRequiredMixin, FormView):
    """
    Вывод списка оборудования в соответствии с проектом МФСБ
    """
    model = EquipmentInstallation
    form_class = ProjectEquipmentForm
    template_name = 'mfss/project_equipment_list.html'
    context_object_name = 'project_equipment_list'
    success_url = reverse_lazy('mfss:project_equipment')
    extra_context = {
            'title': "Проект МФСБ (оборудование)",
    }

    def form_valid(self, form):
        """
        Метод вызывается, если форма прошла валидацию.
        """

        params = {
                'mine': form.cleaned_data.get('number_mines', ),
                'subsystem': form.cleaned_data.get('subsystems', )
        }

        url = f"{reverse('mfss:project_equipment')}?{'&'.join(f'{key}={value}' for key, value in params.items())}"

        return HttpResponseRedirect(url)

    def get_context_data(self, *args, **kwargs):
        """
        Метод для добавления дополнительного контекста в шаблон.
        Здесь выполняется фильтрация данных из базы.
        """
        context = super().get_context_data(**kwargs)
        filter_params = FilterParams(self.request)

        context["project_equipment_list"] = ProjectEquipmentFilterService.get_filtered_queryset(filter_params)

        context.update(
                {
                        "mine": filter_params.get("mine", ),
                        "subsystem": filter_params.get("subsystem", ),
                }
        )

        return context


class ProjectCableListView(LoginRequiredMixin, FormView):
    """
    Вывод списка кабельной продукции в соответствии с проектом МФСБ
    """
    model = CableMagazine
    form_class = ProjectCableForm
    template_name = 'mfss/project_cable_list.html'
    context_object_name = 'project_cable_list'
    success_url = reverse_lazy('mfss:project_cable')
    extra_context = {
            'title': "Проект МФСБ (кабельная продукция)",
    }

    def form_valid(self, form):
        """
        Метод вызывается, если форма прошла валидацию.
        """

        params = {
                'mine': form.cleaned_data.get('number_mines', ),
                'subsystem': form.cleaned_data.get('subsystems', )
        }

        url = f"{reverse('mfss:project_cable')}?{'&'.join(f'{key}={value}' for key, value in params.items())}"

        return HttpResponseRedirect(url)

    def get_context_data(self, *args, **kwargs):
        """
        Метод для добавления дополнительного контекста в шаблон.
        Здесь выполняется фильтрация данных из базы.
        """
        context = super().get_context_data(**kwargs)
        filter_params = FilterParams(self.request)

        context["project_cable_list"] = ProjectCableFilterService.get_filtered_queryset(filter_params)

        context.update(
                {
                        "mine": filter_params.get("mine", ),
                        "subsystem": filter_params.get("subsystem", ),
                }
        )

        return context


class ContactFormView(LoginRequiredMixin, FormView):
    """
    Форма для отправки сообщений администратору
    """
    template_name = 'mfss/contact.html'  # Шаблон для отображения формы
    form_class = ContactForm  # Форма, которую мы будем использовать
    success_url = reverse_lazy('mfss:contact_success')  # URL для перенаправления после успешной отправки

    def form_valid(self, form):
        """
        Этот метод вызывается, если форма прошла валидацию.
        Здесь мы отправляем письма администратору и пользователю.
        """
        # Получаем данные из формы
        name = form.cleaned_data['name']
        email = form.cleaned_data['email']
        message = form.cleaned_data['message']

        # Отправка письма администратору
        admin_subject = f"Новое сообщение от {name}"
        admin_message = f"Имя: {name}\nEmail: {email}\n\nСообщение:\n{message}"

        try:
            send_mail(
                admin_subject,
                admin_message,
                settings.DEFAULT_FROM_EMAIL,
                [settings.EMAIL_HOST_USER],  # Email администратора
                fail_silently=False,
            )

            # Отправка письма пользователю
            user_subject = "Ваше сообщение получено"
            user_message = f"Здравствуйте, {name}!\n\nСпасибо за ваше сообщение.\n\nВаше сообщение:\n{message}"
            send_mail(
                user_subject,
                user_message,
                settings.DEFAULT_FROM_EMAIL,
                [email],  # Email пользователя
                fail_silently=False,
            )
            # Возвращаем стандартный метод после успешной обработки
            return super().form_valid(form)

        except Exception as e:
            logger = logging.getLogger(__name__)
            # Добавляем ошибку в форму при проблемах с отправкой
            form.add_error(None, 'Ошибка отправки. Попробуйте позже.')
            logger.error(f"Ошибка отправки письма: {e}")
            return self.form_invalid(form)


class QuantityEquipmentCableView(LoginRequiredMixin, FormView):
    """
    Вывод количества установленного оборудования и кабельной продукции
    """
    form_class = QuantityEquipmentCableForm
    template_name = 'mfss/quantity_equipment_cable.html'
    context_object_name = 'quantity_equipment_cable_list'
    success_url = reverse_lazy('mfss:quantity_equipment_cable')
    extra_context = {
            'title': "Количество оборудования и кабельной продукции",
    }

    def get_context_data(self, *args, **kwargs):
        """
        Метод для добавления дополнительного контекста в шаблон.
        Здесь выполняется фильтрация данных из базы.
        """
        context = super().get_context_data(**kwargs)

        # Добавляем дополнительные данные в контекст
        context['update'] = QuantityEqCabFilterService.get_latest_update()

        return context

    def form_valid(self, form):
        """
        Метод вызывается, если форма прошла валидацию.
        """
        mine = form.cleaned_data.get("number_mines")
        equipment = form.cleaned_data.get("equipment")
        cable = form.cleaned_data.get("cable")

        result = QuantityEqCabFilterService.calculate_quantity(equipment, cable, mine)
        context = self.get_context_data(form=form)
        context.update(
                {
                        'mine': mine,
                        'equipment': equipment,
                        'cable': cable,
                        'quantity': result['quantity'],
                        'total_length': result['total_length'],
                }
        )

        return self.render_to_response(context)
