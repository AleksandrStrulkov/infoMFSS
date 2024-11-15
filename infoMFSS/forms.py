from django import forms
from infoMFSS.models import Execution, NumberMine, Subsystem, InclinedBlocks


class SubsystemForm(forms.ModelForm):
    number_mines = forms.ModelChoiceField(
        queryset=NumberMine.objects.all(), to_field_name="title", label='Шахта',
        initial='Все шахты'
        )
    subsystems = forms.ModelChoiceField(
        queryset=Subsystem.objects.all(), to_field_name="title", label='Подсистема',
        initial='Все подсистемы'
        )

    incl_blocks = forms.ModelChoiceField(
        queryset=InclinedBlocks.objects.all(), to_field_name="title", label='Уклонный блок',
        initial='Все уклонные блоки'
        )

    class Meta:
        model = Execution
        fields = ('number_mines', 'subsystems', 'incl_blocks',)
        # fields = ('number_mines',)

    def clean(self):
        cleaned_data = super().clean()
        number_mines = cleaned_data.get('number_mines').title
        subsystems = cleaned_data.get('subsystems').title
        incl_blocks = cleaned_data.get('incl_blocks').title
        incl_in_mines = InclinedBlocks.objects.filter(number_mine__title__icontains=number_mines)
        incl_all_blocks = InclinedBlocks.objects.all()
        incl_list = []
        incl_all_list = []

        for incl_in_mine in incl_in_mines:
            incl_list.append(incl_in_mine.title)
            incl_list.append('Все уклонные блоки')

        for incl_all_block in incl_all_blocks:
            incl_all_list.append(incl_all_block.title)

        incl_all_list.remove('Все уклонные блоки')

        if incl_in_mines:
            if incl_blocks not in incl_list:
                raise forms.ValidationError('Не верно указан уклонный блок')

        if number_mines == 'Все шахты' and subsystems == 'Все подсистемы' and incl_blocks in incl_all_list:
            raise forms.ValidationError('Нефтешахта не выбрана')