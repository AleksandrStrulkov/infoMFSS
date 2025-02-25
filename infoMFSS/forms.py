from django import forms
from infoMFSS.models import Execution, NumberMine, Subsystem, InclinedBlocks, Equipment, Cable, BranchesBox, Visual, \
    EquipmentInstallation, CableMagazine
import captcha as captcha
import captcha as captcha
from captcha.fields import CaptchaField


class InfoFormMixin(forms.Form):
    number_mines = forms.ModelChoiceField(
            queryset=NumberMine.objects.all(), to_field_name="title", label='Шахта',
            initial='Все шахты'
    )
    subsystems = forms.ModelChoiceField(
            queryset=Subsystem.objects.all(), to_field_name="title", label='Подсистема',
            initial='Все подсистемы'
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

        if 'Все уклонные блоки' in incl_all_list:

            incl_all_list.remove('Все уклонные блоки')

        if incl_in_mines:
            if incl_blocks not in incl_list:
                self.add_error('incl_blocks', 'Не верно указан уклонный блок')

        if number_mines == 'Все шахты' and subsystems in subsystems_list and incl_blocks in incl_all_list:
            self.add_error('number_mines', 'Нефтешахта не выбрана')


class PercentForm(InfoFormMixin):
    incl_blocks = forms.ModelChoiceField(
            queryset=InclinedBlocks.objects.all(), to_field_name="title", label='Уклонный блок',
            initial='Все уклонные блоки'
    )


class EquipmentForm(InfoFormMixin):
    incl_blocks = forms.ModelChoiceField(
            queryset=InclinedBlocks.objects.all(), to_field_name="title", label='Уклонный блок',
            initial='Все уклонные блоки'
    )
    equipment = forms.ModelChoiceField(
            queryset=Equipment.objects.all(), to_field_name="title", label='Оборудование',
            initial='Все оборудование'
    )


class CableForm(InfoFormMixin):
    incl_blocks = forms.ModelChoiceField(
            queryset=InclinedBlocks.objects.all(), to_field_name="title", label='Уклонный блок',
            initial='Все уклонные блоки'
    )
    cable = forms.ModelChoiceField(
            queryset=Cable.objects.all(), to_field_name="title", label='Кабель',
            initial='Все кабели'
    )


class BoxForm(InfoFormMixin):
    incl_blocks = forms.ModelChoiceField(
            queryset=InclinedBlocks.objects.all(), to_field_name="title", label='Уклонный блок',
            initial='Все уклонные блоки'
    )


class ProjectEquipmentForm(forms.Form):
    number_mines = forms.ModelChoiceField(
            queryset=NumberMine.objects.all(), to_field_name="title", label='Шахта',
            initial='Все шахты'
    )
    subsystems = forms.ModelChoiceField(
            queryset=Subsystem.objects.all(), to_field_name="title", label='Подсистема',
            initial='Все подсистемы'
    )


class ProjectCableForm(forms.Form):
    number_mines = forms.ModelChoiceField(
            queryset=NumberMine.objects.all(), to_field_name="title", label='Шахта',
            initial='Все шахты'
    )
    subsystems = forms.ModelChoiceField(
            queryset=Subsystem.objects.all(), to_field_name="title", label='Подсистема',
            initial='Все подсистемы'
    )


class VisualCreateForm(forms.ModelForm):
    class Meta:
        model = Visual
        fields = ('number_mines', 'equipment')


class ContactForm(forms.Form):

                           # widget=forms.TextInput(attrs={'class': 'captcha-input'}))
    name = forms.CharField(max_length=100, label="Ваше имя")
    email = forms.EmailField(label="Ваш email")
    message = forms.CharField(widget=forms.Textarea, label="Сообщение")
    captcha = CaptchaField(label='Введите ответ', generator='captcha.helpers.math_challenge',
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