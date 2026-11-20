from __future__ import annotations

import logging
from urllib.parse import urlencode

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView as BaseLoginView
from django.contrib.auth.views import LogoutView as BaseLogoutView
from django.contrib.auth.views import PasswordChangeDoneView, PasswordChangeView
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST
from django.views.generic import FormView, UpdateView
from django.views.generic.base import TemplateView

from infoMFSS.services_logger import LoggingMixin, logger_form_valid
from users.forms import RegisterForm, SMSVerificationForm, UserProfileForm
from users.models import SMSDevice, User
from users.services import (
    InvalidInvitation,
    InvitationLimitReached,
    active_invitations,
    create_invitation,
    get_valid_invitation,
    redeem_invitation,
    redeemed_invitations,
)

logger = logging.getLogger(__name__)


class LoginView(LoggingMixin, BaseLoginView):
    template_name = "users/login.html"
    extra_context = {"title": "Доступ к системе по приглашению"}

    def form_valid(self, form):
        logger.info("Пользователь успешно вошёл в систему")
        return super().form_valid(form)


class LegacyLoginRedirectView(TemplateView):
    """Keep old GET bookmarks while accepting legacy login form POSTs."""

    def get(self, request: HttpRequest, *args: object, **kwargs: object) -> HttpResponse:
        destination = reverse("users:login")
        next_url = request.GET.get("next", "")
        if next_url and url_has_allowed_host_and_scheme(
            next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()
        ):
            destination += "?" + urlencode({"next": next_url}, safe="/")
        return redirect(destination)

    def post(self, request: HttpRequest, *args: object, **kwargs: object) -> HttpResponse:
        # Authenticate in place: preserve POST bodies instead of redirecting credentials.
        return LoginView.as_view()(request, *args, **kwargs)


class SMSVerificationView(FormView):
    template_name = "users/verify_sms.html"
    form_class = SMSVerificationForm
    success_url = reverse_lazy("mfss:home")

    def form_valid(self, form):
        user_id = self.request.session.get("sms_user_id")
        if user_id:
            device = SMSDevice.objects.filter(
                user_id=user_id, code=form.cleaned_data["code"], is_verified=False
            ).first()
            if device is not None and device.is_valid():
                device.is_verified = True
                device.save(update_fields=["is_verified"])
                login(self.request, device.user)
                return super().form_valid(form)
        form.add_error(None, "Неверный код или срок действия истёк")
        return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user_phone"] = self.request.session.get("sms_user_phone")
        return context


class LogoutView(BaseLogoutView):
    pass


class RegisterWithoutTokenView(TemplateView):
    template_name = "users/registration_invalid.html"


class RegisterView(FormView):
    form_class = RegisterForm
    template_name = "users/register.html"

    def dispatch(self, request: HttpRequest, *args: object, **kwargs: object) -> HttpResponse:
        self.invitation = get_valid_invitation(str(kwargs["token"]))
        if self.invitation is None:
            response = render(request, "users/registration_invalid.html")
        else:
            response = super().dispatch(request, *args, **kwargs)
        response["Referrer-Policy"] = "no-referrer"
        response["Cache-Control"] = "private, no-store"
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["inviter"] = self.invitation.created_by
        context["title"] = "Регистрация по приглашению"
        return context

    def form_valid(self, form):
        user = form.save(commit=False)
        try:
            user = redeem_invitation(self.invitation.token, user)
        except InvalidInvitation:
            return render(self.request, "users/registration_invalid.html")
        login(self.request, user, backend="django.contrib.auth.backends.ModelBackend")
        return redirect("mfss:home")


@method_decorator(require_POST, name="dispatch")
class CreateInvitationView(LoginRequiredMixin, TemplateView):
    def post(self, request: HttpRequest, *args: object, **kwargs: object) -> HttpResponse:
        try:
            create_invitation(request.user)
            messages.success(request, "Ссылка-приглашение создана.")
        except InvitationLimitReached:
            messages.error(request, "Достигнут предел действующих приглашений.")
        return redirect("users:profile")


class UserUpdateView(LoggingMixin, LoginRequiredMixin, UpdateView):
    model = User
    success_url = reverse_lazy("mfss:home")
    form_class = UserProfileForm
    template_name = "users/user_form.html"
    extra_context = {"title": "Профиль"}

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_invitations"] = [
            (self.request.build_absolute_uri(reverse("users:register", kwargs={"token": invite.token})), invite)
            for invite in active_invitations(self.request.user)
        ]
        context["redeemed_invitations"] = redeemed_invitations(self.request.user)
        return context

    def form_valid(self, form):
        logger_form_valid(self)
        return super().form_valid(form)


class PasswordEditView(SuccessMessageMixin, LoginRequiredMixin, PasswordChangeView):
    template_name = "users/password_edit.html"
    success_url = reverse_lazy("users:profile_edit_done")
    success_message = "Пароль успешно изменен"


class PasswordEditDoneView(SuccessMessageMixin, LoginRequiredMixin, PasswordChangeDoneView):
    template_name = "users/password_update_complete.html"
