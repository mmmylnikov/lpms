from typing import Any

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

    def clean(self) -> dict[str, Any] | None:
        cleaned_data = super().clean()
        if not cleaned_data:
            return None
        repo = cleaned_data.get('repo')
        if not repo:
            return cleaned_data
        validation_error = self.instance.pull_request_policy_validator(
            pr_url=repo
        )
        if validation_error:
            self.add_error('repo', validation_error)
        return cleaned_data

    class Meta:
        model = Homework
        fields = ['repo', 'comment', ]


class ReviewUpdateForm(forms.ModelForm):
    tutor_comment = forms.CharField(
        label='Комментарий к работе (опционально)', required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2}))

    class Meta:
        model = Homework
        fields = ['tutor_comment', ]
