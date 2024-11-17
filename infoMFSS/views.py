from django.shortcuts import render
from django.core.cache import cache
from django.urls import reverse_lazy
from django.utils import dateformat
from django.conf import settings
from datetime import datetime
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView, FormView
from django.shortcuts import redirect
# from mailings.forms import MessageForm, ClientForm, MailingForm, MailingManagerForm, MailingOptionsForm, UserActiveForm
from infoMFSS.models import Execution, DateUpdate, NumberMine, Subsystem, InclinedBlocks
from infoMFSS.forms import SubsystemForm
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
        update = update = DateUpdate.objects.latest('update')
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
        try:
            mine123_count_percent = int(mine123_count_true * 100 / mine123_count_false)
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
    number_mines_object = NumberMine.objects.all()
    subsystems_object = Subsystem.objects.all()
    incl_blocks_object = InclinedBlocks.objects.all()
    number_mines_list = []
    subsystems_list = []
    incl_blocks_list = []
    mine_count_eq = 50000
    mine_all = []

    for obj in number_mines_object:
        number_mines_list.append(obj.title)
    number_mines_list.remove('Все шахты')

    for obj in subsystems_object:
        subsystems_list.append(obj.title)
    subsystems_list.remove('Все подсистемы')

    for obj in incl_blocks_object:
        incl_blocks_list.append(obj.title)
    incl_blocks_list.remove('Все уклонные блоки')

    if request.method == 'POST':
        form = SubsystemForm(request.POST or None)
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
                mine_count_eq_true = Execution.objects.filter(equipment_install__subsystem__title=subsystem,
                                                                   execution_bool=True).count()
                mine_count_cab_true = Execution.objects.filter(cable_magazine__subsystem__title=subsystem,
                                                                    execution_bool=True).count()
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
                mine_count_eq_true = Execution.objects.filter(equipment_install__number_mine__title__contains=mine,
                                                              execution_bool=True).count()
                mine_count_cab_true = Execution.objects.filter(cable_magazine__number_mine__title__contains=mine,
                                                               execution_bool=True).count()
                mine_count_true = mine_count_eq_true + mine_count_cab_true
                try:
                    percent = int(mine_count_true * 100 / mine_count)
                except ZeroDivisionError:
                    percent = 0

            # """True-True-False"""
            elif mine in number_mines_list and subsystem in subsystems_list and incl_blocks == 'Все уклонные блоки':
                mine_count_eq = Execution.objects.filter(equipment_install__number_mine__title=mine,
                                                         equipment_install__subsystem__title=subsystem).count()
                mine_count_cab = Execution.objects.filter(cable_magazine__number_mine__title=mine,
                                                          cable_magazine__subsystem__title=subsystem).count()
                mine_count = mine_count_eq + mine_count_cab
                mine_count_eq_true = Execution.objects.filter(equipment_install__number_mine__title=mine,
                                                              equipment_install__subsystem__title=subsystem,
                                                              execution_bool=True).count()
                mine_count_cab_true = Execution.objects.filter(cable_magazine__number_mine__title=mine,
                                                               cable_magazine__subsystem__title=subsystem,
                                                               execution_bool=True).count()
                mine_count_true = mine_count_eq_true + mine_count_cab_true
                try:
                    percent = int(mine_count_true * 100 / mine_count)
                except ZeroDivisionError:
                    percent = 0

            # """True-True-True"""
            elif mine in number_mines_list and subsystem in subsystems_list and incl_blocks in incl_blocks_list:
                mine_count_eq = Execution.objects.filter(equipment_install__number_mine__title=mine,
                                                         equipment_install__subsystem__title=subsystem,
                                                         equipment_install__inclined_blocks__title=incl_blocks).count()
                mine_count_cab = Execution.objects.filter(cable_magazine__number_mine__title=mine,
                                                          cable_magazine__subsystem__title=subsystem,
                                                          cable_magazine__inclined_blocks__title=incl_blocks).count()
                mine_count = mine_count_eq + mine_count_cab
                mine_count_eq_true = Execution.objects.filter(equipment_install__number_mine__title=mine,
                                                              equipment_install__subsystem__title=subsystem,
                                                              equipment_install__inclined_blocks__title=incl_blocks,
                                                              execution_bool=True).count()
                mine_count_cab_true = Execution.objects.filter(cable_magazine__number_mine__title=mine,
                                                               cable_magazine__subsystem__title=subsystem,
                                                               cable_magazine__inclined_blocks__title=incl_blocks,
                                                               execution_bool=True).count()
                mine_count_true = mine_count_eq_true + mine_count_cab_true
                try:
                    percent = int(mine_count_true * 100 / mine_count)
                except ZeroDivisionError:
                    percent = 0

            # """True-False-True"""
            elif mine in number_mines_list and subsystem == 'Все подсистемы' and incl_blocks in incl_blocks_list:
                mine_count_eq = Execution.objects.filter(equipment_install__number_mine__title=mine,
                                                         equipment_install__inclined_blocks__title=incl_blocks).count()
                mine_count_cab = Execution.objects.filter(cable_magazine__number_mine__title=mine,
                                                          cable_magazine__inclined_blocks__title=incl_blocks).count()
                mine_count = mine_count_eq + mine_count_cab
                mine_count_eq_true = Execution.objects.filter(equipment_install__number_mine__title=mine,
                                                              equipment_install__inclined_blocks__title=incl_blocks,
                                                              execution_bool=True).count()
                mine_count_cab_true = Execution.objects.filter(cable_magazine__number_mine__title=mine,
                                                               cable_magazine__inclined_blocks__title=incl_blocks,
                                                               execution_bool=True).count()
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

            return render(request, 'mfss/subsystem_list.html', context)

    else:
        form = SubsystemForm()
    context = {'form': form}
    return render(request, 'mfss/subsystem_list.html', context)
