from django.contrib.messages.views import SuccessMessageMixin
from django.core.mail import send_mail
from django.http import HttpResponseRedirect
from django.core.cache import cache
from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView, FormView
from django.urls import reverse
from infoMFSS.models import Execution, DateUpdate, NumberMine, Subsystem, InclinedBlocks, PointPhone, BranchesBox, \
    Equipment, Cable, Violations, EquipmentInstallation, CableMagazine, Visual
from infoMFSS.forms import PercentForm, EquipmentForm, CableForm, BoxForm, ProjectEquipmentForm, \
    ProjectCableForm, ContactForm, QuantityEquipmentCableForm, EquipmentCreateForm, CableCreateForm, \
    PointPhoneCreateForm, BranchesBoxCreateForm, CableMagazineCreateForm, ViolationsCreateForm, VisualForm, \
    VisualCreateNewForm, CreateEquipmentInstallationForm, CreateExecutionForm
from django.shortcuts import render, redirect
from django.core.cache import cache
from django.conf import settings
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin, \
    PermissionRequiredMixin
from .services import EquipmentFilterService, CableFilterService, BoxFilterService, \
    ProjectEquipmentFilterService, ProjectCableFilterService, PercentService, QuantityEqCabFilterService, \
    VisualFilterService
from .params import FilterParams
from infoMFSS.services_logger import *
from django.contrib import messages


def sass_page_handler(request):
    return render(request, 'infoMFSS/base.html')


"""Чтение и вывод данных по формам и фильтрам зарегистрированным пользователям"""


