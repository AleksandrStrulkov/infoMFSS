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


# class SubsystemTemplateView(TemplateView):
#     template_name = 'mfss/subsystem_list.html'
#     extra_context = {
#             'title': "Подсистема",
#     }
#     form_class = SubsystemForm
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)


# class SubsystemListView(ListView):
#     model = Execution
#     template_name = 'mfss/subsystem_list.html'
#     context_object_name = 'execution_list'
#     form_class = SubsystemForm
#     percent = ''
# mine3_count = Execution.objects.filter(number_mine__title="Нефтешахта №3").count()


# def index(request):
#     submitbutton = request.POST.get("submit")
#
#     numbermine = ''
#     subsystem = ''
# # emailvalue = ''
#
#     form = UserForm(request.POST or None)
#     if form.is_valid():
#         numbermine = form.cleaned_data.get("number_mine")
#         subsystem = form.cleaned_data.get("sub_system")
#     # emailvalue = form.cleaned_data.get("email")
#
#     context = {'form': form, 'numbermine': numbermine,
#            'subsystem': subsystem, 'submitbutton': submitbutton}
#
#     return render(request, 'mfss/subsystem_list.html', context)


# def get_queryset(self):
#     queryset = super().get_queryset()
# form = self.form_class(self.request.GET)
#
# queryset_mine = queryset.filter(number_mine=self.kwargs.get('pk')).count()
# queryset_mine_bool = queryset.filter(number_mine=self.kwargs.get('pk'), execution_bool=True).count()
# queryset_subsystem = queryset.filter(subsystem=self.kwargs.get('pk')).count()
# queryset_subsystem_bool = queryset.filter(subsystem=self.kwargs.get('pk'), execution_bool=True).count()

# if form.is_valid():
#     number_mine = form.cleaned_data.get('number_mine')
#     subsystem = form.cleaned_data.get('subsystem')
#     if number_mine and subsystem:
#         queryset_mine = queryset.filter(number_mine=number_mine, subsystem=subsystem).count()
#         queryset_mine_bool = queryset.filter(number_mine=number_mine, subsystem=subsystem, execution_bool=True).count()
#         percent = int(queryset_mine_bool.count() * 100 / queryset_mine.count())
#
# context = {percent: percent}
#
# return context

# def get_queryset(self):
#     queryset = super().get_queryset()
#     queryset = queryset.all()
#     return queryset

# def index(request):
#     submit_button = request.POST.get("submit")
#
#     numbermine = ''
#     subsystem_ = ''
#
#     form = SubsystemForm(request.POST or None)
#     if form.is_valid():
#         numbermine = form.cleaned_data.get("number_mine")
#         subsystem_ = form.cleaned_data.get("subsystem")
#
#     context = {'form': form, 'number-mine': numbermine,
#                'subsystem_': subsystem_, 'submit_button': submit_button,}
#
#     return render(request, 'mfss/subsystem_list.html', context)

# class DataFormView(FormView):
#     form_class = SubsystemForm
#     template_name = 'mfss/subsystem_list.html'
#     success_url = reverse_lazy('mfss:subsystem')
#     extra_context = {
#             'title': 'Критерии выбора',
#     }
#     mine = ''
#     subsystem = ''
#     incl_blocks = ''
#     percent = ''
#     update = ''
#     mine_count = 0
#     mine_count_true = 0



    # def post(self, request):
    #     # cleaned_data = super(SubsystemForm).clean()
    #     cleaned_data = SubsystemForm(request.POST or None)
    #     # if form.is_valid():
    #     # self.mine = request.POST.get("number_mine")
    #
    #     self.subsystem = request.POST.get("subsystem")
    #     self.incl_blocks = request.POST.get("incl_blocks")
    #     if self.mine == 'Все шахты' and self.subsystem == 'Все подсистемы' and self.incl_blocks == 'Все уклонные блоки':
    #         mine_count = Execution.objects.all().count()
    #         mine_count_true = Execution.objects.filter(execution_bool=True).count()
    #         try:
    #             percent = int(mine_count_true * 100 / mine_count)
    #         except ZeroDivisionError:
    #             percent = 0
    #     return self.post(request)
    #
    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     update = DateUpdate.objects.latest('update')
    #     context['percent'] = self.percent
    #     context['update'] = update
    #     context['data'] = [self.mine, self.subsystem, self.incl_blocks]
    #
    #     return context






# def get_context_data(self, **kwargs):
#     context = super().get_context_data(**kwargs)
#     if 'number_mines' in self.kwargs:
# number_mines = self.kwargs['number_mines']
# subsystems = self.kwargs['subsystems']
# incl_blocks = self.kwargs['incl_blocks']
#     mine = form.cleaned_data.get("number_mines")
#     number_mines = self.kwargs['number_mines']
#     context['data'] = Execution.objects.filter(equipment_install__number_mine__title=number_mines).count()
# context['incl_blocks'] = self.kwargs['incl_blocks']
# context['data'] = [context['number_mines'], context['subsystems'], context['incl_blocks']]
# return context

