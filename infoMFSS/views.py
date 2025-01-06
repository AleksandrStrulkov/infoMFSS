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

from infoMFSS.filters import MineSabInclFilter
# from mailings.forms import MessageForm, ClientForm, MailingForm, MailingManagerForm, MailingOptionsForm, UserActiveForm
from infoMFSS.models import Execution, DateUpdate, NumberMine, Subsystem, InclinedBlocks, PointPhone, BranchesBox, \
    Equipment, Cable, Violations, Visual, EquipmentInstallation, CableMagazine
from infoMFSS.forms import PercentForm, EquipmentForm, CableForm, BoxForm, VisualCreateForm
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


class MFSSTemplateView(TemplateView):
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

    # for obj in number_mines_object:
    #     number_mines_list.append(obj.title)
    # number_mines_list.remove('Все шахты')

    # for obj in subsystems_object:
    #     subsystems_list.append(obj.title)
    # subsystems_list.remove('Все подсистемы')

    # for obj in incl_blocks_object:
    #     incl_blocks_list.append(obj.title)
    # incl_blocks_list.remove('Все уклонные блоки')

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


# class EquipmentListView(FormMixin, ListView):
#     model = Execution
#     form_class = SubsystemForm
#     template_name = 'mfss/equipment_list.html'
#     context_object_name = "equipment"
#     extra_context = {
#             'title': "Просмотр установленного оборудования",
#     }


class FormListView(FormMixin, ListView):
    result = 0

    def get(self, request, *args, **kwargs):
        # From ProcessFormMixin
        form_class = self.get_form_class()
        self.form = self.get_form(form_class)

        # From BaseListView
        self.object_list = self.get_queryset()
        allow_empty = self.get_allow_empty()
        if not allow_empty and len(self.object_list) == 0:
            raise Http404(
                    u"Empty list and '%(class_name)s.allow_empty' is False."
                    % {'class_name': self.__class__.__name__}
            )

        context = self.get_context_data(object_list=self.object_list, form=self.form)
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['mine'] = self.request.GET.get('number_mines')
        context['subsystem'] = self.request.GET.get('subsystems')
        context['incl_blocks'] = self.request.GET.get('incl_blocks')
        context['equipment'] = self.request.GET.get('equipment')
        context['cable'] = self.request.GET.get('cable')
        context['new'] = self.object_list
        context['result'] = self.result
        context['bool'] = Execution.objects.all()
        # context['phone_number'] = PointPhone.objects.all()
        return context


