from django import forms
from infoMFSS.models import Execution, NumberMine, Subsystem, InclinedBlocks, Equipment, Cable, BranchesBox, Visual, \
    EquipmentInstallation, CableMagazine
from django.core.exceptions import ValidationError


class InfoFormMixin(forms.ModelForm):
    number_mines = forms.ModelChoiceField(
            queryset=NumberMine.objects.all(), to_field_name="title", label='Шахта',
            initial='Все шахты'
    )
    subsystems = forms.ModelChoiceField(
            queryset=Subsystem.objects.all(), to_field_name="title", label='Подсистема',
            initial='Все подсистемы'
    )

    class Meta:
        model = Execution
        fields = ('number_mines', 'subsystems',)


class PercentForm(InfoFormMixin):
    incl_blocks = forms.ModelChoiceField(
            queryset=InclinedBlocks.objects.all(), to_field_name="title", label='Уклонный блок',
            initial='Все уклонные блоки'
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
                raise forms.ValidationError('Не верно указан уклонный блок')

        if number_mines == 'Все шахты' and subsystems == 'Все подсистемы' and incl_blocks in incl_all_list:
            raise forms.ValidationError('Нефтешахта не выбрана')

        if number_mines == 'Все шахты' and subsystems in subsystems_list and incl_blocks in incl_all_list:
            raise forms.ValidationError('Нефтешахта не выбрана')


class EquipmentForm(InfoFormMixin):
    incl_blocks = forms.ModelChoiceField(
            queryset=InclinedBlocks.objects.all(), to_field_name="title", label='Уклонный блок',
            initial='Все уклонные блоки'
    )
    equipment = forms.ModelChoiceField(
            queryset=Equipment.objects.all(), to_field_name="title", label='Оборудование',
            initial='Все оборудование'
    )

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.fields['equipment'].queryset = Equipment.objects.filter(subsystem=self.initial.subsystems)


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


class ProjectEquipmentForm(InfoFormMixin):
    pass


class ProjectCableForm(InfoFormMixin):
    pass


class VisualCreateForm(forms.ModelForm):
    class Meta:
        model = Visual
        fields = ('number_mines', 'equipment')


class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, label="Ваше имя")
    email = forms.EmailField(label="Ваш email")
    message = forms.CharField(widget=forms.Textarea, label="Сообщение")

