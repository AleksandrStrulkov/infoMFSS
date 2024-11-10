from django import forms
from infoMFSS.models import Execution, NumberMine, Subsystem, InclinedBlocks


# class SubsystemForm(forms.ModelForm):
#     class Meta:
#         model = Execution
#         fields = ('number_mine', 'subsystem',)


class SubsystemForm(forms.ModelForm):
    number_mines = forms.ModelChoiceField(queryset=NumberMine.objects.all(), to_field_name="title", label='Шахта',
                                          help_text='Укажите нефтешахту', blank=True)
    subsystems = forms.ModelChoiceField(queryset=Subsystem.objects.all(), label='Подсистема', to_field_name="title",
                                        help_text='Укажите подсистему', blank=True)
    incl_blocks = forms.ModelChoiceField(queryset=InclinedBlocks.objects.all(),
                                         label='Уклонный блок', to_field_name="title",
                                         help_text='Укажите уклонный блок', blank=True)

    class Meta:
        model = Execution
        fields = ('number_mines', 'subsystems', 'incl_blocks',)

    # def __init__(self, *args, **kwargs):
    #     # super().__init__(*args, **kwargs)
    #
    #     super(SubsystemForm, self, ).__init__(*args, **kwargs)
    #     if 'number_mines' in kwargs:
    #         self.number_mines = kwargs.pop('number_mines')
    #     else:
    #         self.number_mines = None
    #     # super(self, SubsystemForm).__init__(*args, **kwargs)
    #     if self.number_mines:
    #         self.fields['incl_blocks'].queryset = InclinedBlocks.objects.filter(number_mine=self.number_mines)
    #     else:
    #         self.fields['incl_blocks'].queryset = InclinedBlocks.objects.all()

    # if form.is_valid():
    #     mine = form.cleaned_data.get("number_mine")
    # self.fields['subsystems'].queryset = Subsystem.objects.filter(number_mine__title=mine)

    # self.fields['incl_blocks'].queryset = InclinedBlocks.objects.filter(number_mine__title=mine)

    # fields = ('subsystem__title',)

# def __init__(self, *args, **kwargs):
#     super().__init__(*args, **kwargs)
#     self.fields['number_mine'].queryset = self.fields['number_mine'].queryset.filter(is_active=True)

# from django import forms


#
# from django import forms
#
#
# class UserForm(forms.Form):
#
#     number_mine = forms.CharField(max_length=100)
#     sub_system = forms.CharField(max_length=100)
# email = forms.EmailField()
# email = forms.EmailField()