class MFSSPercentTemplateView(TemplateView):
    """"
    Вывод процентов выполнения по шахтам
    """
    template_name = 'infoMFSS/home.html'
    extra_context = {
            'title': "МФСС",
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        try:
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

            logger_context_info(self)
        except Exception as e:
            logger_context_warning(self, e)
            context['error_message'] = f"Произошла ошибка в формировании данных"

        return context


class PercentView(LoggingMixin, LoginRequiredMixin, FormView):
    """
    Вывод процентов выполнения c формой и фильтром
    """
    template_name = 'infoMFSS/percents.html'
    form_class = PercentForm
    extra_context = {
            'title': "Процент выполнения",
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        try:
            # Добавляем дополнительные данные в контекст
            context['update'] = PercentService.get_latest_update()
            options = PercentService.get_mines_subsystems_incl_blocks()
            context.update(
                    {
                            'mines': options['mines'],
                            'subsystems': options['subsystems'],
                            'incl_blocks': options['incl_blocks'],
                    }
            )

            logger_context_info(self)
        except Exception as e:
            logger_context_warning(self, e)
            context['error_message'] = f"Произошла ошибка в формировании данных"

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
        context.update(
                {
                        'mine': mine,
                        'subsystem': subsystem,
                        'incl_blocks': incl_blocks,
                        'percent': result['percent'],
                        'data': {
                                'total_count': result['total_count'],
                                'true_count': result['true_count'],
                        },
                }
        )

        # Рендерим шаблон с обновленным контекстом
        logger_form_valid(self)
        return self.render_to_response(context)

    # def dispatch(self, request, *args, **kwargs):
    #     if not request.user.is_authenticated:
    #         return redirect('users:register')
    #     else:
    #         return super().dispatch(request, *args, **kwargs)


class EquipmentListView(LoggingMixin, LoginRequiredMixin, FormView):
    """
    Вывод списка установленного оборудования
    """
    form_class = EquipmentForm
    model = Execution
    template_name = 'infoMFSS/equipment_list.html'
    context_object_name = 'equipment_list'
    success_url = reverse_lazy('mfss:equipment')
    extra_context = {
            'title': "Просмотр установленного оборудования",
    }

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

        logger_form_valid(self)
        return HttpResponseRedirect(url)

    def get_context_data(self, **kwargs):
        """
        Метод для добавления дополнительного контекста в шаблон.
        Здесь выполняется фильтрация данных из базы.
        """
        context = super().get_context_data(**kwargs)
        filter_params = FilterParams(self.request)

        try:
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

            logger_context_info(self)
        except Exception as e:
            logger_context_warning(self, e)
            context['error_message'] = f"Произошла ошибка в формировании данных"

        return context


class CableListView(LoggingMixin, LoginRequiredMixin, FormView):
    """
    Вывод списка проложенных трасс кабелей
    """
    form_class = CableForm
    model = Execution
    template_name = 'infoMFSS/cable_list.html'
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

        logger_form_valid(self)
        return HttpResponseRedirect(url)

    def get_context_data(self, **kwargs):
        """
        Метод для добавления дополнительного контекста в шаблон.
        Здесь выполняется фильтрация данных из базы.
        """
        context = super().get_context_data(**kwargs)
        filter_params = FilterParams(self.request)

        try:
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

            logger_context_info(self)

        except Exception as e:
            logger_context_warning(self, e)
            context['error_message'] = f"Произошла ошибка в формировании данных"

        return context


class BoxListView(LoggingMixin, LoginRequiredMixin, FormView):
    """
    Вывод списка подключенных устройств
    """
    form_class = BoxForm
    model = BranchesBox
    template_name = 'infoMFSS/box_list.html'
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

        logger_form_valid(self)
        return HttpResponseRedirect(url)

    def get_context_data(self, **kwargs):
        """
        Метод для добавления дополнительного контекста в шаблон.
        Здесь выполняется фильтрация данных из базы.
        """
        context = super().get_context_data(**kwargs)
        filter_params = FilterParams(self.request)

        try:
            context["box_list"] = BoxFilterService.get_filtered_queryset(filter_params)

            # Добавляем параметры в контекст для отображения в шаблоне
            context.update(
                    {
                            "mine": filter_params.get("mine", ),
                            "subsystem": filter_params.get("subsystem", ),
                            "incl_blocks": filter_params.get("incl_blocks", ),
                    }
            )

            logger_context_info(self)
        except Exception as e:
            logger_context_warning(self, e)
            context['error_message'] = f"Произошла ошибка в формировании данных"

        return context


class EquipmentFileListView(LoggingMixin, LoginRequiredMixin, ListView):
    """
    Вывод списка файлов с документацией по оборудованию
    """
    model = Equipment
    template_name = 'infoMFSS/equipment_file_list.html'
    context_object_name = 'equipment_file_list'
    extra_context = {
            'title': "Документация (оборудование)",
    }


class CableFileListView(LoggingMixin, LoginRequiredMixin, ListView):
    """
    Вывод списка файлов с документацией по кабелям
    """
    model = Cable
    template_name = 'infoMFSS/cable_file_list.html'
    context_object_name = 'cable_file_list'
    extra_context = {
            'title': "Документация (кабели)",
    }


class ViolationsListView(LoggingMixin, LoginRequiredMixin, ListView):
    """
    Вывод списка замечаний
    """
    model = Violations
    template_name = 'infoMFSS/violations_list.html'
    context_object_name = 'violations_list'
    extra_context = {
            'title': "Обзор выданных замечаний",
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        try:
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

            logger_context_info(self)
        except Exception as e:
            logger_context_warning(self, e)
            context['error_message'] = f"Произошла ошибка в формировании данных"

        return context


class VisualView(LoggingMixin, LoginRequiredMixin, FormView):
    """
    Вывод файла pdf для визуализации установленного оборудования
    """
    model = Visual
    form_class = VisualForm
    template_name = 'infoMFSS/visual_list.html'
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
                'mine': form.cleaned_data.get("number_mine", ),
                'equipment': form.cleaned_data.get("equipment", ),
                'cable': form.cleaned_data.get("cable", ),
        }

        url = f"{reverse('mfss:visual')}?{'&'.join(f'{key}={value}' for key, value in params.items())}"

        logger_form_valid(self)
        return HttpResponseRedirect(url)

    def get_context_data(self, *args, **kwargs):
        """
        Метод для добавления дополнительного контекста в шаблон.
        Здесь выполняется фильтрация данных из базы.
        """
        context = super().get_context_data(**kwargs)
        filter_params = FilterParams(self.request)
        try:
            context["visual_list"] = VisualFilterService.get_filtered_queryset(filter_params)

            context.update(
                    {
                            "mine": filter_params.get("mine", ),
                            "equipment": filter_params.get("equipment", ),
                            "cable": filter_params.get("cable", ),
                    }
            )

            for visual in context["visual_list"]:
                context['pdf_visual'] = visual.file_pdf
            print(context)
            logger_context_info(self)
        except Exception as e:
            logger_context_warning(self, e)
            context['error_message'] = f"Произошла ошибка в формировании данных"
        return context


class ProjectEquipmentListView(LoggingMixin, LoginRequiredMixin, FormView):
    """
    Вывод списка оборудования в соответствии с проектом МФСБ
    """
    model = EquipmentInstallation
    form_class = ProjectEquipmentForm
    template_name = 'infoMFSS/project_equipment_list.html'
    context_object_name = 'project_equipment_list'
    success_url = reverse_lazy('mfss:project_equipment')
    extra_context = {
            'title': "Общий просмотр (оборудование)",
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
        logger.info(f"Форма {self.form_class} прошла валидацию")

        logger_form_valid(self)
        return HttpResponseRedirect(url)

    def get_context_data(self, *args, **kwargs):
        """
        Метод для добавления дополнительного контекста в шаблон.
        Здесь выполняется фильтрация данных из базы.
        """
        context = super().get_context_data(**kwargs)
        filter_params = FilterParams(self.request)

        try:
            context["project_equipment_list"] = ProjectEquipmentFilterService.get_filtered_queryset(filter_params)

            context.update(
                    {
                            "mine": filter_params.get("mine", ),
                            "subsystem": filter_params.get("subsystem", ),
                    }
            )

            logger_context_info(self)
        except Exception as e:
            logger_context_warning(self, e)
            context['error_message'] = f"Произошла ошибка в формировании данных"

        return context


class ProjectCableListView(LoggingMixin, LoginRequiredMixin, FormView):
    """
    Вывод списка кабельной продукции в соответствии с проектом МФСБ
    """
    model = CableMagazine
    form_class = ProjectCableForm
    template_name = 'infoMFSS/project_cable_list.html'
    context_object_name = 'project_cable_list'
    success_url = reverse_lazy('mfss:project_cable')
    extra_context = {
            'title': "Общий просмотр (кабельная продукция)",
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

        logger_form_valid(self)
        return HttpResponseRedirect(url)

    def get_context_data(self, *args, **kwargs):
        """
        Метод для добавления дополнительного контекста в шаблон.
        Здесь выполняется фильтрация данных из базы.
        """
        context = super().get_context_data(**kwargs)
        filter_params = FilterParams(self.request)

        try:
            context["project_cable_list"] = ProjectCableFilterService.get_filtered_queryset(filter_params)

            context.update(
                    {
                            "mine": filter_params.get("mine", ),
                            "subsystem": filter_params.get("subsystem", ),
                    }
            )

            logger_context_info(self)
        except Exception as e:
            logger_context_warning(self, e)
            context['error_message'] = f"Произошла ошибка в формировании данных"

        return context


class ContactFormView(LoggingMixin, FormView):
    """
    Форма для отправки сообщений администратору
    """
    template_name = 'infoMFSS/contact.html'  # Шаблон для отображения формы
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
        admin_message = f"Имя: {name}\nEmail: {email}\n\nСообщение:\n\n{message}"

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
            user_message = f"Здравствуйте, {name}!\n\nСпасибо за ваше сообщение.\n\nВаше сообщение:\n\n{message}"
            send_mail(
                    user_subject,
                    user_message,
                    settings.DEFAULT_FROM_EMAIL,
                    [email],  # Email пользователя
                    fail_silently=False,
            )
            # Возвращаем стандартный метод после успешной обработки
            logger.info("Письмо успешно отправлено", extra={'classname': self.__class__.__name__})
            return super().form_valid(form)

        except Exception as e:
            form.add_error(None, 'Ошибка отправки. Попробуйте позже.')
            logger.error(f"Ошибка отправки письма: {e}", extra={'classname': self.__class__.__name__})
            return self.form_invalid(form)

    def get_initial(self):
        initial = super().get_initial()
        if self.request.user.is_authenticated:
            initial['email'] = self.request.user.email  # Подставляем email авторизованного пользователя
            initial['name'] = self.request.user.first_name  # Подставляем имя авторизованного пользователя
        return initial


class QuantityEquipmentCableView(LoggingMixin, LoginRequiredMixin, FormView):
    """
    Вывод количества установленного оборудования и кабельной продукции
    """
    form_class = QuantityEquipmentCableForm
    template_name = 'infoMFSS/quantity_equipment_cable.html'
    context_object_name = 'quantity_equipment_cable_list'
    success_url = reverse_lazy('mfss:quantity_equipment_cable')
    extra_context = {
            'title': "Всего установлено",
    }

    def get_context_data(self, *args, **kwargs):
        """
        Метод для добавления дополнительного контекста в шаблон.
        Здесь выполняется фильтрация данных из базы.
        """
        context = super().get_context_data(**kwargs)

        try:
            # Добавляем дополнительные данные в контекст
            context['update'] = QuantityEqCabFilterService.get_latest_update()

            logger_context_info(self)
        except Exception as e:
            logger_context_warning(self, e)
            context['error_message'] = f"Произошла ошибка в формировании данных"

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

        logger_form_valid(self)
        return self.render_to_response(context)


"""Запись данных в БД для модераторов"""


class CreateEquipmentView(LoggingMixin, LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """
    Добавить в базу данных оборудование
    """
    model = Equipment
    form_class = EquipmentCreateForm
    permission_required = 'infoMFSS.add_equipment'
    success_url = reverse_lazy('mfss:create_equipment')
    template_name = 'infoMFSS/equipment_form.html'
    context_object_name = 'equipment_list'
    # success_message = 'Оборудование "%(title)s" успешно создано.'
    extra_context = {
            'title': "Добавить оборудование",
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['equipment_list'] = Equipment.objects.all()
        return context


class CreateCableView(LoggingMixin, LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """
    Добавить в базу данных кабельную продукцию
    """
    model = Cable
    form_class = CableCreateForm
    permission_required = 'infoMFSS.add_cable'
    success_url = reverse_lazy('mfss:create_cable')
    template_name = 'infoMFSS/cable_form.html'
    context_object_name = 'cable_list'
    extra_context = {
            'title': "Добавить кабельную продукцию",
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cable_list'] = Cable.objects.all()
        return context


class CreatePointPhoneView(LoggingMixin, LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """
    Добавить в базу данных точку телефонной связи
    """
    model = PointPhone
    form_class = PointPhoneCreateForm
    permission_required = 'infoMFSS.add_pointphone'
    success_url = reverse_lazy('mfss:create_pointphone')
    template_name = 'infoMFSS/pointphone_form.html'
    context_object_name = 'pointphone_list'
    extra_context = {
            'title': "Добавить точку телефонной связи",
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pointphone_list'] = PointPhone.objects.all()
        return context


class CreateBranchesBoxView(LoggingMixin, LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """
    Добавить в базу данных распределительные коробки
    """
    model = BranchesBox
    form_class = BranchesBoxCreateForm
    permission_required = 'infoMFSS.add_branchesbox'
    success_url = reverse_lazy('mfss:create_branchesbox')
    template_name = 'infoMFSS/branchesbox_form.html'
    context_object_name = 'branchesbox_list'
    extra_context = {
            'title': "Добавить распределительные коробки",
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['branchesbox_list'] = BranchesBox.objects.all()
        return context


class CreateCableMagazineView(LoggingMixin, LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """
    Добавить в базу данный значения в кабельный журнал
    """

    model = CableMagazine
    form_class = CableMagazineCreateForm
    permission_required = 'infoMFSS.add_cablemagazine'
    success_url = reverse_lazy('mfss:create_cablemagazine')
    template_name = 'infoMFSS/cable_magazine_form.html'
    context_object_name = 'cable_magazine_list'
    extra_context = {
            'title': "Добавить кабель в кабельный журнал",
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cable_magazine_list'] = CableMagazine.objects.all()
        return context


class CreateViolationsView(LoggingMixin, LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """
    Добавить в базу данных нарушения
    """
    model = Violations
    form_class = ViolationsCreateForm
    permission_required = 'infoMFSS.add_violations'
    success_url = reverse_lazy('mfss:create_violations')
    template_name = 'infoMFSS/violations_form.html'
    context_object_name = 'violations_list'
    extra_context = {
            'title': "Добавить отчет по замечаниям",
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['violations_list'] = Violations.objects.all()
        return context


class CreateVisualView(LoggingMixin, LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """
    Добавить в базу данных визуальное представление выполненных работ
    """
    model = Visual
    form_class = VisualCreateNewForm
    permission_required = 'infoMFSS.add_visual'
    success_url = reverse_lazy('mfss:create_visual')
    template_name = 'infoMFSS/visual_form.html'
    context_object_name = 'visual_list'
    extra_context = {
            'title': "Добавить визуальное представление выполненных работ",
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['visual_list'] = Visual.objects.all()
        return context


class CreateEquipmentInstallationView(LoggingMixin, LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """
    Добавить в базу данных места установки оборудования
    """
    model = EquipmentInstallation
    form_class = CreateEquipmentInstallationForm
    permission_required = 'infoMFSS.add_equipmentinstallation'
    success_url = reverse_lazy('mfss:create_equipment_installation')
    template_name = 'infoMFSS/create_equipment_installation_form.html'
    context_object_name = 'equipment_installation_list'
    extra_context = {
            'title': "Добавить место установки оборудования",
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['equipment_installation_list'] = EquipmentInstallation.objects.all()
        return context


class CreateExecutionView(LoggingMixin, LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """
    Добавить в базу данных отчет о выполненных работах
    """
    model = Execution
    form_class = CreateExecutionForm
    permission_required = 'infoMFSS.add_execution'
    success_url = reverse_lazy('mfss:create_execution')
    template_name = 'infoMFSS/create_execution_form.html'
    context_object_name = 'execution_list'
    extra_context = {
            'title': "Добавить в отчет выполненные работы",
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['execution_list'] = Execution.objects.all()
        return context


"""Отображение данных для модераторов для выбора изменения или удаления"""


class EquipmentView(LoggingMixin, LoginRequiredMixin, ListView):
    """
    Вывод списка оборудования для последующего изменения в БД
    """
    model = Equipment
    template_name = 'infoMFSS/equipment.html'
    context_object_name = 'equipment_list'
    extra_context = {
            'title': "Список оборудования",
    }
    # success_url = reverse_lazy('mfss:equipment_list')


class CableView(LoggingMixin, LoginRequiredMixin, ListView):
    """
    Вывод списка кабельных трасс для последующего изменения в БД
    """
    model = Cable
    template_name = 'infoMFSS/cable.html'
    context_object_name = 'cable_list'
    extra_context = {
            'title': "Список трасс кабелей",
    }


class PointPhoneView(LoggingMixin, LoginRequiredMixin, ListView):
    """
    Вывод списка точек телефонии для последующего изменения в БД
    """
    model = PointPhone
    template_name = 'infoMFSS/point_phone.html'
    context_object_name = 'point_phone_list'
    extra_context = {
            'title': "Список точек телефонии",
    }


class BranchesBoxView(LoggingMixin, LoginRequiredMixin, ListView):
    """
    Вывод списка точек телефонии для последующего изменения в БД
    """
    model = BranchesBox
    template_name = 'infoMFSS/branches_box.html'
    context_object_name = 'branches_box_list'
    extra_context = {
            'title': "Список распределительных коробок",
    }


class CableMagazineView(LoggingMixin, LoginRequiredMixin, ListView):
    """
    Вывод данных из кабельного журнала для последующего изменения в БД
    """
    model = CableMagazine
    template_name = 'infoMFSS/cable_magazine.html'
    context_object_name = 'cable_magazine_list'
    extra_context = {
            'title': "Кабельный журнал",
    }


class ViolationsView(LoggingMixin, LoginRequiredMixin, ListView):
    """
    Вывод списка нарушений для последующего изменения в БД
    """
    model = Violations
    template_name = 'infoMFSS/violations.html'
    context_object_name = 'violations_list'
    extra_context = {
            'title': "Список нарушений",
    }


class VisualistView(LoggingMixin, LoginRequiredMixin, ListView):
    """
    Вывод списка данных визуального представления выполненных работ для последующего изменения в БД
    """
    model = Visual
    template_name = 'infoMFSS/visual.html'
    context_object_name = 'visual_list'
    extra_context = {
            'title': "Список визуального представления выполненных работ",
    }


class EquipmentInstallationView(LoggingMixin, LoginRequiredMixin, ListView):
    """
    Вывод списка мест установки оборудования для последующего изменения в БД
    """
    model = EquipmentInstallation
    template_name = 'infoMFSS/equipment_installation.html'
    context_object_name = 'equipment_installation_list'
    extra_context = {
            'title': "Список мест установки оборудования",
    }


class ExecutionView(LoggingMixin, LoginRequiredMixin, ListView):
    """
    Вывод списка выполненных работ для последующего изменения в БД
    """
    model = Execution
    template_name = 'infoMFSS/execution.html'
    context_object_name = 'execution_list'
    extra_context = {
            'title': "Список выполненных работ",
    }


class UpdateEquipmentView(LoggingMixin, LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """
    Изменить оборудование в БД
    """
    model = Equipment
    form_class = EquipmentCreateForm
    permission_required = 'infoMFSS.change_equipment'
    template_name = 'infoMFSS/equipment_update_form.html'
    success_url = reverse_lazy('mfss:equipment_list')
    extra_context = {
            'title': "Редактирование списка оборудования",
    }

    def get_queryset(self, *args, **kwargs):
        queryset = super().get_queryset(*args, **kwargs)
        queryset = queryset.filter(id=self.kwargs.get('pk'))
        return queryset


class UpdateCableView(LoggingMixin, LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """
    Изменить в БД кабельную продукцию
    """
    model = Cable
    form_class = CableCreateForm
    permission_required = 'infoMFSS.change_cable'
    template_name = 'infoMFSS/cable_update_form.html'
    success_url = reverse_lazy('mfss:cable_list')
    extra_context = {
            'title': "Редактирование трассы кабеля",
    }

    def get_queryset(self, *args, **kwargs):
        queryset = super().get_queryset(*args, **kwargs)
        queryset = queryset.filter(id=self.kwargs.get('pk'))
        return queryset


class UpdatePointPhoneView(LoggingMixin, LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """
    Изменить в БД точку телефонной связи
    """
    model = PointPhone
    form_class = PointPhoneCreateForm
    permission_required = 'infoMFSS.change_pointphone'
    template_name = 'infoMFSS/point_phone_update_form.html'
    success_url = reverse_lazy('mfss:point_phone_list')
    extra_context = {
            'title': "Редактирование точки телефонной связи",
    }

    def get_queryset(self, *args, **kwargs):
        queryset = super().get_queryset(*args, **kwargs)
        queryset = queryset.filter(id=self.kwargs.get('pk'))
        return queryset


class UpdateBranchesBoxView(LoggingMixin, LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """
    Изменить в БД распределительные коробки
    """
    model = BranchesBox
    form_class = BranchesBoxCreateForm
    permission_required = 'infoMFSS.change_branchesbox'
    template_name = 'infoMFSS/branches_box_update_form.html'
    success_url = reverse_lazy('mfss:branches_box_list')
    extra_context = {
            'title': "Редактирование распределительных коробок",
    }

    def get_queryset(self, *args, **kwargs):
        queryset = super().get_queryset(*args, **kwargs)
        queryset = queryset.filter(id=self.kwargs.get('pk'))
        return queryset


class UpdateCableMagazineView(LoggingMixin, LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """
    Изменить в БД значения в кабельном журнале
    """
    model = CableMagazine
    form_class = CableMagazineCreateForm
    permission_required = 'infoMFSS.change_cablemagazine'
    template_name = 'infoMFSS/cable_magazine_update_form.html'
    success_url = reverse_lazy('mfss:cable_magazine_list')
    extra_context = {
            'title': "Редактирование данных в кабельном журнале",
    }

    def get_queryset(self, *args, **kwargs):
        queryset = super().get_queryset(*args, **kwargs)
        queryset = queryset.filter(id=self.kwargs.get('pk'))
        return queryset


class UpdateViolationsView(LoggingMixin, LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """
    Изменить в БД нарушения
    """
    model = Violations
    form_class = ViolationsCreateForm
    permission_required = 'infoMFSS.change_violations'
    template_name = 'infoMFSS/violations_update_form.html'
    success_url = reverse_lazy('mfss:violations_list')
    extra_context = {
            'title': "Редактирование списка нарушений",
    }

    def get_queryset(self, *args, **kwargs):
        queryset = super().get_queryset(*args, **kwargs)
        queryset = queryset.filter(id=self.kwargs.get('pk'))
        return queryset


class UpdateVisualView(LoggingMixin, LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """
    Добавить в БД визуальное представление выполненных работ
    """
    model = Visual
    form_class = VisualCreateNewForm
    permission_required = 'infoMFSS.change_visual'
    template_name = 'infoMFSS/visual_update_form.html'
    success_url = reverse_lazy('mfss:visual_list')
    extra_context = {
            'title': "Редактирование визуального представления выполненных работ",
    }

    def get_queryset(self, *args, **kwargs):
        queryset = super().get_queryset(*args, **kwargs)
        queryset = queryset.filter(id=self.kwargs.get('pk'))
        return queryset


class UpdateEquipmentInstallationView(LoggingMixin, LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """
    Изменить в БД места установки оборудования
    """
    model = EquipmentInstallation
    form_class = CreateEquipmentInstallationForm
    permission_required = 'infoMFSS.change_equipmentinstallation'
    template_name = 'infoMFSS/equipment_installation_update_form.html'
    success_url = reverse_lazy('mfss:equipment_installation_list')
    extra_context = {
            'title': "Редактирование мест установки оборудования",
    }

    def get_queryset(self, *args, **kwargs):
        queryset = super().get_queryset(*args, **kwargs)
        queryset = queryset.filter(id=self.kwargs.get('pk'))
        return queryset


class UpdateExecutionView(LoggingMixin, LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """
    Добавить в базу данных отчет о выполненных работах
    """
    model = Execution
    form_class = CreateExecutionForm
    permission_required = 'infoMFSS.change_execution'
    template_name = 'infoMFSS/execution_update_form.html'
    success_url = reverse_lazy('mfss:execution_list')
    extra_context = {
            'title': "Редактировать отчет о выполненных работах",
    }

    def get_queryset(self, *args, **kwargs):
        queryset = super().get_queryset(*args, **kwargs)
        queryset = queryset.filter(id=self.kwargs.get('pk'))
        return queryset


"""Удаление данных в БД для модераторов"""


class DeleteEquipmentView(LoggingMixin, LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """
    Изменить оборудование в БД
    """
    model = Equipment
    permission_required = 'infoMFSS.delete_equipment'
    success_url = reverse_lazy('mfss:equipment_list')


class DeleteCableView(LoggingMixin, LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """
    Изменить в БД кабельную продукцию
    """
    model = Cable
    permission_required = 'infoMFSS.delete_cable'
    success_url = reverse_lazy('mfss:cable_list')


class DeletePointPhoneView(LoggingMixin, LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """
    Изменить в БД точку телефонной связи
    """
    model = PointPhone
    permission_required = 'infoMFSS.delete_pointphone'
    success_url = reverse_lazy('mfss:point_phone_list')


class DeleteBranchesBoxView(LoggingMixin, LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """
    Изменить в БД распределительные коробки
    """
    model = BranchesBox
    permission_required = 'infoMFSS.delete_branchesbox'
    success_url = reverse_lazy('mfss:branches_box_list')


class DeleteCableMagazineView(LoggingMixin, LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """
    Изменить в БД значения в кабельном журнале
    """
    model = CableMagazine
    permission_required = 'infoMFSS.delete_cablemagazine'
    success_url = reverse_lazy('mfss:cable_magazine_list')


class DeleteViolationsView(LoggingMixin, LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """
    Изменить в БД нарушения
    """
    model = Violations
    permission_required = 'infoMFSS.delete_violations'
    success_url = reverse_lazy('mfss:violations_list')


class DeleteVisualView(LoggingMixin, LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """
    Добавить в БД визуальное представление выполненных работ
    """
    model = Visual
    permission_required = 'infoMFSS.delete_visual'
    success_url = reverse_lazy('mfss:visual_list')


class DeleteEquipmentInstallationView(LoggingMixin, LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """
    Изменить в БД места установки оборудования
    """
    model = EquipmentInstallation
    permission_required = 'infoMFSS.delete_equipmentinstallation'
    success_url = reverse_lazy('mfss:equipment_installation_list')


class DeleteExecutionView(LoggingMixin, LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """
    Добавить в базу данных отчет о выполненных работах
    """
    model = Execution
    permission_required = 'infoMFSS.delete_execution'
    success_url = reverse_lazy('mfss:execution_list')