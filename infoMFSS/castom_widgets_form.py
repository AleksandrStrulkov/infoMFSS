from django.forms import Select
from django import forms
from django.forms import ModelChoiceField


class CustomModelChoiceField(ModelChoiceField):

    def label_from_instance(self, obj):
        # Возвращаем форматированное значение для отображения в выпадающем списке
        if obj.title == 'Все уклонные блоки':
            return obj.title
        else:
            return f'УБ {obj.title} (НШ-{obj.number_mine.title[-1]})'