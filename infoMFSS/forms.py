from captcha.fields import CaptchaField
from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, Field, Layout, Submit
from django import forms
from django.db.models import Case, IntegerField, Value, When
from django.utils import timezone

from infoMFSS.castom_widgets_form import CustomModelChoiceField
from infoMFSS.models import (Beacon, BranchesBox, Cable, CableMagazine,
                             DateUpdate, Equipment, EquipmentInstallation,
                             Execution, InclinedBlocks, NumberMine, PointPhone,
                             Subsystem, Tunnel, Violations, Visual)


class InfoFormMixin(forms.Form):
    number_mines = forms.ModelChoiceField(
        queryset=NumberMine.objects.none(), to_field_name="title", label="Шахта", initial="Все шахты"
    )
    subsystems = forms.ModelChoiceField(
        queryset=Subsystem.objects.none(), to_field_name="title", label="Подсистема", initial="Все подсистемы"
    )
    incl_blocks = CustomModelChoiceField(
        queryset=InclinedBlocks.objects.none(),
        to_field_name="title",
        label="Уклонный блок",
        initial="Все уклонные блоки",
        # widget=CustomSelect(),
    )

    def clean(self):
        cleaned_data = super().clean()
        # if "number_mines" in cleaned_data:
        number_mines = cleaned_data.get("number_mines").title
        # if "incl_block" in cleaned_data:
        incl_blocks = cleaned_data.get("incl_blocks").title
        subsystems = None
        if "subsystems" in cleaned_data:
            subsystems = cleaned_data.get("subsystems").title
        # incl_blocks = cleaned_data.get('incl_blocks').title

        # Получаем списки значений из базы данных
        incl_list = list(
            InclinedBlocks.objects.filter(number_mine__title__icontains=number_mines).values_list("title", flat=True)
        )
        incl_list.append("Все уклонные блоки")

        incl_all_list = list(
            InclinedBlocks.objects.exclude(title="Все уклонные блоки").values_list("title", flat=True)
        )

        subsystems_list = list(Subsystem.objects.values_list("title", flat=True))

        if incl_list and incl_blocks not in incl_list:
            self.add_error("incl_blocks", "Не верно указан уклонный блок")

        if number_mines == "Все шахты" and subsystems in subsystems_list and incl_blocks in incl_all_list:
            self.add_error("number_mines", "Нефтешахта не выбрана")

        return cleaned_data

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Добавляем "Все шахты" и реальные объекты
        all_number_mines_option = NumberMine.objects.filter(title="Все шахты").first()
        if all_number_mines_option:
            self.fields["number_mines"].queryset = NumberMine.objects.annotate(
                custom_order=Case(
                    When(id=all_number_mines_option.id, then=Value(0)),  # "Все шахты" получает порядок 0
                    default=Value(1),  # Все остальные получают порядок 1
                    output_field=IntegerField(),
                )
            ).order_by("custom_order", "title")
        else:
            self.fields["number_mines"].queryset = NumberMine.objects.all()

        all_subsystems_option = Subsystem.objects.filter(title="Все подсистемы").first()
        if all_subsystems_option:
            self.fields["subsystems"].queryset = Subsystem.objects.annotate(
                custom_order=Case(
                    When(id=all_subsystems_option.id, then=Value(0)),  # "Все шахты" получает порядок 0
                    default=Value(1),  # Все остальные получают порядок 1
                    output_field=IntegerField(),
                )
            ).order_by("custom_order", "title")
        else:
            self.fields["subsystems"].queryset = Subsystem.objects.all()

        # Добавляем "Все шахты" и реальные объекты
        all_blocks_option = InclinedBlocks.objects.filter(title="Все уклонные блоки").first()
        if all_blocks_option:
            self.fields["incl_blocks"].queryset = InclinedBlocks.objects.annotate(
                custom_order=Case(
                    When(id=all_blocks_option.id, then=Value(0)),  # "Все шахты" получает порядок 0
                    default=Value(1),  # Все остальные получают порядок 1
                    output_field=IntegerField(),
                )
            ).order_by("custom_order", "number_mine")
        else:
            self.fields["incl_blocks"].queryset = InclinedBlocks.objects.all()


