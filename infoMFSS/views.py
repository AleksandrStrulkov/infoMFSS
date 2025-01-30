from django.core.mail import send_mail
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.core.cache import cache
from django.urls import reverse_lazy
from django.utils import dateformat
from django.conf import settings
from datetime import datetime
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView, FormView
from django.http import Http404
# from django.utils.translation import ugettext as _
from django.shortcuts import redirect
from django.views.generic.edit import FormMixin
from django.urls import reverse

from infoMFSS.filters import MineSabInclFilter
# from mailings.forms import MessageForm, ClientForm, MailingForm, MailingManagerForm, MailingOptionsForm, UserActiveForm
from infoMFSS.models import Execution, DateUpdate, NumberMine, Subsystem, InclinedBlocks, PointPhone, BranchesBox, \
    Equipment, Cable, Violations, Visual, EquipmentInstallation, CableMagazine
from infoMFSS.forms import PercentForm, EquipmentForm, CableForm, BoxForm, VisualCreateForm, ProjectEquipmentForm, \
    ProjectCableForm, ContactForm
from django.shortcuts import render
from users.models import User
import random
from django.core.cache import cache
from django.conf import settings
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin, \
    PermissionRequiredMixin


# from .forms import UserForm


def sass_page_handler(request):
    return render(request, 'mfss/base.html')


