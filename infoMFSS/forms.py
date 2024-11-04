from django import forms
from infoMFSS.models import Execution


class SubsystemForm(forms.ModelForm):
    class Meta:
        model = Execution
        fields = ('number_mine', 'subsystem',)
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