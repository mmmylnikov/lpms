from django import forms

from user.models import User


class UserUpdateForm(forms.ModelForm):
    first_name = forms.CharField(label='Имя',
                                 widget=forms.TextInput(
                                     attrs={'class': 'form-control'}))
    last_name = forms.CharField(label='Фамилия',
                                widget=forms.TextInput(
                                    attrs={'class': 'form-control'}))
    tg_username = forms.CharField(label='Telegram',
                                  widget=forms.TextInput(
                                      attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'tg_username', ]
