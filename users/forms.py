from __future__ import annotations

import re

from django import forms
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.core.exceptions import ValidationError

# from catalog.forms import StyleFormMixin
from users.models import User


class StyleFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name != "is_staff":
                field.widget.attrs["class"] = "form-control"


class UserProfileForm(StyleFormMixin, UserChangeForm):
    """Добавление формы профиля пользователя"""

    class Meta:
        model = User
        fields = (
            "last_name",
            "first_name",
            "middle_name",
            "email",
            "phone",
            "location_of_work",
            "post",
            "password",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["password"].widget = forms.HiddenInput()


class RegisterForm(StyleFormMixin, UserCreationForm):
    """Регистрация пользователя только по действительному приглашению."""

    phone = forms.CharField(
        max_length=12,
        widget=forms.TextInput(
            attrs={
                "placeholder": "+7XXXXXXXXXX",  # Подсказка в поле
                "value": "+7",  # Автоматическое значение
            }
        ),
        label="Номер телефона",
        required=True,
    )

    class Meta:
        model = User
        fields = (
            "last_name",
            "first_name",
            "middle_name",
            "email",
            "phone",
            "location_of_work",
            "post",
        )

    def clean(self):
        cleaned_data = super().clean()
        phone = cleaned_data.get("phone")
        last_name = cleaned_data.get("last_name")
        first_name = cleaned_data.get("first_name")
        middle_name = cleaned_data.get("middle_name")

        if phone:
            if not phone.startswith("+7"):
                self.add_error("phone", "Номер телефона должен начинаться с '+7'.")
            elif not re.fullmatch(r"\d{10}", phone[2:]):
                self.add_error("phone", "Введите 10 цифр после '+7'.")

        if (
            all((last_name, first_name, middle_name))
            and User.objects.filter(last_name=last_name, first_name=first_name, middle_name=middle_name).exists()
        ):
            raise ValidationError("Пользователь с такими ФИО уже зарегистрирован.")

        if phone and User.objects.filter(phone=phone).exists():
            self.add_error("phone", "Пользователь с таким номером телефона уже зарегистрирован.")

        return cleaned_data


class SMSVerificationForm(forms.Form):
    code = forms.CharField(
        label=False,
        max_length=4,
        min_length=4,
        widget=forms.TextInput(
            attrs={
                "autocomplete": "off",
                "style": "width: 200px; height: 50px;",
                "class": "mx-auto d-block",
                "placeholder": "Введите 4-х значный код",
            }
        ),
    )
