from django import forms
from infoMFSS.models import Execution, NumberMine, Subsystem, InclinedBlocks


# class SubsystemForm(forms.ModelForm):
#     class Meta:
#         model = Execution
#         fields = ('number_mine', 'subsystem',)


class SubsystemForm(forms.ModelForm):
    number_mines = forms.ModelChoiceField(queryset=NumberMine.objects.all(), to_field_name="title", label='Шахта',
                                         help_text='Укажите нефтешахту', empty_label='Выберите один из пунктов списка',
                                          label_suffix='')
    subsystems = forms.ModelChoiceField(queryset=Subsystem.objects.all(), to_field_name="title", label='Подсистема',
                                         help_text='Укажите подсистему', empty_label='Выберите один из пунктов списка')

    incl_blocks = forms.ModelChoiceField(queryset=InclinedBlocks.objects.all(), label='Уклонный блок',
                                         to_field_name="title", help_text='Укажите уклонный блок',
                                         empty_label='Выберите один из пунктов списка')

    class Meta:
        model = Execution
        fields = ('number_mines', 'subsystems', 'incl_blocks',)
        # fields = ('number_mines',)

    def clean(self):
        cleaned_data = super().clean()
        number_mines = cleaned_data.get('number_mines')
        subsystems = cleaned_data.get('subsystems')
        incl_blocks = cleaned_data.get('incl_blocks')
        incl = InclinedBlocks.objects.filter(number_mine__title__icontains=number_mines)
        a = []
        for i in incl:
            a.append(i.title)
            a.append('Все уклонные блоки')


        if incl_blocks.title not in a:
            raise forms.ValidationError(f'Не то')

        return cleaned_data

