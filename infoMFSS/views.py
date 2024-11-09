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
        mine1_count = Execution.objects.filter(number_mine__title="Нефтешахта №1").count()
        mine1_count_true = Execution.objects.filter(number_mine__title="Нефтешахта №1", execution_bool=True).count()
        try:
            mine1_count_percent = int(mine1_count_true * 100 / mine1_count)
        except ZeroDivisionError:
            mine1_count_percent = 0
        context['percent_mine1'] = mine1_count_percent

        """Контекст для нефтешахты №2"""
        mine2_count = Execution.objects.filter(number_mine__title="Нефтешахта №2").count()
        mine2_count_true = Execution.objects.filter(number_mine__title="Нефтешахта №2", execution_bool=True).count()
        try:
            mine2_count_percent = int(mine2_count_true * 100 / mine2_count)
        except ZeroDivisionError:
            mine2_count_percent = 0
        context['percent_mine2'] = mine2_count_percent

        """Контекст для нефтешахты №3"""
        mine3_count = Execution.objects.filter(number_mine__title="Нефтешахта №3").count()
        mine3_count_true = Execution.objects.filter(number_mine__title="Нефтешахта №3", execution_bool=True).count()
        try:
            mine3_count_percent = int(mine3_count_true * 100 / mine3_count)
        except ZeroDivisionError:
            mine3_count_percent = 0
        context['percent_mine3'] = mine3_count_percent

        """Контекст для всех шахт"""
        mine123_count = mine1_count + mine2_count + mine3_count
        mine123_count_true = mine1_count_true + mine2_count_true + mine3_count_true
        try:
            mine123_count_percent = int(mine123_count_true * 100 / mine123_count)
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
    # submitbutton = request.POST.get("submit")

    mine = ''
    subsystem = ''
    percent = ''
    update = ''
    # emailvalue = ''

    form = SubsystemForm(request.POST or None)
    if form.is_valid():
        mine = form.cleaned_data.get("number_mine")
        subsystem = form.cleaned_data.get("subsystem")
        # emailvalue = form.cleaned_data.get("email")

    mine_count = Execution.objects.filter(number_mine__title=mine, subsystem__title=subsystem).count()
    mine_count_true = Execution.objects.filter(number_mine__title=mine, subsystem__title=subsystem,
                                               execution_bool=True).count()
    update = DateUpdate.objects.latest('update')
    # print(mine_count, mine_count_true)
    try:
        percent = int(mine_count_true * 100 / mine_count)
    except ZeroDivisionError:
        percent = 0

    # queryset_mine = queryset.filter(number_mine=number_mine, subsystem=subsystem).count()
    #         queryset_mine_bool = queryset.filter(number_mine=number_mine, subsystem=subsystem, execution_bool=True).count()
    #         percent = int(queryset_mine_bool.count() * 100 / queryset_mine.count())


    context = {'form': form,
               'mine': mine,
               'subsystem': subsystem,
               'percent': percent,
               'update': update,
               }

    return render(request, 'mfss/subsystem_list.html', context)
