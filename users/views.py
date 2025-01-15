from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import render

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.views import LoginView as BaseLoginView, PasswordChangeView
from django.contrib.auth.views import LogoutView as BaseLogoutView
from django.views.generic import CreateView, UpdateView
from django.views.generic.base import TemplateView

from users.models import User
from django.urls import reverse_lazy, reverse

from users.forms import RegisterForm, UserProfileForm

from django.core.signing import BadSignature

from .services import send_new_password
from .utilities import signer
from django.contrib.auth import views as auth_views
from django.core.mail import send_mail
from django.conf import settings


class LoginView(BaseLoginView):
    template_name = 'users/login.html'
    extra_context = {
            'title': "Авторизация",
    }


class LogoutView(BaseLogoutView):
    pass


class RegisterView(CreateView):
    model = User
    # form_class = UserForm
    form_class = RegisterForm
    success_url = reverse_lazy('users:register_done')
    extra_context = {
            'title': "Регистрация",
    }
    template_name = 'users/register.html'
    success_message = 'Вы успешно зарегистрировались'


class RegisterDoneView(TemplateView):
    template_name = 'users/register_done.html'
    # extra_context = {
    #         'title': "Регистрация",
    # }


def user_activate(request, sign):
    try:
        email = signer.unsign(sign)
    except BadSignature:
        return render(request, 'users/activation_failed.html')

    user = get_object_or_404(User, email=email)

    if user.is_activated:
        template = 'users/activation_done_earlier.html'
    else:
        template = 'users/activation_done.html'
        user.is_active = True
        user.is_activated = True
        user.save()

    return render(request, template)


class UserUpdateView(LoginRequiredMixin, UpdateView):
    models = User
    success_url = reverse_lazy('users:profile')
    form_class = UserProfileForm
    extra_context = {
            'title': "Профиль",
    }

    def get_object(self, queryset=None):  # Избавляемся от входящего параметра pk
        return self.request.user


# @login_required
# def generate_new_password(request):
#     new_password = User.objects.make_random_password()
#     request.user.set_password(new_password)
#     request.user.save()
#     send_new_password(request.user.email, new_password)
#     return redirect(reverse('catalog:home'))

class PasswordEditView(SuccessMessageMixin, LoginRequiredMixin, PasswordChangeView):
    template_name = 'users/password_edit.html'
    success_url = reverse_lazy('users:profile')
    success_message = 'Пароль успешно изменен'


# class PasswordResetView(auth_views.PasswordResetView):
#     template_name = 'users/password_reset_done.html'

