from itertools import chain
from django.db.models import Case, When, Value, IntegerField
from django import forms
from infoMFSS.models import Execution, NumberMine, Subsystem, InclinedBlocks, Equipment, Cable, BranchesBox, Visual, \
    EquipmentInstallation, CableMagazine, PointPhone
from captcha.fields import CaptchaField


class InfoFormMixin(forms.Form):
    number_mines = forms.ModelChoiceField(
            queryset=NumberMine.objects.none(), to_field_name="title", label='Шахта',
            initial='Все шахты'
    )
    subsystems = forms.ModelChoiceField(
            queryset=Subsystem.objects.none(), to_field_name="title", label='Подсистема',
            initial='Все подсистемы'
    )
    incl_blocks = forms.ModelChoiceField(
            queryset=InclinedBlocks.objects.none(), to_field_name="title", label='Уклонный блок',
            initial='Все уклонные блоки',
    )

    def clean(self):
        cleaned_data = super().clean()
        number_mines = cleaned_data.get('number_mines').title
        subsystems = cleaned_data.get('subsystems').title
        incl_blocks = cleaned_data.get('incl_blocks').title
        incl_in_mines = InclinedBlocks.objects.filter(number_mine__title__icontains=number_mines)
        incl_all_blocks = InclinedBlocks.objects.all()
        subsystems_all = Subsystem.objects.all()
        incl_list = []
        incl_all_list = []
        subsystems_list = []

        for incl_in_mine in incl_in_mines:
            incl_list.append(incl_in_mine.title)
            incl_list.append('Все уклонные блоки')

        for incl_all_block in incl_all_blocks:
            incl_all_list.append(incl_all_block.title)

        for subsystem_all in subsystems_all:
            subsystems_list.append(subsystem_all.title)

        incl_all_list.remove('Все уклонные блоки')

        if incl_in_mines:
            if incl_blocks not in incl_list:
                self.add_error('incl_blocks', 'Не верно указан уклонный блок')

        if number_mines == 'Все шахты' and subsystems in subsystems_list and incl_blocks in incl_all_list:
            self.add_error('number_mines', 'Нефтешахта не выбрана')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Добавляем "Все шахты" и реальные объекты
        all_number_mines_option = NumberMine.objects.filter(title='Все шахты').first()
        if all_number_mines_option:
            self.fields['number_mines'].queryset = NumberMine.objects.annotate(
                    custom_order=Case(
                            When(id=all_number_mines_option.id, then=Value(0)),  # "Все шахты" получает порядок 0
                            default=Value(1),  # Все остальные получают порядок 1
                            output_field=IntegerField(),
                    )
            ).order_by('custom_order', 'title')
        else:
            self.fields['number_mines'].queryset = NumberMine.objects.all()

        all_subsystems_option = Subsystem.objects.filter(title='Все подсистемы').first()
        if all_subsystems_option:
            self.fields['subsystems'].queryset = Subsystem.objects.annotate(
                    custom_order=Case(
                            When(id=all_subsystems_option.id, then=Value(0)),  # "Все шахты" получает порядок 0
                            default=Value(1),  # Все остальные получают порядок 1
                            output_field=IntegerField(),
                    )
            ).order_by('custom_order', 'title')
        else:
            self.fields['subsystems'].queryset = Subsystem.objects.all()

        # Добавляем "Все шахты" и реальные объекты
        all_blocks_option = InclinedBlocks.objects.filter(title='Все уклонные блоки').first()
        if all_blocks_option:
            self.fields['incl_blocks'].queryset = InclinedBlocks.objects.annotate(
                    custom_order=Case(
                            When(id=all_blocks_option.id, then=Value(0)),  # "Все шахты" получает порядок 0
                            default=Value(1),  # Все остальные получают порядок 1
                            output_field=IntegerField(),
                    )
            ).order_by('custom_order', 'number_mine')
        else:
            self.fields['incl_blocks'].queryset = InclinedBlocks.objects.all()


