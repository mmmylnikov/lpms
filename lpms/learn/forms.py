from django import forms

from learn.models import Homework


class TaskUpdateForm(forms.ModelForm):
    repo = forms.CharField(label='Ссылка на пулл-реквест',
                           widget=forms.TextInput(
                               attrs={'class': 'form-control'}))
    comment = forms.CharField(label='Комментарий', required=False,
                              widget=forms.Textarea(
                                  attrs={'class': 'form-control', 'rows': 2}))

    class Meta:
        model = Homework
        fields = ['repo', 'comment', ]
