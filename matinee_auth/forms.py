from django_registration.forms import RegistrationForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django_registration.forms import RegistrationForm
from django import forms

from matinee_auth.models import User


class MatineeRegistrationForm(RegistrationForm):
    first_name = forms.CharField(required=True)

    class Meta(RegistrationForm.Meta):
        model = User
        fields = ("email", "first_name", "last_name", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super(MatineeRegistrationForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit("submit", "Register"))
