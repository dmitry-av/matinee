from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

from movie.models import Showtime, Invitation

UserModel = get_user_model()


class SearchForm(forms.Form):
    term = forms.CharField(required=False)


class ShowtimeForm(forms.ModelForm):
    class Meta:
        model = Showtime
        fields = ["start_time"]

    def __init__(self, *args, **kwargs):
        super(ShowtimeForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit("submit", "Create"))


class InviteForm(forms.Form):
    email = forms.EmailField()

    _user = False

    def __init__(self, *args, **kwargs):
        super(InviteForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit("submit", "Invite"))

    def clean_email(self):
        email = self.cleaned_data["email"]
        try:
            # cache for later
            self._user = UserModel.objects.get(email=email)
        except UserModel.DoesNotExist:
            raise ValidationError(
                f"User with email address '{email}' was not found.")

        return email


class AttendForm(forms.ModelForm):
    class Meta:
        model = Invitation
        fields = ["is_attending"]

    def __init__(self, *args, **kwargs):
        super(AttendForm, self).__init__(*args, **kwargs)
        self.fields["is_attending"].label = "Attending?"
        self.helper = FormHelper()
        self.helper.add_input(Submit("submit", "Update Attendance"))
