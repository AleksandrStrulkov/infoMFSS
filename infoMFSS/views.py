from django.shortcuts import render

from django.urls import reverse_lazy

from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView
from django.shortcuts import redirect
# from mailings.forms import MessageForm, ClientForm, MailingForm, MailingManagerForm, MailingOptionsForm, UserActiveForm
from infoMFSS.models import Execution, DateUpdate
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
        mine1_count_true_eg = Execution.objects.filter(equipment_install__number_mine__title="Нефтешахта №1",
                                                       execution_bool=True).count()
        mine1_count_true_cab = Execution.objects.filter(cable_magazine__number_mine__title="Нефтешахта №1",
                                                        execution_bool=True).count()
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
        mine2_count_true_eq = Execution.objects.filter(equipment_install__number_mine__title="Нефтешахта №2",
                                                       execution_bool=True).count()
        mine2_count_true_cab = Execution.objects.filter(cable_magazine__number_mine__title="Нефтешахта №2",
                                                        execution_bool=True).count()
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
        mine3_count_true_eq = Execution.objects.filter(equipment_install__number_mine__title="Нефтешахта №3",
                                                       execution_bool=True).count()
        mine3_count_true_cab = Execution.objects.filter(cable_magazine__number_mine__title="Нефтешахта №3",
                                                        execution_bool=True).count()
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

class DataUpdate:
    objects = None


def index(request):

    mine = ''
    subsystem = ''
    incl_blocks = ''
    percent = ''
    update = ''

    form = SubsystemForm(request.POST or None)
    if form.is_valid():
        mine = form.cleaned_data.get("number_mine")
        subsystem = form.cleaned_data.get("subsystem")
        incl_blocks = form.cleaned_data.get("incl_blocks")

    if not mine and not subsystem and not incl_blocks:
        mine_count = Execution.objects.all().count()
        mine_count_true = Execution.objects.filter(execution_bool=True).count()
        try:
            percent = int(mine_count_true * 100 / mine_count)
        except ZeroDivisionError:
            percent = 0
    elif not mine and subsystem and not incl_blocks:
        subsystem_count_eq = Execution.objects.filter(equipment_install__subsystem__title=subsystem).count()
        subsystem_count_cab = Execution.objects.filter(cable_magazine__subsystem__title=subsystem).count()
        subsystem_count = subsystem_count_eq + subsystem_count_cab
        subsystem_count_eq_true = Execution.objects.filter(equipment_install__subsystem__title=subsystem,
                                                           execution_bool=True).count()
        subsystem_count_cab_true = Execution.objects.filter(cable_magazine__subsystem__title=subsystem,
                                                            execution_bool=True).count()
        subsystem_count_true = subsystem_count_eq_true + subsystem_count_cab_true
        try:
            percent = int(subsystem_count_true * 100 / subsystem_count)
        except ZeroDivisionError:
            percent = 0
    elif mine and not subsystem and not incl_blocks:
        mine_count_eq = Execution.objects.filter(equipment_install__number_mine__title=mine).count()
        mine_count_cab = Execution.objects.filter(cable_magazine__number_mine__title=mine).count()
        mine_count = mine_count_eq + mine_count_cab
        mine_count_eq_true = Execution.objects.filter(equipment_install__number_mine__title=mine,
                                                      execution_bool=True).count()
        mine_count_cab_true = Execution.objects.filter(cable_magazine__number_mine__title=mine,
                                                       execution_bool=True).count()
        mine_count_true = mine_count_eq_true + mine_count_cab_true
        try:
            percent = int(mine_count_true * 100 / mine_count)
        except ZeroDivisionError:
            percent = 0
    elif mine and subsystem and not incl_blocks:
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
    elif mine and subsystem and incl_blocks:
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

    context = {'form': form,
               'mine': mine,
               'subsystem': subsystem,
               'incl_blocks': incl_blocks,
               'percent': percent,
               'update': update,
               }

    return render(request, 'mfss/subsystem_list.html', context)
