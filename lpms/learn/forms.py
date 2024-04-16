from django import forms
from django.urls import reverse_lazy
from learn.models import Homework


class TaskUpdateForm(forms.ModelForm):
    repo = forms.CharField(label='Ссылка на пулл-реквест',
                           widget=forms.TextInput(
                               attrs={
                                'class': 'form-control',
                                'list': 'repo_options',
                                'placeholder': 'начните вводить '
                                               'название репозитория',
                                'hx-get': reverse_lazy(
                                    'pull_autocomplete_view'),
                                'hx-target': "#repo_options",
                                'hx-trigger': "load, keyup delay:2000ms",
                                }))
    comment = forms.CharField(label='Комментарий', required=False,
                              widget=forms.Textarea(
                                  attrs={'class': 'form-control', 'rows': 2}))

    class Meta:
        model = Homework
        fields = ['repo', 'comment', ]