class InfoProjectFormMixin(InfoFormMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop('incl_blocks')

    def clean(self):
        return self.cleaned_data


class PercentForm(InfoFormMixin):
    pass


class EquipmentForm(InfoFormMixin):
    equipment = forms.ModelChoiceField(
            queryset=Equipment.objects.none(), to_field_name="title", label='Оборудование',
            initial='Все оборудование'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Добавляем "Все шахты" и реальные объекты
        all_equipment_option = Equipment.objects.filter(title='Все оборудование').first()
        if all_equipment_option:
            self.fields['equipment'].queryset = Equipment.objects.annotate(
                    custom_order=Case(
                            When(id=all_equipment_option.id, then=Value(0)),  # "Все шахты" получает порядок 0
                            default=Value(1),  # Все остальные получают порядок 1
                            output_field=IntegerField(),
                    )
            ).order_by('custom_order', 'title')
        else:
            self.fields['equipment'].queryset = Equipment.objects.all()


class CableForm(InfoFormMixin):
    cable = forms.ModelChoiceField(
            queryset=Cable.objects.none(), to_field_name="title", label='Кабель',
            initial='Все кабели'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Добавляем "Все шахты" и реальные объекты
        all_cable_option = Cable.objects.filter(title='Все кабели').first()
        if all_cable_option:
            self.fields['cable'].queryset = Cable.objects.annotate(
                    custom_order=Case(
                            When(id=all_cable_option.id, then=Value(0)),  # "Все шахты" получает порядок 0
                            default=Value(1),  # Все остальные получают порядок 1
                            output_field=IntegerField(),
                    )
            ).order_by('custom_order', 'title')
        else:
            self.fields['cable'].queryset = Cable.objects.all()


class BoxForm(InfoFormMixin):
    pass


class ProjectEquipmentForm(InfoProjectFormMixin):
    pass


class ProjectCableForm(InfoProjectFormMixin):
    pass


class VisualCreateForm(forms.ModelForm):
    class Meta:
        model = Visual
        fields = ('number_mines', 'equipment')


class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, label="Ваше имя")
    email = forms.EmailField(label="Ваш email")
    message = forms.CharField(widget=forms.Textarea, label="Сообщение")
    captcha = CaptchaField(
        label='Введите ответ', generator='captcha.helpers.math_challenge',
        error_messages={'invalid': 'Неправильный ответ'}, )


class QuantityEquipmentCableForm(forms.Form):
    number_mines = forms.ChoiceField(
            choices=[
                    ('Нефтешахта №1', 'Нефтешахта №1'),
                    ('Нефтешахта №2', 'Нефтешахта №2'),
                    ('Нефтешахта №3', 'Нефтешахта №3'),
            ],
            label="Выберите шахту", required=True
    )
    equipment = forms.ModelChoiceField(
            queryset=Equipment.objects.exclude(title='Все оборудование'), to_field_name="title", label='Оборудование',
            required=False, empty_label="Не выбрано"
    )
    cable = forms.ModelChoiceField(
            queryset=Cable.objects.exclude(title='Все кабели'), to_field_name="title", label='Кабель',
            required=False, empty_label="Не выбрано"
    )

    def clean(self):
        cleaned_data = super().clean()
        equipment = cleaned_data.get('equipment')
        cable = cleaned_data.get('cable')

        if equipment is None and cable is None:
            self.add_error('equipment', 'Не выбрано оборудование')
            self.add_error('cable', 'Не выбран кабель')

        if equipment and cable:
            self.add_error('equipment', 'Выберите только один из вариантов')


class EquipmentCreateForm(forms.ModelForm):
    class Meta:
        model = Equipment
        fields = ('title', 'description', 'subsystem', 'file_pdf', 'file_passport', 'file_certificate',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['subsystem'].queryset = Subsystem.objects.exclude(title="Все подсистемы")

        for field_name, field in self.fields.items():
            if isinstance(field, forms.ModelChoiceField):
                field.empty_label = "Выберите значение"

    def clean(self):
        cleaned_data = super().clean()
        subsystem = cleaned_data.get('subsystem')

        if subsystem is None:
            self.add_error('subsystem', 'Подсистема не выбрана')


class CableCreateForm(forms.ModelForm):
    class Meta:
        model = Cable
        fields = ('title', 'description', 'file_pdf', 'file_passport', 'file_certificate',)


class PointPhoneCreateForm(forms.ModelForm):
    class Meta:
        model = PointPhone
        fields = ('title', 'number_mine', 'tunnel', 'inclined_blocks', 'subscriber_number', 'picket', 'description')
        required = True
        widgets = {
                'title': forms.TextInput(
                        attrs={
                                'placeholder': 'T1-65',
                        }
                ),
                'subscriber_number': forms.TextInput(
                        attrs={
                                'placeholder': '8777',
                        }
                ),
                'picket': forms.TextInput(
                        attrs={
                                'placeholder': '12',
                        }
                ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['number_mine'].queryset = NumberMine.objects.exclude(title="Все шахты")
        self.fields['inclined_blocks'].queryset = InclinedBlocks.objects.exclude(title="Все уклонные блоки")
        # self.fields['number_mine'].empty_label = "Выберите значение"

        for field_name, field in self.fields.items():
            if isinstance(field, forms.ModelChoiceField):
                field.empty_label = "Выберите значение"

    def clean(self):
        cleaned_data = super().clean()
        number_mine = cleaned_data.get('number_mine')
        tunnel = cleaned_data.get('tunnel')
        inclined_blocks = cleaned_data.get('inclined_blocks')
        title = cleaned_data.get('title')
        subscriber_number = cleaned_data.get('subscriber_number')

        if title is None:
            self.add_error('title', 'Укажите обозначение точки телефонии')

        if number_mine is None:
            self.add_error('number_mine', 'Нефтешахта не выбрана')

        if tunnel is None:
            self.add_error('tunnel', 'Выработка не выбрана')

        if subscriber_number is None:
            self.add_error('subscriber_number', 'Укажите абонентский номер')

        if tunnel.inclined_blocks is not None and inclined_blocks is None:
            self.add_error('inclined_blocks', f'Уклонный блок {tunnel.inclined_blocks.title} не выбран')