class EquipmentListView(FormListView):
    form_class = EquipmentForm
    model = Execution
    template_name = 'mfss/equipment_list.html'
    extra_context = {
            'title': "Просмотр установленного оборудования",
    }

    def get_queryset(self):
        mine = self.request.GET.get('number_mines')
        subsystem = self.request.GET.get('subsystems')
        incl_blocks = self.request.GET.get('incl_blocks')
        equipment = self.request.GET.get('equipment')

        if mine == 'Все шахты' and subsystem == 'Все подсистемы' and incl_blocks == 'Все уклонные блоки' and \
                equipment == 'Все оборудование':
            self.result = 1
            object_list = Execution.objects.filter(execution_bool=True)
            return object_list

        elif mine == 'Все шахты' and subsystem and incl_blocks == 'Все уклонные блоки' and \
                equipment == 'Все оборудование':
            self.result = 2
            object_list = Execution.objects.filter(
                    equipment_install__subsystem__title=subsystem,
                    execution_bool=True
            )
            return object_list
        elif mine and subsystem == 'Все подсистемы' and incl_blocks == 'Все уклонные блоки' and \
                equipment == 'Все оборудование':
            self.result = 3
            object_list = Execution.objects.filter(
                    equipment_install__number_mine__title=mine,
                    execution_bool=True
            )
            return object_list
        elif mine and subsystem and incl_blocks == 'Все уклонные блоки' and \
                equipment == 'Все оборудование':
            self.result = 4
            object_list = Execution.objects.filter(
                    equipment_install__number_mine__title=mine,
                    equipment_install__subsystem__title=subsystem,
                    execution_bool=True
            )
            return object_list
        elif mine and subsystem == 'Все подсистемы' and incl_blocks and \
                equipment == 'Все оборудование':
            self.result = 5
            object_list = Execution.objects.filter(
                    equipment_install__number_mine__title=mine,
                    equipment_install__inclined_blocks__title=incl_blocks,
                    execution_bool=True
            )
            return object_list
        elif mine == 'Все шахты' and subsystem == 'Все подсистемы' and incl_blocks == 'Все уклонные блоки' and \
                equipment:
            self.result = 6
            object_list = Execution.objects.filter(equipment_install__title__title=equipment, execution_bool=True)
            return object_list

        elif mine and subsystem == 'Все подсистемы' and incl_blocks == 'Все уклонные блоки' and \
                equipment:
            self.result = 7
            object_list = Execution.objects.filter(
                    equipment_install__number_mine__title=mine,
                    equipment_install__title__title=equipment, execution_bool=True
            )
            return object_list
        elif mine and subsystem and incl_blocks == 'Все уклонные блоки' and equipment:
            self.result = 8
            object_list = Execution.objects.filter(
                    equipment_install__number_mine__title=mine,
                    equipment_install__subsystem__title=subsystem,
                    equipment_install__title__title=equipment,
                    execution_bool=True
            )
            return object_list
        elif mine and subsystem and incl_blocks and equipment:
            self.result = 9
            object_list = Execution.objects.filter(
                    equipment_install__number_mine__title=mine,
                    equipment_install__subsystem__title=subsystem,
                    equipment_install__inclined_blocks__title=incl_blocks,
                    equipment_install__title__title=equipment,
                    execution_bool=True
            )
            return object_list


class CableListView(FormListView):
    form_class = CableForm
    model = Execution
    template_name = 'mfss/cable_list.html'
    extra_context = {
            'title': "Просмотр проложенных трасс кабелей",
    }

    def get_queryset(self):
        mine = self.request.GET.get('number_mines')
        subsystem = self.request.GET.get('subsystems')
        incl_blocks = self.request.GET.get('incl_blocks')
        cable = self.request.GET.get('cable')

        if mine == 'Все шахты' and subsystem == 'Все подсистемы' and incl_blocks == 'Все уклонные блоки' and \
                cable == 'Все кабели':
            self.result = 1
            object_list = Execution.objects.filter(execution_bool=True)
            return object_list

        elif mine == 'Все шахты' and subsystem and incl_blocks == 'Все уклонные блоки' and \
                cable == 'Все кабели':
            self.result = 2
            object_list = Execution.objects.filter(
                    cable_magazine__subsystem__title=subsystem,
                    execution_bool=True
            )
            return object_list
        elif mine and subsystem == 'Все подсистемы' and incl_blocks == 'Все уклонные блоки' and \
                cable == 'Все кабели':
            self.result = 3
            object_list = Execution.objects.filter(
                    cable_magazine__number_mine__title=mine,
                    execution_bool=True
            )
            return object_list
        elif mine and subsystem and incl_blocks == 'Все уклонные блоки' and \
                cable == 'Все кабели':
            self.result = 4
            object_list = Execution.objects.filter(
                    cable_magazine__number_mine__title=mine,
                    cable_magazine__subsystem__title=subsystem,
                    execution_bool=True
            )
            return object_list
        elif mine and subsystem == 'Все подсистемы' and incl_blocks and \
                cable == 'Все кабели':
            self.result = 5
            object_list = Execution.objects.filter(
                    cable_magazine__number_mine__title=mine,
                    cable_magazine__inclined_blocks__title=incl_blocks,
                    execution_bool=True
            )
            return object_list
        elif mine == 'Все шахты' and subsystem == 'Все подсистемы' and incl_blocks == 'Все уклонные блоки' and \
                cable:
            self.result = 6
            object_list = Execution.objects.filter(cable_magazine__cable__title=cable, execution_bool=True)
            return object_list

        elif mine and subsystem == 'Все подсистемы' and incl_blocks == 'Все уклонные блоки' and \
                cable:
            self.result = 7
            object_list = Execution.objects.filter(
                    cable_magazine__number_mine__title=mine,
                    cable_magazine__cable__title=cable, execution_bool=True
            )
            return object_list
        elif mine and subsystem and incl_blocks == 'Все уклонные блоки' and cable:
            self.result = 8
            object_list = Execution.objects.filter(
                    cable_magazine__number_mine__title=mine,
                    cable_magazine__subsystem__title=subsystem,
                    cable_magazine__cable__title=cable,
                    execution_bool=True
            )
            return object_list

        elif mine and subsystem and incl_blocks and cable:
            self.result = 9
            object_list = Execution.objects.filter(
                    cable_magazine__number_mine__title=mine,
                    cable_magazine__subsystem__title=subsystem,
                    cable_magazine__inclined_blocks__title=incl_blocks,
                    cable_magazine__cable__title=cable,
                    execution_bool=True
            )
            return object_list


