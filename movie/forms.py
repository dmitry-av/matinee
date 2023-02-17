from django import forms
from django.contrib.auth import get_user_model

UserModel = get_user_model()


class SearchForm(forms.Form):
    term = forms.CharField(required=False)
