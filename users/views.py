import logging
from random import randint

from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView as BaseLoginView
from django.contrib.auth.views import LogoutView as BaseLogoutView
from django.contrib.auth.views import (PasswordChangeDoneView,
                                       PasswordChangeView)
from django.contrib.messages.views import SuccessMessageMixin
from django.core.signing import BadSignature
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, FormView, UpdateView
from django.views.generic.base import TemplateView

from infoMFSS.services_logger import LoggingMixin, logger_form_valid
from users.forms import RegisterForm, SMSVerificationForm, UserProfileForm
from users.models import User

from .models import SMSDevice
from .sms_utils import send_sms_via_smsc
from .utilities import signer

logger = logging.getLogger(__name__)


class LoginView(LoggingMixin, BaseLoginView):
    template_name = "users/login.html"
    extra_context = {
        "title": "Весь функционал доступен только зарегистрированным пользователям",
    }

    def form_valid(self, form):
        username = form.cleaned_data.get("username")
        user = authenticate(username=username, password=form.cleaned_data.get("password"))
        if user:
            # Генерация и отправка кода
            code = str(randint(1000, 9999))
            response = send_sms_via_smsc(user.phone, code)

            if response.get("error"):
                logger.error(f'Ошибка отправки СМС на номер телефона: {user.phone}: {response["error"]}')
                form.add_error(None, "Ошибка отправки SMS. Попробуйте позже.")
                return self.form_invalid(form)

            # Сохранение кода в БД
            SMSDevice.objects.create(user=user, code=code)
            self.request.session["sms_user_id"] = user.id  # Сохраняем ID для верификации
            self.request.session["sms_user_phone"] = user.phone  # Сохраняем номер телефона для верификации

            logger.info(f"Код отправлен пользователю {username}")
            return redirect("users:verify_sms")  # Перенаправляем на страницу ввода кода

        # # Логирование успешной авторизации
        # logger.info(f'Пользователь {username} успешно авторизовался',
        #             extra={'classname': self.__class__.__name__})

        logger.warning(f"Неудачная попытка входа для {username}")
        return super().form_invalid(form)


class SMSVerificationView(FormView):
    template_name = "users/verify_sms.html"
    form_class = SMSVerificationForm  # Форма с полем code
    success_url = reverse_lazy("infoMFSS:home")  # URL после успешной верификации

    def form_valid(self, form):
        user_id = self.request.session.get("sms_user_id")
        code = form.cleaned_data["code"]

        if user_id:
            try:
                device = SMSDevice.objects.get(user_id=user_id, code=code, is_verified=False)
                device.is_verified = True
                device.save()

                user = device.user
                login(self.request, user)  # Финализируем вход
                logger.info(f"Пользователь {user.username} успешно верифицирован")
                return super().form_valid(form)

            except SMSDevice.DoesNotExist:
                logger.warning(f"Неверный код для пользователя ID {user_id}")
                form.add_error(None, "Неверный код или срок действия истёк")

        return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user_phone"] = self.request.session.get("sms_user_phone")
        return context


class LogoutView(BaseLogoutView):

    def dispatch(self, request, *args, **kwargs):
        logger.info(
            f"Запрос: {request.method} {request.path}/выход из системы", extra={"classname": self.__class__.__name__}
        )
        return super().dispatch(request, *args, **kwargs)


class RegisterView(LoggingMixin, CreateView):
    model = User
    form_class = RegisterForm
    success_url = reverse_lazy("users:register_done")
    extra_context = {
        "title": "Регистрация",
    }
    template_name = "users/register.html"
    success_message = "Вы успешно зарегистрировались"

    def form_valid(self, form):
        logger_form_valid(self)
        return super().form_valid(form)


class RegisterDoneView(TemplateView):
    template_name = "users/register_done.html"
    # extra_context = {
    #         'title': "Регистрация",
    # }


def user_activate(request, sign):
    try:
        email = signer.unsign(sign)
        # logger.info("Активация прошла удачно", extra={'classname': __name__})
    except BadSignature:
        # logger.info("Активация не прошла", extra={'classname': __name__})
        return render(request, "users/activation_failed.html")

    user = get_object_or_404(User, email=email)

    if user.is_activated:
        logger.info(f"Пользователь: {user.email} уже был активирован ранее", extra={"classname": __name__})
        template = "users/activation_done_earlier.html"
    else:
        logger.info(f"Активация прошла удачно. Пользователь: {user.email}", extra={"classname": __name__})
        template = "users/activation_done.html"
        user.is_active = True
        user.is_activated = True
        user.save()

    return render(request, template)


class UserUpdateView(LoggingMixin, LoginRequiredMixin, UpdateView):
    models = User
    success_url = reverse_lazy("mfss:home")
    form_class = UserProfileForm
    extra_context = {
        "title": "Профиль",
    }

    def get_object(self, queryset=None):  # Избавляемся от входящего параметра pk
        return self.request.user

    def form_valid(self, form):
        logger_form_valid(self)
        return super().form_valid(form)


class PasswordEditView(SuccessMessageMixin, LoginRequiredMixin, PasswordChangeView):
    template_name = "users/password_edit.html"
    success_url = reverse_lazy("users:profile_edit_done")
    success_message = "Пароль успешно изменен"

    def dispatch(self, request, *args, **kwargs):
        logger.info(
            f"Запрос: {request.method} {request.path}{request.user.last_name}/запрос изменения пароля",
            extra={"classname": self.__class__.__name__},
        )
        return super().dispatch(request, *args, **kwargs)


class PasswordEditDoneView(SuccessMessageMixin, LoginRequiredMixin, PasswordChangeDoneView):
    template_name = "users/password_update_complete.html"

    def dispatch(self, request, *args, **kwargs):
        logger.info(
            f"Запрос: {request.method} {request.path}{request.user.last_name}/пароль изменен",
            extra={"classname": self.__class__.__name__},
        )
        return super().dispatch(request, *args, **kwargs)
