from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.views import LoginView as BaseLoginView, PasswordChangeView, PasswordChangeDoneView
from django.contrib.auth.views import LogoutView as BaseLogoutView
from django.views.generic import CreateView, UpdateView
from django.views.generic.base import TemplateView
from users.models import User
from django.urls import reverse_lazy, reverse
from users.forms import RegisterForm, UserProfileForm
from django.core.signing import BadSignature
from .utilities import signer
from infoMFSS.services_logger import *

logger = logging.getLogger(__name__)


class LoginView(LoggingMixin, BaseLoginView):
    template_name = 'users/login.html'
    extra_context = {
            'title': "Весь функционал доступен только зарегистрированным пользователям",
    }

    def form_valid(self, form):
        username = form.cleaned_data.get('username')

        # Логирование успешной авторизации
        logger.info(f'Пользователь {username} . успешно авторизовался',
                    extra={'classname': self.__class__.__name__})

        return super().form_valid(form)


class LogoutView(BaseLogoutView):

    def dispatch(self, request, *args, **kwargs):
        logger.info(f'Запрос: {request.method} {request.path}/выход из системы',
                    extra={'classname': self.__class__.__name__})
        return super().dispatch(request, *args, **kwargs)


class RegisterView(LoggingMixin, CreateView):
    model = User
    # form_class = UserForm
    form_class = RegisterForm
    success_url = reverse_lazy('users:register_done')
    extra_context = {
            'title': "Регистрация",
    }
    template_name = 'users/register.html'
    success_message = 'Вы успешно зарегистрировались'

    def form_valid(self, form):
        logger_form_valid(self)
        return super().form_valid(form)


class RegisterDoneView(TemplateView):
    template_name = 'users/register_done.html'
    # extra_context = {
    #         'title': "Регистрация",
    # }


def user_activate(request, sign):
    try:
        email = signer.unsign(sign)
        # logger.info("Активация прошла удачно", extra={'classname': __name__})
    except BadSignature:
        # logger.info("Активация не прошла", extra={'classname': __name__})
        return render(request, 'users/activation_failed.html')

    user = get_object_or_404(User, email=email)

    if user.is_activated:
        logger.info(f"Пользователь: {user.email} уже был активирован ранее", extra={'classname': __name__})
        template = 'users/activation_done_earlier.html'
    else:
        logger.info(f"Активация прошла удачно. Пользователь: {user.email}", extra={'classname': __name__})
        template = 'users/activation_done.html'
        user.is_active = True
        user.is_activated = True
        user.save()

    return render(request, template)


class UserUpdateView(LoggingMixin, LoginRequiredMixin, UpdateView):
    models = User
    success_url = reverse_lazy('mfss:home')
    form_class = UserProfileForm
    extra_context = {
            'title': "Профиль",
    }

    def get_object(self, queryset=None):  # Избавляемся от входящего параметра pk
        return self.request.user

    def form_valid(self, form):
        logger_form_valid(self)
        return super().form_valid(form)


class PasswordEditView(SuccessMessageMixin, LoginRequiredMixin, PasswordChangeView):
    template_name = 'users/password_edit.html'
    success_url = reverse_lazy('users:profile_edit_done')
    success_message = 'Пароль успешно изменен'

    def dispatch(self, request, *args, **kwargs):
        logger.info(f'Запрос: {request.method} {request.path}{request.user.last_name}/запрос изменения пароля',
                    extra={'classname': self.__class__.__name__})
        return super().dispatch(request, *args, **kwargs)


class PasswordEditDoneView(SuccessMessageMixin, LoginRequiredMixin, PasswordChangeDoneView):
    template_name = 'users/password_update_complete.html'

    def dispatch(self, request, *args, **kwargs):
        logger.info(f'Запрос: {request.method} {request.path}{request.user.last_name}/пароль изменен',
                    extra={'classname': self.__class__.__name__})
        return super().dispatch(request, *args, **kwargs)

