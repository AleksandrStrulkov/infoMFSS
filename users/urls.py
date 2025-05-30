from django.contrib.auth.views import (PasswordResetCompleteView,
                                       PasswordResetConfirmView,
                                       PasswordResetDoneView,
                                       PasswordResetView)
from django.urls import path, reverse_lazy

from users.apps import UsersConfig
from users.views import (LoginView, LogoutView, PasswordEditDoneView,
                         PasswordEditView, RegisterDoneView, RegisterView,
                         SMSVerificationView, UserUpdateView, user_activate)

app_name = UsersConfig.name

urlpatterns = [
    path("", LoginView.as_view(), name="login"),
    path("verify-sms/", SMSVerificationView.as_view(), name="verify_sms"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("accounts/register/", RegisterView.as_view(), name="register"),
    path("accounts/register/done/", RegisterDoneView.as_view(), name="register_done"),
    path("accounts/activate/<str:sign>", user_activate, name="activate"),
    path("accounts/profile/", UserUpdateView.as_view(), name="profile"),
    # path('profile/genpassword/', generate_new_password, name='generate_new_password'),
    path(
        "accounts/profile/edit/",
        PasswordEditView.as_view(),
        name="profile_edit",
    ),
    path(
        "accounts/profile/edit/done/",
        PasswordEditDoneView.as_view(),
        name="profile_edit_done",
    ),
    path(
        "accounts/password-reset/",
        PasswordResetView.as_view(
            template_name="users/password_reset_form.html",
            email_template_name="users/password_reset_email.html",
            success_url=reverse_lazy("users:password_reset_done"),
        ),
        name="password_reset",
    ),
    path(
        "accounts/password-reset/done/",
        PasswordResetDoneView.as_view(template_name="users/password_reset_done.html"),
        name="password_reset_done",
    ),
    path(
        "accounts/password-reset/<uidb64>/<token>/",
        PasswordResetConfirmView.as_view(
            template_name="users/password_reset_confirm.html",
            success_url=reverse_lazy("users:password_reset_complete"),
        ),
        name="password_reset_confirm",
    ),
    path(
        "accounts/password-reset/complete/",
        PasswordResetCompleteView.as_view(template_name="users/password_reset_complete.html"),
        name="password_reset_complete",
    ),
]
