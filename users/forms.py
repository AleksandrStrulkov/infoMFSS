from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django import forms
# from catalog.forms import StyleFormMixin
from users.models import User
from users.signals import post_register
import re
from .models import AllowedPerson
from django.core.exceptions import ValidationError


class StyleFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name != 'is_staff':
                field.widget.attrs['class'] = 'form-control'


class UserProfileForm(StyleFormMixin, UserChangeForm):
    """Добавление формы профиля пользователя"""

    class Meta:
        model = User
        fields = ('last_name', 'first_name', 'middle_name', 'email', 'phone', 'location_of_work', 'post', 'password',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['password'].widget = forms.HiddenInput()


class RegisterForm(StyleFormMixin, UserCreationForm):
    """Добавление формы регистрации пользователя с верификацией"""
    phone = forms.CharField(
            max_length=12,
            widget=forms.TextInput(
                    attrs={
                            'placeholder': '+7XXXXXXXXXX',  # Подсказка в поле
                            'value': '+7',  # Автоматическое значение
                    }
            ),
            label="Номер телефона",
            required=True
    )

    class Meta:
        model = User
        fields = ('last_name', 'first_name', 'middle_name', 'email', 'phone', 'location_of_work', 'post',)

    def clean(self):
        cleaned_data = super().clean()
        phone = cleaned_data.get('phone')
        last_name = cleaned_data.get('last_name')
        first_name = cleaned_data.get('first_name')
        middle_name = cleaned_data.get('middle_name')

        if phone:
            if not phone.startswith('+7'):
                self.add_error('phone', "Номер телефона должен начинаться с '+7'.")

        digits = phone[2:]
        if not re.match(r'^\d{10}$', digits):  # Проверяем, что оставшиеся 10 символов — цифры
            self.add_error('phone', "Введите 10 цифр после '+7'.")

            # Проверяем, есть ли ФИО в списке разрешённых
        if not AllowedPerson.objects.filter(
                last_name=last_name,
                first_name=first_name,
                middle_name=middle_name,
                is_active=True
        ).exists():
            raise ValidationError(
                    "Ваши ФИО не входят в список разрешённых для регистрации. Обратитесь пожалуйста к администратору "
                    "ресурса."
            )

            # Проверяем, существует ли пользователь с такими же ФИО
        if User.objects.filter(
                last_name=last_name,
                first_name=first_name,
                middle_name=middle_name,
        ).exists():
            raise ValidationError("Пользователь с такими ФИО уже зарегистрирован.")

        if User.objects.filter(
                phone=phone,
        ).exists():
            # raise ValidationError("Пользователь с таким номером телефона уже зарегистрирован.")
            self.add_error('phone', 'Пользователь с таким номером телефона уже зарегистрирован.')

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        user.is_active = False
        user.is_activated = False
        if commit:
            user.save()
        post_register.send(RegisterForm, instance=user)
        return user


class SMSVerificationForm(forms.Form):
    code = forms.CharField(
        label=False,
        max_length=4,
        min_length=4,
        widget=forms.TextInput(attrs={
                'autocomplete': 'off',
                'style': 'width: 200px; height: 50px;',
                'class': 'mx-auto d-block',
                'placeholder': 'Введите 4-х значный код',
        }),
    )