class BoxListView(FormListView):
    form_class = BoxForm
    model = BranchesBox
    template_name = 'mfss/box_list.html'
    extra_context = {
            'title': "Просмотр подключенных устройств",
    }

    def get_queryset(self):
        mine = self.request.GET.get('number_mines')
        subsystem = self.request.GET.get('subsystems')
        incl_blocks = self.request.GET.get('incl_blocks')

        if mine == 'Все шахты' and subsystem == 'Все подсистемы' and incl_blocks == 'Все уклонные блоки':
            self.result = 1
            object_list = BranchesBox.objects.all()
            return object_list

        elif mine == 'Все шахты' and subsystem and incl_blocks == 'Все уклонные блоки':
            self.result = 2
            object_list = BranchesBox.objects.filter(
                    subsystem__title=subsystem,
            )
            return object_list
        elif mine and subsystem == 'Все подсистемы' and incl_blocks == 'Все уклонные блоки':
            self.result = 3
            object_list = BranchesBox.objects.filter(
                    number_mine__title=mine,
            )
            return object_list
        elif mine and subsystem and incl_blocks == 'Все уклонные блоки':
            self.result = 4
            object_list = BranchesBox.objects.filter(
                    number_mine__title=mine,
                    subsystem__title=subsystem,
            )
            return object_list
        elif mine and subsystem == 'Все подсистемы' and incl_blocks:
            self.result = 5
            object_list = BranchesBox.objects.filter(
                    number_mine__title=mine,
                    inclined_blocks__title=incl_blocks,
            )
            return object_list
        elif mine and subsystem and incl_blocks:
            self.result = 9
            object_list = BranchesBox.objects.filter(
                    number_mine__title=mine,
                    subsystem__title=subsystem,
                    inclined_blocks__title=incl_blocks,
            )
            return object_list


class EquipmentFileListView(ListView):
    model = Equipment
    template_name = 'mfss/equipment_file_list.html'
    extra_context = {
            'title': "Документация (оборудование)",
    }


class CableFileListView(ListView):
    model = Cable
    template_name = 'mfss/cable_file_list.html'
    extra_context = {
            'title': "Документация (кабели)",
    }


class ViolationsListView(ListView):
    model = Violations
    template_name = 'mfss/violations_list.html'
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


class VisualListView(FormListView):
    model = Visual
    form_class = VisualCreateForm
    template_name = 'mfss/visual_list.html'
    extra_context = {
            'title': "Визуализация установленного оборудования",
    }

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        mine = self.request.GET.get('number_mines')
        equipment = self.request.GET.get('equipment')

        objects = Visual.objects.filter(
            number_mines=mine,
            equipment=equipment,
            )

        for object_ in objects:
            context['pdf_visual'] = object_.file_pdf

        return context


class ProjectEquipmentListView(ListView):
    model = EquipmentInstallation
    template_name = 'mfss/project_equipment_list.html'
    extra_context = {
            'title': "Проект МФСБ",
    }


class ProjectCableListView(ListView):
    model = CableMagazine
    template_name = 'mfss/project_cable_list.html'
    extra_context = {
            'title': "Проект МФСБ",
    }