# def form_valid(self, form):
#     mine = form.cleaned_data.get("number_mines")
#
#
#     return super().form_valid(form)


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

    # elif mine == 'Все шахты' and subsystem in subsystems_list and incl_blocks == 'Все уклонные блоки':
    #     mine_count_eq = Execution.objects.filter(equipment_install__subsystem__title=subsystem).count()
    #     mine_count_cab = Execution.objects.filter(cable_magazine__subsystem__title=subsystem).count()
    #     mine_count = mine_count_eq + mine_count_cab
    #     mine_count_eq_true = Execution.objects.filter(equipment_install__subsystem__title=subsystem,
    #                                                        execution_bool=True).count()
    #     mine_count_cab_true = Execution.objects.filter(cable_magazine__subsystem__title=subsystem,
    #                                                         execution_bool=True).count()
    #     mine_count_true = mine_count_eq_true + mine_count_cab_true
    #     try:
    #         percent = int(mine_count_true * 100 / mine_count)
    #     except ZeroDivisionError:
    #         percent = 0
    # if mine and subsystem.title == 'Все подсистемы' and incl_blocks.title == 'Все уклонные блоки':
    #     mine_count_eq = Execution.objects.filter(equipment_install__number_mine__title=mine).count()
    #     mine_count_cab = Execution.objects.filter(cable_magazine__number_mine__title=mine).count()
    #     mine_count = mine_count_eq + mine_count_cab
    #     mine_count_eq_true = Execution.objects.filter(equipment_install__number_mine__title=mine,
    #                                                   execution_bool=True).count()
    #     mine_count_cab_true = Execution.objects.filter(cable_magazine__number_mine__title=mine,
    #                                                    execution_bool=True).count()
    #     mine_count_true = mine_count_eq_true + mine_count_cab_true
    #     try:
    #         percent = int(mine_count_true * 100 / mine_count)
    #     except ZeroDivisionError:
    #         percent = 0
    # elif mine and subsystem and incl_blocks.title == 'Все уклонные блоки':
    #     mine_count_eq = Execution.objects.filter(equipment_install__number_mine__title=mine,
    #                                              equipment_install__subsystem__title=subsystem).count()
    #     mine_count_cab = Execution.objects.filter(cable_magazine__number_mine__title=mine,
    #                                               cable_magazine__subsystem__title=subsystem).count()
    #     mine_count = mine_count_eq + mine_count_cab
    #     mine_count_eq_true = Execution.objects.filter(equipment_install__number_mine__title=mine,
    #                                                   equipment_install__subsystem__title=subsystem,
    #                                                   execution_bool=True).count()
    #     mine_count_cab_true = Execution.objects.filter(cable_magazine__number_mine__title=mine,
    #                                                    cable_magazine__subsystem__title=subsystem,
    #                                                    execution_bool=True).count()
    #     mine_count_true = mine_count_eq_true + mine_count_cab_true
    #     try:
    #         percent = int(mine_count_true * 100 / mine_count)
    #     except ZeroDivisionError:
    #         percent = 0
    # elif mine and subsystem and incl_blocks:
    #     mine_count_eq = Execution.objects.filter(equipment_install__number_mine__title=mine,
    #                                              equipment_install__subsystem__title=subsystem,
    #                                              equipment_install__inclined_blocks__title=incl_blocks).count()
    #     mine_count_cab = Execution.objects.filter(cable_magazine__number_mine__title=mine,
    #                                               cable_magazine__subsystem__title=subsystem,
    #                                               cable_magazine__inclined_blocks__title=incl_blocks).count()
    #     mine_count = mine_count_eq + mine_count_cab
    #     mine_count_eq_true = Execution.objects.filter(equipment_install__number_mine__title=mine,
    #                                                   equipment_install__subsystem__title=subsystem,
    #                                                   equipment_install__inclined_blocks__title=incl_blocks,
    #                                                   execution_bool=True).count()
    #     mine_count_cab_true = Execution.objects.filter(cable_magazine__number_mine__title=mine,
    #                                                    cable_magazine__subsystem__title=subsystem,
    #                                                    cable_magazine__inclined_blocks__title=incl_blocks,
    #                                                    execution_bool=True).count()
    #     mine_count_true = mine_count_eq_true + mine_count_cab_true
    #     try:
    #         percent = int(mine_count_true * 100 / mine_count)
    #     except ZeroDivisionError:
    #         percent = 0







# def percent_view(request):
#     mine_in_form = ''
#     subsystem_in_form = ''
#     incl_blocks_in_form = ''
#     percent = 0
#
#     if request.method == 'POST':
#         form = SubsystemForm(request.POST)
#         if form.is_valid():
#             mine_in_form = form.cleaned_data.get("number_mines")
#             subsystem_in_form = form.cleaned_data.get("subsystems")
#             incl_blocks_in_form = form.cleaned_data.get("incl_blocks")
#             percent = 0
#             # mine_count_eq = Execution.objects.filter(equipment_install__number_mine__title=mine_in_form,
#             #                                               equipment_install__subsystem__title=subsystem_in_form).count()
#             if mine_in_form.title == 'Все шахты' and subsystem_in_form.title == 'Все подсистемы' and \
#                     incl_blocks_in_form.title == \
#                     'Все уклонные блоки':
#                 mine_count = Execution.objects.all().count()
#                 mine_count_true = Execution.objects.filter(execution_bool=True).count()
#                 try:
#                     percent = int(mine_count_true * 100 / mine_count)
#                 except ZeroDivisionError:
#                     percent = 0
#             context = {percent: percent}
#             return render(request, 'mfss/subsystem_list.html', context)




    # if mine == 'Все шахты' and subsystem in subsystems_list and incl_blocks == 'Все уклонные блоки':
    #     mine_count_eq = Execution.objects.filter(equipment_install__subsystem__title=subsystem).count()
    #     mine_count_cab = Execution.objects.filter(cable_magazine__subsystem__title=subsystem).count()
    #     mine_count = mine_count_eq + mine_count_cab
    #     mine_count_eq_true = Execution.objects.filter(equipment_install__subsystem__title=subsystem,
    #                                                            execution_bool=True).count()