class InfoProjectFormMixin(InfoFormMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop("incl_blocks")

    def clean(self):
        return self.cleaned_data


class PercentForm(InfoFormMixin):
    pass


class EquipmentForm(InfoFormMixin):
    equipment = forms.ModelChoiceField(
        queryset=Equipment.objects.none(), to_field_name="title", label="Оборудование", initial="Все оборудование"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Добавляем "Все шахты" и реальные объекты
        all_equipment_option = Equipment.objects.filter(title="Все оборудование").first()
        if all_equipment_option:
            self.fields["equipment"].queryset = Equipment.objects.annotate(
                custom_order=Case(
                    When(id=all_equipment_option.id, then=Value(0)),  # "Все шахты" получает порядок 0
                    default=Value(1),  # Все остальные получают порядок 1
                    output_field=IntegerField(),
                )
            ).order_by("custom_order", "title")
        else:
            self.fields["equipment"].queryset = Equipment.objects.all()


class CableForm(InfoFormMixin):
    cable = forms.ModelChoiceField(
        queryset=Cable.objects.none(), to_field_name="title", label="Кабель", initial="Все кабели"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Добавляем "Все шахты" и реальные объекты
        all_cable_option = Cable.objects.filter(title="Все кабели").first()
        if all_cable_option:
            self.fields["cable"].queryset = Cable.objects.annotate(
                custom_order=Case(
                    When(id=all_cable_option.id, then=Value(0)),  # "Все шахты" получает порядок 0
                    default=Value(1),  # Все остальные получают порядок 1
                    output_field=IntegerField(),
                )
            ).order_by("custom_order", "title")
        else:
            self.fields["cable"].queryset = Cable.objects.all()


class BoxForm(InfoFormMixin):
    pass


class ProjectEquipmentForm(InfoProjectFormMixin):
    pass


class ProjectCableForm(InfoProjectFormMixin):
    pass


class BeaconForm(InfoFormMixin, forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "subsystems" in self.fields:
            del self.fields["subsystems"]

    def clean(self):
        cleaned_data = super(InfoFormMixin, self).clean()

        number_mines = cleaned_data.get("number_mines")
        incl_blocks = cleaned_data.get("incl_blocks")

        number_mines = number_mines.title
        incl_blocks = incl_blocks.title

        # Получаем списки значений из базы данных
        incl_list = list(
            InclinedBlocks.objects.filter(number_mine__title__icontains=number_mines).values_list("title", flat=True)
        )
        incl_list.append("Все уклонные блоки")

        incl_all_list = list(
            InclinedBlocks.objects.exclude(title="Все уклонные блоки").values_list("title", flat=True)
        )

        if incl_list and incl_blocks not in incl_list:
            self.add_error("incl_blocks", "Не верно указан уклонный блок")

        if number_mines == "Все шахты" and incl_blocks != "Все уклонные блоки":
            self.add_error("number_mines", "Нефтешахта не выбрана")

        return cleaned_data


class VisualForm(forms.ModelForm):
    class Meta:
        model = Visual
        fields = ("number_mine", "equipment", "cable")

    def clean(self):
        cleaned_data = super().clean()
        number_mine = cleaned_data.get("number_mine")
        equipment = cleaned_data.get("equipment")
        cable = cleaned_data.get("cable")

        if number_mine is None:
            self.add_error("number_mine", "Укажите шахту")

        if equipment and cable:
            self.add_error("equipment", "Выберите один из вариантов")

        if equipment and cable:
            self.add_error("cable", "Выберите один из вариантов")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["number_mine"].queryset = NumberMine.objects.exclude(title="Все шахты")
        self.fields["equipment"].queryset = Equipment.objects.exclude(title="Все оборудование")
        self.fields["cable"].queryset = Cable.objects.exclude(title="Все кабели")
        self.fields["number_mine"].empty_label = "Выберите шахту"
        self.fields["equipment"].empty_label = "Выберите оборудование"
        self.fields["cable"].empty_label = "Выберите кабель"


class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, label="Ваше имя")
    email = forms.EmailField(label="Ваш email")
    message = forms.CharField(widget=forms.Textarea, label="Сообщение")
    captcha = CaptchaField(
        label="Введите ответ",
        generator="captcha.helpers.math_challenge",
        error_messages={"invalid": "Неправильный ответ"},
    )


class QuantityEquipmentCableForm(forms.Form):
    number_mines = forms.ChoiceField(
        choices=[
            ("Нефтешахта №1", "Нефтешахта №1"),
            ("Нефтешахта №2", "Нефтешахта №2"),
            ("Нефтешахта №3", "Нефтешахта №3"),
        ],
        label="Выберите шахту",
        required=True,
    )
    equipment = forms.ModelChoiceField(
        queryset=Equipment.objects.exclude(title="Все оборудование"),
        to_field_name="title",
        label="Оборудование",
        required=False,
        empty_label="Не выбрано",
    )
    cable = forms.ModelChoiceField(
        queryset=Cable.objects.exclude(title="Все кабели"),
        to_field_name="title",
        label="Кабель",
        required=False,
        empty_label="Не выбрано",
    )

    def clean(self):
        cleaned_data = super().clean()
        equipment = cleaned_data.get("equipment")
        cable = cleaned_data.get("cable")

        if equipment is None and cable is None:
            self.add_error("equipment", "Не выбрано оборудование")
            self.add_error("cable", "Не выбран кабель")

        if equipment and cable:
            self.add_error("equipment", "Выберите только один из вариантов")


class EquipmentCreateForm(forms.ModelForm):
    class Meta:
        model = Equipment
        fields = (
            "title",
            "device_type",
            "description",
            "subsystem",
            "file_pdf",
            "file_passport",
            "file_certificate",
        )
        widgets = {
            "device_type": forms.TextInput(
                attrs={
                    "placeholder": "Например: Эльтон-Ex231",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["subsystem"].queryset = Subsystem.objects.exclude(title="Все подсистемы")

        for field_name, field in self.fields.items():
            if isinstance(field, forms.ModelChoiceField):
                field.empty_label = "Выберите значение"

    def clean(self):
        cleaned_data = super().clean()
        subsystem = cleaned_data.get("subsystem")

        if subsystem is None:
            self.add_error("subsystem", "Подсистема не выбрана")


class CableCreateForm(forms.ModelForm):
    class Meta:
        model = Cable
        fields = (
            "title",
            "device_type",
            "description",
            "file_pdf",
            "file_passport",
            "file_certificate",
        )


class BeaconCreateForm(forms.ModelForm):
    class Meta:
        model = Beacon
        fields = (
            "designation",
            "subsystem",
            "number_mine",
            "tunnel",
            "inclined_blocks",
            "picket",
            "mac_address",
            "serial_number",
            "minor",
            "execution_bool",
            "data",
        )
        widgets = {
            "designation": forms.TextInput(
                attrs={
                    "placeholder": "Например: 1TD205",
                }
            ),
            "picket": forms.TextInput(
                attrs={
                    "placeholder": "Например: 55 или 55+4",
                }
            ),
            "mac_address": forms.TextInput(
                attrs={
                    "placeholder": "Например D9:0A:15:56:D5:3B",
                    "class": "mac-input",  # для JS-обработки
                }
            ),
            "serial_number": forms.TextInput(
                attrs={
                    "placeholder": "Например: 254",
                }
            ),
            "minor": forms.TextInput(
                attrs={
                    "placeholder": "Например: 8888",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["number_mine"].queryset = NumberMine.objects.exclude(title="Все шахты")
        # self.fields['tunnel'].queryset = Tunnel.objects.exclude(title="Все туннели")
        self.fields["inclined_blocks"].queryset = InclinedBlocks.objects.exclude(title="Все уклонные блоки")

        for field_name, field in self.fields.items():
            if isinstance(field, forms.ModelChoiceField):
                field.empty_label = "Выберите значение"

    def clean(self):
        cleaned_data = super().clean()

        number_mine = cleaned_data.get("number_mine")
        tunnel = cleaned_data.get("tunnel")
        inclined_blocks = cleaned_data.get("inclined_blocks")

        # Получаем списки значений из базы данных
        incl_list = list(
            InclinedBlocks.objects.filter(number_mine__title__icontains=number_mine).values_list("title", flat=True)
        )
        incl_list.append("Все уклонные блоки")

        incl_all_list = list(
            InclinedBlocks.objects.exclude(title="Все уклонные блоки").values_list("title", flat=True)
        )

        if tunnel is not None:
            if tunnel.inclined_blocks is not None and inclined_blocks is None:
                self.add_error("inclined_blocks", f"Выберите уклонный блок {tunnel.inclined_blocks.title}")
            if tunnel.inclined_blocks != inclined_blocks and inclined_blocks is not None:
                self.add_error("inclined_blocks", "Укажите уклонный блок верно")

        return cleaned_data


class PointPhoneCreateForm(forms.ModelForm):
    class Meta:
        model = PointPhone
        fields = (
            "title",
            "device_type",
            "serial_number",
            "number_mine",
            "tunnel",
            "inclined_blocks",
            "subscriber_number",
            "picket",
            "description",
        )
        # required = True
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "placeholder": "Например: T1-65",
                }
            ),
            "subscriber_number": forms.TextInput(
                attrs={
                    "placeholder": "Например: 8777",
                }
            ),
            "picket": forms.TextInput(
                attrs={
                    "placeholder": "Например 55 или 55+7",
                }
            ),
            "device_type": forms.TextInput(
                attrs={
                    "placeholder": "Например: Эльтон-Ex231",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["number_mine"].queryset = NumberMine.objects.exclude(title="Все шахты")
        self.fields["inclined_blocks"].queryset = InclinedBlocks.objects.exclude(title="Все уклонные блоки")
        self.fields["device_type"].initial = "Эльтон-Ex231"

        for field_name, field in self.fields.items():
            if isinstance(field, forms.ModelChoiceField):
                field.empty_label = "Выберите значение"

    def clean(self):
        cleaned_data = super().clean()
        number_mine = cleaned_data.get("number_mine")
        tunnel = cleaned_data.get("tunnel")
        inclined_blocks = cleaned_data.get("inclined_blocks")
        title = cleaned_data.get("title")
        subscriber_number = cleaned_data.get("subscriber_number")
        serial_number = cleaned_data.get("serial_number")

        if title is None:
            self.add_error("title", "Укажите обозначение точки телефонии")

        if number_mine is None:
            self.add_error("number_mine", "Нефтешахта не выбрана")

        if tunnel is None:
            self.add_error("tunnel", "Выработка не выбрана")

        if subscriber_number is None:
            self.add_error("subscriber_number", "Укажите абонентский номер")

        if serial_number is not None:
            for item in serial_number:
                if not item.isdigit():
                    self.add_error("serial_number", f"Заводской номер должен быть числом")

        for item in subscriber_number:
            if not item.isdigit():
                self.add_error("subscriber_number", "Абонентский номер должен содержать только цифры")

        if tunnel is not None:
            if tunnel.inclined_blocks is not None and inclined_blocks is None:
                self.add_error("inclined_blocks", f"Выберите уклонный блок {tunnel.inclined_blocks.title}")
            if tunnel.inclined_blocks != inclined_blocks and inclined_blocks is not None:
                self.add_error("inclined_blocks", "Укажите уклонный блок верно")


class BranchesBoxCreateForm(forms.ModelForm):
    class Meta:
        model = BranchesBox
        fields = (
            "title",
            "device_type",
            "serial_number",
            "ip_address",
            "subsystem",
            "number_mine",
            "tunnel",
            "inclined_blocks",
            "picket",
            "description",
            "equipment",
            "boolean_block",
        )
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "placeholder": "Например: 50#01 или 1ССП01",
                }
            ),
            "device_type": forms.TextInput(
                attrs={
                    "placeholder": "Например: МС12.18-34",
                }
            ),
            "picket": forms.TextInput(
                attrs={
                    "placeholder": "Например 12 или 12+5",
                }
            ),
            "serial_number": forms.TextInput(
                attrs={
                    "placeholder": "Например: 123",
                }
            ),
            "ip_address": forms.TextInput(
                attrs={
                    "placeholder": "10.10.110.110",
                    "class": "ip-input",  # для JS-обработки
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["number_mine"].queryset = NumberMine.objects.exclude(title="Все шахты")
        self.fields["inclined_blocks"].queryset = InclinedBlocks.objects.exclude(title="Все уклонные блоки")
        self.fields["subsystem"].queryset = Subsystem.objects.exclude(title="Все подсистемы")

        for field_name, field in self.fields.items():
            if isinstance(field, forms.ModelChoiceField):
                field.empty_label = "Выберите значение"

    def clean(self):
        cleaned_data = super().clean()
        # number_mine = cleaned_data.get('number_mine')
        tunnel = cleaned_data.get("tunnel")
        inclined_blocks = cleaned_data.get("inclined_blocks")
        subsystem = cleaned_data.get("subsystem")
        equipment = cleaned_data.get("equipment")
        boolean_block = cleaned_data.get("boolean_block")
        ip_address = cleaned_data.get("ip_address")
        serial_number = cleaned_data.get("serial_number")

        if serial_number is None:
            self.add_error("serial_number", "Укажите заводской номер")

        if ip_address is None:
            self.add_error("ip_address", "Укажите IP-адрес")

        if serial_number:
            for item in serial_number:
                if not item.isdigit():
                    self.add_error("serial_number", f"Заводской номер должен быть числом")

        if tunnel is None:
            self.add_error("tunnel", "Выработка не выбрана")

        if subsystem is None:
            self.add_error("subsystem", "Подсистема не выбрана")

        if tunnel is not None:
            if tunnel.inclined_blocks is not None and inclined_blocks is None:
                self.add_error("inclined_blocks", f"Выберите уклонный блок {tunnel.inclined_blocks.title}")
            if tunnel.inclined_blocks != inclined_blocks and inclined_blocks is not None:
                self.add_error("inclined_blocks", "Укажите уклонный блок верно")

        if inclined_blocks and boolean_block is False:
            self.add_error(
                "boolean_block", f"Установите галочку, т.к. уклонный блок " f"{tunnel.inclined_blocks.title} выбран"
            )


class CableMagazineCreateForm(forms.ModelForm):
    class Meta:
        model = CableMagazine
        fields = (
            "cable",
            "subsystem",
            "number_mine",
            "inclined_blocks",
            "track_from",
            "track_to",
            # "track_to_phone",
            "distance",
            "unit",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["number_mine"].queryset = NumberMine.objects.exclude(title="Все шахты")
        self.fields["inclined_blocks"].queryset = InclinedBlocks.objects.exclude(title="Все уклонные блоки")
        self.fields["subsystem"].queryset = Subsystem.objects.exclude(title="Все подсистемы")
        # self.fields['cable_bool'].queryset = CableMagazine.objects.select_related(
        #         'cable_bool__cable_magazine').all()

        self.fields["cable"].empty_label = "Выберите кабель"
        self.fields["subsystem"].empty_label = "Выберите подсистему"
        self.fields["number_mine"].empty_label = "Выберите шахту"
        self.fields["inclined_blocks"].empty_label = "Выберите уклонный блок"
        self.fields["track_from"].empty_label = "Выберите начало трассы"
        self.fields["track_to"].empty_label = "Выберите окончание трассы"
        # self.fields["track_to_phone"].empty_label = "Выберите точку телефонии"
        self.fields["unit"].empty_label = "Выберите единицу измерения"
        # self.fields['cable_bool'].empty_label = "Выберите значение после фиксирования выполнения в отчете"

    def clean(self):
        cleaned_data = super().clean()
        track_from = cleaned_data.get("track_from")
        track_to = cleaned_data.get("track_to")
        # track_to_phone = cleaned_data.get("track_to_phone")

        if track_from is None:
            self.add_error("track_from", "Поле обязательно для заполнения")

        if track_to is None:
            self.add_error("track_to", "Поле обязательно для заполнения")

        # if track_to_box and track_to_phone:
        #     self.add_error("track_to_phone", "Выберите только одно поле")


class ViolationsCreateForm(forms.ModelForm):
    class Meta:
        model = Violations
        fields = (
            "number_act",
            "date_act",
            "issued_by_act",
            "number_mine",
            "title",
            "execution_bool",
            "file_act",
            "file_notification",
        )
        widgets = {
            "number_act": forms.TextInput(
                attrs={
                    "placeholder": "№1-2024/12",
                }
            ),
            "date_act": forms.TextInput(
                attrs={
                    "placeholder": "23.02.2025",
                }
            ),
            "issued_by_act": forms.TextInput(
                attrs={
                    "placeholder": "УМиАП",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["number_mine"].queryset = NumberMine.objects.exclude(title="Все шахты")
        self.fields["number_mine"].empty_label = "Выберите шахту"

    def clean(self):
        cleaned_data = super().clean()
        number_act = cleaned_data.get("number_act")
        date_act = cleaned_data.get("date_act")
        issued_by_act = cleaned_data.get("issued_by_act")
        title = cleaned_data.get("title")

        if number_act is None:
            self.add_error("number_act", "Укажите номер акта")

        if date_act is None:
            self.add_error("date_act", "Укажите дату акта")

        if issued_by_act is None:
            self.add_error("issued_by_act", "Укажите кем выдан акт")

        if title is None:
            self.add_error("title", "Опишите нарушение")


class VisualCreateNewForm(forms.ModelForm):
    class Meta:
        model = Visual
        fields = ("number_mine", "subsystem", "equipment", "cable", "file_pdf")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["number_mine"].queryset = NumberMine.objects.exclude(title="Все шахты")
        self.fields["number_mine"].empty_label = "Выберите шахту"
        self.fields["subsystem"].queryset = Subsystem.objects.exclude(title="Все подсистемы")
        self.fields["subsystem"].empty_label = "Выберите подсистему"
        self.fields["equipment"].queryset = Equipment.objects.exclude(title="Все оборудование")
        self.fields["equipment"].empty_label = "Выберите оборудование"
        self.fields["cable"].queryset = Cable.objects.exclude(title="Все кабели")
        self.fields["cable"].empty_label = "Выберите кабель"

    def clean(self):
        cleaned_data = super().clean()
        number_mine = cleaned_data.get("number_mine")
        subsystem = cleaned_data.get("subsystem")
        equipment = cleaned_data.get("equipment")
        cable = cleaned_data.get("cable")
        file_pdf = cleaned_data.get("file_pdf")

        if number_mine is None:
            self.add_error("number_mine", "Укажите нефтешахту")

        if subsystem is None:
            self.add_error("subsystem", "Укажите подсистему")

        if equipment and cable:
            self.add_error("equipment", "Укажите один из пунктов")
            self.add_error("cable", "Укажите один из пунктов")

        if file_pdf is None:
            self.add_error("file_pdf", "Загрузите файл в формате PDF, JPEG или PNG")


class CreateEquipmentInstallationForm(forms.ModelForm):

    inclined_blocks = CustomModelChoiceField(
        queryset=InclinedBlocks.objects.none(),  # Укажите правильный queryset
        to_field_name="title",  # Указываем, что значение для отправки — это `title`
        label="Уклонный блок",  # Укажите нужный label
        required=False,  # Разрешаем пустое значение
    )

    class Meta:
        model = EquipmentInstallation
        fields = (
            "title",
            "point_phone",
            "branches_box",
            "name",
            "serial_number",
            "ip_address",
            "subsystem",
            "number_mine",
            "tunnel",
            "inclined_blocks",
            "picket",
            "device_type",
            "description",
            "file_graphics",
        )
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "placeholder": "Например: TD101",
                }
            ),
            "picket": forms.TextInput(
                attrs={
                    "placeholder": "Например: 175 или 175+3",
                }
            ),
            "ip_address": forms.TextInput(
                attrs={
                    "placeholder": "10.10.110.110",
                    "class": "ip-input",  # для JS-обработки
                }
            ),
            "serial_number": forms.TextInput(
                attrs={
                    "placeholder": "Например: 777",
                }
            ),
            "device_type": forms.TextInput(
                attrs={
                    "placeholder": "Например: Эльтон-Ex231",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Динамически устанавливаем queryset для поля inclined_blocks
        if self.instance and self.instance.number_mine:
            self.fields["inclined_blocks"].queryset = InclinedBlocks.objects.filter(
                number_mine=self.instance.number_mine
            )
        else:
            self.fields["inclined_blocks"].queryset = InclinedBlocks.objects.all()

        self.fields["point_phone"].empty_label = "Ничего не выбрано"
        self.fields["branches_box"].empty_label = "Ничего не выбрано"
        self.fields["title"].empty_label = "Данное поле обязательно всегда"
        self.fields["title"].queryset = Equipment.objects.exclude(title="Все оборудование")
        self.fields["subsystem"].empty_label = "Ничего не выбрано"
        self.fields["subsystem"].queryset = Subsystem.objects.exclude(title="Все подсистемы")
        self.fields["number_mine"].empty_label = "Ничего не выбрано"
        self.fields["number_mine"].queryset = NumberMine.objects.exclude(title="Все шахты")
        self.fields["tunnel"].empty_label = "Ничего не выбрано"
        self.fields["inclined_blocks"].empty_label = "Ничего не выбрано"
        self.fields["inclined_blocks"].queryset = InclinedBlocks.objects.exclude(title="Все уклонные блоки")

        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.layout = Layout(
            Field("title"),
            Field("point_phone"),
            Field("branches_box"),
            HTML(
                '<p><u><font color="#6d37ff">Далее значения не обязательны если выбрана точка телефонии или '
                "распред.коробка</font></u></p>"
            ),
            Field("name"),
            Field("device_type"),
            Field("serial_number"),
            Field("ip_address"),
            Field("subsystem"),
            Field("number_mine"),
            Field("tunnel"),
            Field("inclined_blocks"),
            Field("picket"),
            # Field("file_graphics"),
        )

    def clean(self):
        cleaned_data = super().clean()
        point_phone = cleaned_data.get("point_phone")
        branches_box = cleaned_data.get("branches_box")
        title = cleaned_data.get("title")
        name = cleaned_data.get("name")
        subsystem = cleaned_data.get("subsystem")
        number_mine = cleaned_data.get("number_mine")
        tunnel = cleaned_data.get("tunnel")
        inclined_blocks = cleaned_data.get("inclined_blocks")
        picket = cleaned_data.get("picket")
        serial_number = cleaned_data.get("serial_number")
        device_type = cleaned_data.get("device_type")

        if point_phone and branches_box:
            self.add_error("point_phone", "Укажите одну позицию")
            self.add_error("branches_box", "Укажите одну позицию")

        if point_phone and title is None:
            self.add_error("title", "Укажите наименование оборудования")

        if branches_box and title is None:
            self.add_error("title", "Укажите наименование оборудования")

        if serial_number is None:
            self.add_error("serial_number", "Укажите заводской номер")

        if serial_number:
            for item in serial_number:
                if not item.isdigit():
                    self.add_error("serial_number", f"Заводской номер должен быть числом")

        if point_phone is not None and (name or number_mine or tunnel or inclined_blocks or picket):
            if branches_box is None:
                if name:
                    self.add_error("name", "При выборе точки телефонии данное поле не указывается")
                if number_mine:
                    self.add_error("number_mine", "При выборе точки телефонии данное поле не указывается")
                if tunnel:
                    self.add_error("tunnel", "При выборе точки телефонии данное поле не указывается")
                if inclined_blocks:
                    self.add_error("inclined_blocks", "При выборе точки телефонии данное поле не указывается")
                if picket:
                    self.add_error("picket", "При выборе точки телефонии данное поле не указывается")
                if device_type:
                    self.add_error("device_type", "При выборе точки телефонии данное поле не указывается")

        if branches_box is not None and (name or subsystem or number_mine or tunnel or inclined_blocks or picket):
            if point_phone is None:
                if name:
                    self.add_error("name", "При выборе распределительной коробки данное поле не указывается")
                if subsystem:
                    self.add_error("subsystem", "При выборе распределительной коробки данное поле не указывается")
                if number_mine:
                    self.add_error("number_mine", "При выборе распределительной коробки данное поле не указывается")
                if tunnel:
                    self.add_error("tunnel", "При выборе распределительной коробки данное поле не указывается")
                if inclined_blocks:
                    self.add_error(
                        "inclined_blocks", "При выборе распределительной коробки данное поле не указывается"
                    )
                if picket:
                    self.add_error("picket", "При выборе распределительной коробки данное поле не указывается")
                if device_type:
                    self.add_error("device_type", "При выборе распределительной коробки данное поле не указывается")

        if title is None:
            self.add_error("title", "Укажите наименование оборудования")

        if point_phone is None and branches_box is None and name is None:
            self.add_error("name", "Поле не должно быть пустым")

        if point_phone is None and branches_box is None and subsystem is None:
            self.add_error("subsystem", "Поле не должно быть пустым")

        if point_phone is None and branches_box is None and number_mine is None:
            self.add_error("number_mine", "Поле не должно быть пустым")

        if point_phone is None and branches_box is None and tunnel is None:
            self.add_error("tunnel", "Поле не должно быть пустым")

        # if point_phone is None and branches_box is None and picket is None:
        #     self.add_error('picket', 'Поле не должно быть пустым')

        if point_phone and subsystem is None:
            self.add_error("subsystem", "Поле не должно быть пустым")

        if tunnel is not None:
            if tunnel.inclined_blocks is not None and inclined_blocks is None:
                self.add_error("inclined_blocks", f"Выберите уклонный блок {tunnel.inclined_blocks.title}")
            if tunnel.inclined_blocks != inclined_blocks and inclined_blocks is not None:
                self.add_error("inclined_blocks", "Укажите уклонный блок верно")


class CreateExecutionForm(forms.ModelForm):
    class Meta:
        model = Execution
        fields = ("equipment_install", "cable_magazine", "execution_bool", "date_start", "date_end")
        widgets = {
            "date_start": forms.TextInput(
                attrs={
                    "placeholder": "11.01.2024",
                }
            ),
            "date_end": forms.TextInput(
                attrs={
                    "placeholder": "12.01.2024",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["equipment_install"].empty_label = "Выберите оборудование"
        self.fields["cable_magazine"].empty_label = "Выберите кабель"

        if self.instance and self.instance.date_start:
            self.initial["date_start"] = self.instance.date_start.strftime("%d.%m.%Y")

        if self.instance and self.instance.date_end:
            self.initial["date_end"] = self.instance.date_end.strftime("%d.%m.%Y")

    def clean(self):
        cleaned_data = super().clean()
        equipment_install = cleaned_data.get("equipment_install")
        date_start = cleaned_data.get("date_start")
        date_end = cleaned_data.get("date_end")

        if date_start and date_end:
            if date_start > date_end:
                self.add_error("date_end", "Дата завершения не может быть раньше даты начала")


class CreateDateUpdateForm(forms.ModelForm):
    class Meta:
        model = DateUpdate
        fields = ("update", "description")
        widgets = {
            "update": forms.DateTimeInput(
                format="%d.%m.%Y %H:%M:%S",  # Формат "дд.мм.гггг чч:мм:сс"
                attrs={"placeholder": "дд.мм.гггг чч:мм:сс"},
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Устанавливаем текущую дату (без времени)
        now = timezone.localtime(timezone.now())  # Конвертирует UTC в локальное время
        self.fields["update"].initial = now