class MFSSPercentTemplateView(TemplateView):
    template_name = 'mfss/home.html'
    extra_context = {
            'title': "МФСС",
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        """Контекст для нефтешахты №1"""
        mine1_count_eq = Execution.objects.filter(equipment_install__number_mine__title="Нефтешахта №1").count()
        mine1_count_cab = Execution.objects.filter(cable_magazine__number_mine__title="Нефтешахта №1").count()
        update = DateUpdate.objects.latest('update')
        mine1_count = mine1_count_eq + mine1_count_cab
        mine1_count_true_eg = Execution.objects.filter(
                equipment_install__number_mine__title="Нефтешахта №1",
                execution_bool=True
        ).count()
        mine1_count_true_cab = Execution.objects.filter(
                cable_magazine__number_mine__title="Нефтешахта №1",
                execution_bool=True
        ).count()
        mine1_count_true = mine1_count_true_eg + mine1_count_true_cab
        try:
            mine1_count_percent = int(mine1_count_true * 100 / mine1_count)
        except ZeroDivisionError:
            mine1_count_percent = 0
        context['percent_mine1'] = mine1_count_percent
        context['update'] = update

        """Контекст для нефтешахты №2"""
        mine2_count_eq = Execution.objects.filter(equipment_install__number_mine__title="Нефтешахта №2").count()
        mine2_count_cab = Execution.objects.filter(cable_magazine__number_mine__title="Нефтешахта №2").count()
        mine2_count = mine2_count_eq + mine2_count_cab
        mine2_count_true_eq = Execution.objects.filter(
                equipment_install__number_mine__title="Нефтешахта №2",
                execution_bool=True
        ).count()
        mine2_count_true_cab = Execution.objects.filter(
                cable_magazine__number_mine__title="Нефтешахта №2",
                execution_bool=True
        ).count()
        mine2_count_true = mine2_count_true_eq + mine2_count_true_cab
        try:
            mine2_count_percent = int(mine2_count_true * 100 / mine2_count)
        except ZeroDivisionError:
            mine2_count_percent = 0
        context['percent_mine2'] = mine2_count_percent

        """Контекст для нефтешахты №3"""
        mine3_count_eq = Execution.objects.filter(equipment_install__number_mine__title="Нефтешахта №3").count()
        mine3_count_cab = Execution.objects.filter(cable_magazine__number_mine__title="Нефтешахта №3").count()
        mine3_count = mine3_count_eq + mine3_count_cab
        mine3_count_true_eq = Execution.objects.filter(
                equipment_install__number_mine__title="Нефтешахта №3",
                execution_bool=True
        ).count()
        mine3_count_true_cab = Execution.objects.filter(
                cable_magazine__number_mine__title="Нефтешахта №3",
                execution_bool=True
        ).count()
        mine3_count_true = mine3_count_true_eq + mine3_count_true_cab
        try:
            mine3_count_percent = int(mine3_count_true * 100 / mine3_count)
        except ZeroDivisionError:
            mine3_count_percent = 0
        context['percent_mine3'] = mine3_count_percent

        """Контекст для всех шахт"""

        mine123_count_false = Execution.objects.filter(execution_bool=False).count()
        mine123_count_true = Execution.objects.filter(execution_bool=True).count()
        mine123_count = Execution.objects.all().count()

        try:
            mine123_count_percent = int(mine123_count_true * 100 / mine123_count)
        except ZeroDivisionError:
            mine123_count_percent = 0
        context['percent_mine123'] = mine123_count_percent

        return context


def percent_view(request):
    mine = ''
    subsystem = ''
    incl_blocks = ''
    percent = ''
    update = ''
    mine_count = 0
    mine_count_true = 0
    # number_mines_object = NumberMine.objects.all()
    # subsystems_object = Subsystem.objects.all()
    # incl_blocks_object = InclinedBlocks.objects.all()
    number_mines_list = [obj.title for obj in NumberMine.objects.exclude(title='Все шахты')]
    subsystems_list = [obj.title for obj in Subsystem.objects.exclude(title='Все подсистемы')]
    incl_blocks_list = [obj.title for obj in InclinedBlocks.objects.exclude(title='Все уклонные блоки')]
    mine_count_eq = 50000
    mine_all = []

    if request.method == 'POST':
        form = PercentForm(request.POST or None)
        if form.is_valid():
            mine = form.cleaned_data.get("number_mines").title
            subsystem = form.cleaned_data.get("subsystems").title
            incl_blocks = form.cleaned_data.get("incl_blocks").title

            # """False-False-False"""
            if mine == 'Все шахты' and subsystem == 'Все подсистемы' and incl_blocks == 'Все уклонные блоки':
                mine_count = Execution.objects.all().count()
                mine_count_true = Execution.objects.filter(execution_bool=True).count()
                try:
                    percent = int(mine_count_true * 100 / mine_count)
                except ZeroDivisionError:
                    percent = 0

            # """False-True-False"""
            elif mine == 'Все шахты' and subsystem in subsystems_list and incl_blocks == 'Все уклонные блоки':
                mine_count_eq = Execution.objects.filter(equipment_install__subsystem__title=subsystem).count()
                mine_count_cab = Execution.objects.filter(cable_magazine__subsystem__title=subsystem).count()
                mine_count = mine_count_eq + mine_count_cab
                mine_count_eq_true = Execution.objects.filter(
                        equipment_install__subsystem__title=subsystem,
                        execution_bool=True
                ).count()
                mine_count_cab_true = Execution.objects.filter(
                        cable_magazine__subsystem__title=subsystem,
                        execution_bool=True
                ).count()
                mine_count_true = mine_count_eq_true + mine_count_cab_true
                try:
                    percent = int(mine_count_true * 100 / mine_count)
                except ZeroDivisionError:
                    percent = 0

            # """True-False-False"""
            elif mine in number_mines_list and subsystem == 'Все подсистемы' and \
                    incl_blocks == 'Все уклонные блоки':
                mine_count_eq = Execution.objects.filter(equipment_install__number_mine__title=mine).count()
                # mine_all = Execution.objects.(equipment_install__number_mine__title=mine).count()
                mine_count_cab = Execution.objects.filter(cable_magazine__number_mine__title__contains=mine).count()
                mine_count = mine_count_eq + mine_count_cab
                mine_count_eq_true = Execution.objects.filter(
                        equipment_install__number_mine__title__contains=mine,
                        execution_bool=True
                ).count()
                mine_count_cab_true = Execution.objects.filter(
                        cable_magazine__number_mine__title__contains=mine,
                        execution_bool=True
                ).count()
                mine_count_true = mine_count_eq_true + mine_count_cab_true
                try:
                    percent = int(mine_count_true * 100 / mine_count)
                except ZeroDivisionError:
                    percent = 0

            # """True-True-False"""
            elif mine in number_mines_list and subsystem in subsystems_list and incl_blocks == 'Все уклонные блоки':
                mine_count_eq = Execution.objects.filter(
                        equipment_install__number_mine__title=mine,
                        equipment_install__subsystem__title=subsystem
                ).count()
                mine_count_cab = Execution.objects.filter(
                        cable_magazine__number_mine__title=mine,
                        cable_magazine__subsystem__title=subsystem
                ).count()
                mine_count = mine_count_eq + mine_count_cab
                mine_count_eq_true = Execution.objects.filter(
                        equipment_install__number_mine__title=mine,
                        equipment_install__subsystem__title=subsystem,
                        execution_bool=True
                ).count()
                mine_count_cab_true = Execution.objects.filter(
                        cable_magazine__number_mine__title=mine,
                        cable_magazine__subsystem__title=subsystem,
                        execution_bool=True
                ).count()
                mine_count_true = mine_count_eq_true + mine_count_cab_true
                try:
                    percent = int(mine_count_true * 100 / mine_count)
                except ZeroDivisionError:
                    percent = 0

            # """True-True-True"""
            elif mine in number_mines_list and subsystem in subsystems_list and incl_blocks in incl_blocks_list:
                mine_count_eq = Execution.objects.filter(
                        equipment_install__number_mine__title=mine,
                        equipment_install__subsystem__title=subsystem,
                        equipment_install__inclined_blocks__title=incl_blocks
                ).count()
                mine_count_cab = Execution.objects.filter(
                        cable_magazine__number_mine__title=mine,
                        cable_magazine__subsystem__title=subsystem,
                        cable_magazine__inclined_blocks__title=incl_blocks
                ).count()
                mine_count = mine_count_eq + mine_count_cab
                mine_count_eq_true = Execution.objects.filter(
                        equipment_install__number_mine__title=mine,
                        equipment_install__subsystem__title=subsystem,
                        equipment_install__inclined_blocks__title=incl_blocks,
                        execution_bool=True
                ).count()
                mine_count_cab_true = Execution.objects.filter(
                        cable_magazine__number_mine__title=mine,
                        cable_magazine__subsystem__title=subsystem,
                        cable_magazine__inclined_blocks__title=incl_blocks,
                        execution_bool=True
                ).count()
                mine_count_true = mine_count_eq_true + mine_count_cab_true
                try:
                    percent = int(mine_count_true * 100 / mine_count)
                except ZeroDivisionError:
                    percent = 0

            # """True-False-True"""
            elif mine in number_mines_list and subsystem == 'Все подсистемы' and incl_blocks in incl_blocks_list:
                mine_count_eq = Execution.objects.filter(
                        equipment_install__number_mine__title=mine,
                        equipment_install__inclined_blocks__title=incl_blocks
                ).count()
                mine_count_cab = Execution.objects.filter(
                        cable_magazine__number_mine__title=mine,
                        cable_magazine__inclined_blocks__title=incl_blocks
                ).count()
                mine_count = mine_count_eq + mine_count_cab
                mine_count_eq_true = Execution.objects.filter(
                        equipment_install__number_mine__title=mine,
                        equipment_install__inclined_blocks__title=incl_blocks,
                        execution_bool=True
                ).count()
                mine_count_cab_true = Execution.objects.filter(
                        cable_magazine__number_mine__title=mine,
                        cable_magazine__inclined_blocks__title=incl_blocks,
                        execution_bool=True
                ).count()
                mine_count_true = mine_count_eq_true + mine_count_cab_true
                try:
                    percent = int(mine_count_true * 100 / mine_count)
                except ZeroDivisionError:
                    percent = 0

            update = DateUpdate.objects.latest('update')
            data = [mine, subsystem, incl_blocks, mine_count, mine_count_true,
                    number_mines_list, mine_count_eq, mine_all]
            context = {'form': form,
                       'mine': mine,
                       'subsystem': subsystem,
                       'incl_blocks': incl_blocks,
                       'percent': percent,
                       'update': update,
                       'data': data,
                       }

            return render(request, 'mfss/percents.html', context)

    else:
        form = PercentForm()
    context = {'form': form}
    return render(request, 'mfss/percents.html', context)


# class FormListViewMixin(FormMixin, ListView):
#     """Подготавливаем миксин для сохранения в гет запросе значений полей из формы"""
#
#     result = 0
#
#     def get(self, request, *args, **kwargs):
#         # From ProcessFormMixin
#         form_class = self.get_form_class()
#         self.form = self.get_form(form_class)
#
#         # From BaseListView
#         self.object_list = self.get_queryset()
#         allow_empty = self.get_allow_empty()
#         if not allow_empty and len(self.object_list) == 0:
#             raise Http404(
#                     u"Empty list and '%(class_name)s.allow_empty' is False."
#                     % {'class_name': self.__class__.__name__}
#             )
#
#         context = self.get_context_data(object_list=self.object_list, form=self.form)
#         return self.render_to_response(context)
#
#     def post(self, request, *args, **kwargs):
#         return self.get(request, *args, **kwargs)
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['mine'] = self.request.GET.get('number_mines')
#         context['subsystem'] = self.request.GET.get('subsystems')
#         context['incl_blocks'] = self.request.GET.get('incl_blocks')
#         context['equipment'] = self.request.GET.get('equipment')
#         context['cable'] = self.request.GET.get('cable')
#         context['new'] = self.object_list
#         context['result'] = self.result
#         context['bool'] = Execution.objects.all()
#         # context['phone_number'] = PointPhone.objects.all()
#         return context
#
#     def get_queryset(self):
#         queryset = super().get_queryset()
#         mine = self.request.GET.get('number_mines')
#         subsystem = self.request.GET.get('subsystems')
#
#         if mine == 'Все шахты' and subsystem == 'Все подсистемы':
#             self.result = 1
#             object_list = queryset.all().order_by('number_mine__title')
#             return object_list
#
#         elif mine == 'Все шахты' and subsystem:
#             self.result = 2
#             object_list = queryset.filter(
#                     subsystem__title=subsystem,
#             )
#             return object_list
#
#         elif mine and subsystem == 'Все подсистемы':
#             self.result = 3
#             object_list = queryset.filter(
#                     number_mine__title=mine,
#             )
#             return object_list
#
#         elif mine and subsystem:
#             self.result = 4
#             object_list = queryset.filter(
#                     number_mine__title=mine,
#                     subsystem__title=subsystem,
#             )
#             return object_list


class EquipmentListView(FormView):
    form_class = EquipmentForm
    model = Execution
    template_name = 'mfss/equipment_list.html'
    context_object_name = 'equipment_list'
    success_url = reverse_lazy('mfss:equipment')
    extra_context = {
            'title': "Просмотр установленного оборудования",
    }
    result = 0

    def post(self, request, *args, **kwargs):
        print("POST-запрос получен")
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        """
        Метод вызывается, если форма прошла валидацию.
        """
        # Получаем данные из формы
        mine = form.cleaned_data.get('number_mines', )
        subsystem = form.cleaned_data.get('subsystems', )
        incl_blocks = form.cleaned_data.get('incl_blocks', )
        equipment = form.cleaned_data.get('equipment', )
        print("Данные из формы получены:", mine, subsystem, incl_blocks, equipment)

        query_params = {
                'mine': mine,
                'subsystem': subsystem,
                'incl_blocks': incl_blocks,
                'equipment': equipment,
        }

        url = f"{reverse('mfss:equipment')}?{'&'.join(f'{key}={value}' for key, value in query_params.items())}"

        return HttpResponseRedirect(url)

    def form_invalid(self, form):
        print("Форма не прошла валидацию")
        print(form.errors)  # Вывод ошибок формы
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        """
        Метод для добавления дополнительного контекста в шаблон.
        Здесь выполняется фильтрация данных из базы.
        """
        context = super().get_context_data(**kwargs)

        # Получаем параметры из GET-запроса
        mine = self.request.GET.get('mine', )
        subsystem = self.request.GET.get('subsystem', )
        incl_blocks = self.request.GET.get('incl_blocks', )
        equipment = self.request.GET.get('equipment', )

        equipment_list = None

        if mine == 'Все шахты' and subsystem == 'Все подсистемы' and incl_blocks == 'Все уклонные блоки' and \
                equipment == 'Все оборудование':
            self.result = 1
            equipment_list = Execution.objects.filter(execution_bool=True).order_by(
                    'equipment_install__number_mine__title'
            )

        elif mine == 'Все шахты' and subsystem and incl_blocks == 'Все уклонные блоки' and \
                equipment == 'Все оборудование':
            self.result = 2
            equipment_list = Execution.objects.filter(
                    equipment_install__subsystem__title=subsystem,
                    execution_bool=True
            )

        elif mine and subsystem == 'Все подсистемы' and incl_blocks == 'Все уклонные блоки' and \
                equipment == 'Все оборудование':
            self.result = 3
            equipment_list = Execution.objects.filter(
                    equipment_install__number_mine__title=mine,
                    execution_bool=True
            )

        elif mine and subsystem and incl_blocks == 'Все уклонные блоки' and \
                equipment == 'Все оборудование':
            self.result = 4
            equipment_list = Execution.objects.filter(
                    equipment_install__number_mine__title=mine,
                    equipment_install__subsystem__title=subsystem,
                    execution_bool=True
            )

        elif mine and subsystem == 'Все подсистемы' and incl_blocks and \
                equipment == 'Все оборудование':
            self.result = 5
            equipment_list = Execution.objects.filter(
                    equipment_install__number_mine__title=mine,
                    equipment_install__inclined_blocks__title=incl_blocks,
                    execution_bool=True
            )

        elif mine == 'Все шахты' and subsystem == 'Все подсистемы' and incl_blocks == 'Все уклонные блоки' and \
                equipment:
            self.result = 6
            equipment_list = Execution.objects.filter(equipment_install__title__title=equipment, execution_bool=True)

        elif mine and subsystem == 'Все подсистемы' and incl_blocks == 'Все уклонные блоки' and \
                equipment:
            self.result = 7
            equipment_list = Execution.objects.filter(
                    equipment_install__number_mine__title=mine,
                    equipment_install__title__title=equipment,
                    execution_bool=True
            )

        elif mine and subsystem and incl_blocks == 'Все уклонные блоки' and equipment:
            self.result = 8
            equipment_list = Execution.objects.filter(
                    equipment_install__number_mine__title=mine,
                    equipment_install__subsystem__title=subsystem,
                    equipment_install__title__title=equipment,
                    execution_bool=True
            )

        elif mine and subsystem and incl_blocks and equipment:
            self.result = 9
            equipment_list = Execution.objects.filter(
                    equipment_install__number_mine__title=mine,
                    equipment_install__subsystem__title=subsystem,
                    equipment_install__inclined_blocks__title=incl_blocks,
                    equipment_install__title__title=equipment,
                    execution_bool=True
            )

        context['equipment_list'] = equipment_list
        context['mine'] = mine
        context['subsystem'] = subsystem
        context['incl_blocks'] = incl_blocks
        context['equipment'] = equipment
        context['result'] = self.result

        return context


class CableListView(FormView):
    form_class = CableForm
    model = Execution
    template_name = 'mfss/cable_list.html'
    context_object_name = 'cable_list'
    success_url = reverse_lazy('mfss:cable')
    extra_context = {
            'title': "Просмотр проложенных трасс кабелей",
    }
    result = 0

    def post(self, request, *args, **kwargs):
        print("POST-запрос получен")
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        """
        Метод вызывается, если форма прошла валидацию.
        """
        # Получаем данные из формы
        mine = form.cleaned_data.get('number_mines', )
        subsystem = form.cleaned_data.get('subsystems', )
        incl_blocks = form.cleaned_data.get('incl_blocks', )
        cable = form.cleaned_data.get('cable', )
        print("Данные из формы получены:", mine, subsystem, incl_blocks, cable)

        query_params = {
                'mine': mine,
                'subsystem': subsystem,
                'incl_blocks': incl_blocks,
                'cable': cable,
        }

        url = f"{reverse('mfss:cable')}?{'&'.join(f'{key}={value}' for key, value in query_params.items())}"

        return HttpResponseRedirect(url)

    def form_invalid(self, form):
        print("Форма не прошла валидацию")
        print(form.errors)  # Вывод ошибок формы
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        """
        Метод для добавления дополнительного контекста в шаблон.
        Здесь выполняется фильтрация данных из базы.
        """
        context = super().get_context_data(**kwargs)

        # Получаем параметры из GET-запроса
        mine = self.request.GET.get('mine', )
        subsystem = self.request.GET.get('subsystem', )
        incl_blocks = self.request.GET.get('incl_blocks', )
        cable = self.request.GET.get('cable', )

        cable_list = None

        if mine == 'Все шахты' and subsystem == 'Все подсистемы' and incl_blocks == 'Все уклонные блоки' and \
                cable == 'Все кабели':
            self.result = 1
            cable_list = Execution.objects.filter(execution_bool=True)

        elif mine == 'Все шахты' and subsystem and incl_blocks == 'Все уклонные блоки' and \
                cable == 'Все кабели':
            self.result = 2
            cable_list = Execution.objects.filter(
                    cable_magazine__subsystem__title=subsystem,
                    execution_bool=True
            )

        elif mine and subsystem == 'Все подсистемы' and incl_blocks == 'Все уклонные блоки' and \
                cable == 'Все кабели':
            self.result = 3
            cable_list = Execution.objects.filter(
                    cable_magazine__number_mine__title=mine,
                    execution_bool=True
            )

        elif mine and subsystem and incl_blocks == 'Все уклонные блоки' and \
                cable == 'Все кабели':
            self.result = 4
            cable_list = Execution.objects.filter(
                    cable_magazine__number_mine__title=mine,
                    cable_magazine__subsystem__title=subsystem,
                    execution_bool=True
            )

        elif mine and subsystem == 'Все подсистемы' and incl_blocks and \
                cable == 'Все кабели':
            self.result = 5
            cable_list = Execution.objects.filter(
                    cable_magazine__number_mine__title=mine,
                    cable_magazine__inclined_blocks__title=incl_blocks,
                    execution_bool=True
            )

        elif mine == 'Все шахты' and subsystem == 'Все подсистемы' and incl_blocks == 'Все уклонные блоки' and \
                cable:
            self.result = 6
            cable_list = Execution.objects.filter(cable_magazine__cable__title=cable, execution_bool=True)

        elif mine and subsystem == 'Все подсистемы' and incl_blocks == 'Все уклонные блоки' and \
                cable:
            self.result = 7
            cable_list = Execution.objects.filter(
                    cable_magazine__number_mine__title=mine,
                    cable_magazine__cable__title=cable, execution_bool=True
            )

        elif mine and subsystem and incl_blocks == 'Все уклонные блоки' and cable:
            self.result = 8
            cable_list = Execution.objects.filter(
                    cable_magazine__number_mine__title=mine,
                    cable_magazine__subsystem__title=subsystem,
                    cable_magazine__cable__title=cable,
                    execution_bool=True
            )

        elif mine and subsystem and incl_blocks and cable:
            self.result = 9
            cable_list = Execution.objects.filter(
                    cable_magazine__number_mine__title=mine,
                    cable_magazine__subsystem__title=subsystem,
                    cable_magazine__inclined_blocks__title=incl_blocks,
                    cable_magazine__cable__title=cable,
                    execution_bool=True
            )

        context['cable_list'] = cable_list
        context['mine'] = mine
        context['subsystem'] = subsystem
        context['incl_blocks'] = incl_blocks
        context['cable'] = cable
        context['result'] = self.result

        return context


class BoxListView(FormView):
    form_class = BoxForm
    model = BranchesBox
    template_name = 'mfss/box_list.html'
    context_object_name = 'box_list'
    success_url = reverse_lazy('mfss:box')
    extra_context = {
            'title': "Просмотр подключенных устройств",
    }
    result = 0

    def post(self, request, *args, **kwargs):
        print("POST-запрос получен")
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        """
        Метод вызывается, если форма прошла валидацию.
        """
        # Получаем данные из формы
        mine = form.cleaned_data.get('number_mines', )
        subsystem = form.cleaned_data.get('subsystems', )
        incl_blocks = form.cleaned_data.get('incl_blocks', )
        print("Данные из формы получены:", mine, subsystem, incl_blocks)

        query_params = {
                'mine': mine,
                'subsystem': subsystem,
                'incl_blocks': incl_blocks,
        }

        url = f"{reverse('mfss:box')}?{'&'.join(f'{key}={value}' for key, value in query_params.items())}"

        return HttpResponseRedirect(url)

    def get_context_data(self, **kwargs):
        """
        Метод для добавления дополнительного контекста в шаблон.
        Здесь выполняется фильтрация данных из базы.
        """
        context = super().get_context_data(**kwargs)

        # Получаем параметры из GET-запроса
        mine = self.request.GET.get('mine', )
        subsystem = self.request.GET.get('subsystem', )
        incl_blocks = self.request.GET.get('incl_blocks', )

        box_list = None

        if mine == 'Все шахты' and subsystem == 'Все подсистемы' and incl_blocks == 'Все уклонные блоки':
            self.result = 1
            box_list = BranchesBox.objects.all()

        elif mine == 'Все шахты' and subsystem and incl_blocks == 'Все уклонные блоки':
            self.result = 2
            box_list = BranchesBox.objects.filter(
                    subsystem__title=subsystem,
            )

        elif mine and subsystem == 'Все подсистемы' and incl_blocks == 'Все уклонные блоки':
            self.result = 3
            box_list = BranchesBox.objects.filter(
                    number_mine__title=mine,
            )

        elif mine and subsystem and incl_blocks == 'Все уклонные блоки':
            self.result = 4
            box_list = BranchesBox.objects.filter(
                    number_mine__title=mine,
                    subsystem__title=subsystem,
            )

        elif mine and subsystem == 'Все подсистемы' and incl_blocks:
            self.result = 5
            box_list = BranchesBox.objects.filter(
                    number_mine__title=mine,
                    inclined_blocks__title=incl_blocks,
            )

        elif mine and subsystem and incl_blocks:
            self.result = 9
            box_list = BranchesBox.objects.filter(
                    number_mine__title=mine,
                    subsystem__title=subsystem,
                    inclined_blocks__title=incl_blocks,
            )

        context['box_list'] = box_list
        context['mine'] = mine
        context['subsystem'] = subsystem
        context['incl_blocks'] = incl_blocks
        context['result'] = self.result

        return context


class EquipmentFileListView(ListView):
    model = Equipment
    template_name = 'mfss/equipment_file_list.html'
    context_object_name = 'equipment_file_list'
    extra_context = {
            'title': "Документация (оборудование)",
    }


class CableFileListView(ListView):
    model = Cable
    template_name = 'mfss/cable_file_list.html'
    context_object_name = 'cable_file_list'
    extra_context = {
            'title': "Документация (кабели)",
    }


class ViolationsListView(ListView):
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
        # Получаем данные из формы
        mine = form.cleaned_data.get('number_mines', )
        equipment = form.cleaned_data.get('equipment', )
        print("Данные из формы получены:", mine, equipment, )

        query_params = {
                'mine': mine,
                'equipment': equipment,
        }

        url = f"{reverse('mfss:visual')}?{'&'.join(f'{key}={value}' for key, value in query_params.items())}"

        return HttpResponseRedirect(url)

    def get_context_data(self, *args, **kwargs):
        """
        Метод для добавления дополнительного контекста в шаблон.
        Здесь выполняется фильтрация данных из базы.
        """
        context = super().get_context_data(**kwargs)

        # Получаем параметры из GET-запроса
        mine = self.request.GET.get('mine')
        equipment = self.request.GET.get('equipment')

        visual_list = Visual.objects.filter(
                number_mines=mine,
                equipment=equipment,
        )

        context['mine'] = mine
        context['equipment'] = equipment

        for visual in visual_list:
            context['pdf_visual'] = visual.file_pdf
        print(context)
        return context


class ProjectEquipmentListView(FormView):
    model = EquipmentInstallation
    form_class = ProjectEquipmentForm
    template_name = 'mfss/project_equipment_list.html'
    context_object_name = 'project_equipment_list'
    success_url = reverse_lazy('mfss:project_equipment')
    extra_context = {
            'title': "Проект МФСБ (оборудование)",
    }

    def post(self, request, *args, **kwargs):
        print("POST-запрос получен")
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        """
        Метод вызывается, если форма прошла валидацию.
        """
        # Получаем данные из формы
        mine = form.cleaned_data.get('number_mines', )
        subsystem = form.cleaned_data.get('subsystems', )
        print("Данные из формы получены:", mine, subsystem)

        query_params = {
                'mine': mine,
                'subsystem': subsystem,
        }

        url = f"{reverse('mfss:project_equipment')}?{'&'.join(f'{key}={value}' for key, value in query_params.items())}"

        return HttpResponseRedirect(url)

    def get_context_data(self, *args, **kwargs):
        """
        Метод для добавления дополнительного контекста в шаблон.
        Здесь выполняется фильтрация данных из базы.
        """
        context = super().get_context_data(**kwargs)

        mine = self.request.GET.get('mine', )
        subsystem = self.request.GET.get('subsystem', )

        project_equipment_list = None

        if mine == 'Все шахты' and subsystem == 'Все подсистемы':
            project_equipment_list = EquipmentInstallation.objects.all().order_by('number_mine__title')

        elif mine == 'Все шахты' and subsystem:
            # self.result = 2
            project_equipment_list = EquipmentInstallation.objects.filter(
                    subsystem__title=subsystem,
            ).order_by('number_mine__title')

        elif mine and subsystem == 'Все подсистемы':
            # self.result = 3
            project_equipment_list = EquipmentInstallation.objects.filter(
                    number_mine__title=mine,
            )

        elif mine and subsystem:
            # self.result = 4
            project_equipment_list = EquipmentInstallation.objects.filter(
                    number_mine__title=mine,
                    subsystem__title=subsystem,
            )

        context['mine'] = mine
        context['subsystem'] = subsystem
        context['project_equipment_list'] = project_equipment_list

        return context


class ProjectCableListView(LoginRequiredMixin, FormView):
    model = CableMagazine
    form_class = ProjectCableForm
    template_name = 'mfss/project_cable_list.html'
    context_object_name = 'project_cable_list'
    success_url = reverse_lazy('mfss:project_cable')
    extra_context = {
            'title': "Проект МФСБ (кабельная продукция)",
    }

    def post(self, request, *args, **kwargs):
        print("POST-запрос получен")
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        """
        Метод вызывается, если форма прошла валидацию.
        """
        # Получаем данные из формы
        mine = form.cleaned_data.get('number_mines', )
        subsystem = form.cleaned_data.get('subsystems', )
        print("Данные из формы получены:", mine, subsystem)

        query_params = {
                'mine': mine,
                'subsystem': subsystem,
        }

        url = f"{reverse('mfss:project_cable')}?{'&'.join(f'{key}={value}' for key, value in query_params.items())}"

        return HttpResponseRedirect(url)

    def form_invalid(self, form):
        print("Форма не прошла валидацию")
        print(form.errors)  # Вывод ошибок формы
        return super().form_invalid(form)

    def get_context_data(self, *args, **kwargs):
        """
        Метод для добавления дополнительного контекста в шаблон.
        Здесь выполняется фильтрация данных из базы.
        """
        context = super().get_context_data(**kwargs)

        mine = self.request.GET.get('mine', )
        subsystem = self.request.GET.get('subsystem', )

        project_cable_list = None

        if mine == 'Все шахты' and subsystem == 'Все подсистемы':
            project_cable_list = CableMagazine.objects.all().order_by('number_mine__title')

        elif mine == 'Все шахты' and subsystem:
            # self.result = 2
            project_cable_list = CableMagazine.objects.filter(
                    subsystem__title=subsystem,
            ).order_by('number_mine__title')

        elif mine and subsystem == 'Все подсистемы':
            # self.result = 3
            project_cable_list = CableMagazine.objects.filter(
                    number_mine__title=mine,
            )

        elif mine and subsystem:
            # self.result = 4
            project_cable_list = CableMagazine.objects.filter(
                    number_mine__title=mine,
                    subsystem__title=subsystem,
            )

        context['mine'] = mine
        context['subsystem'] = subsystem
        context['project_cable_list'] = project_cable_list

        return context




class ContactFormView(LoginRequiredMixin, FormView):
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