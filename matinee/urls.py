"""matinee URL Configuration
"""
from django.contrib import admin
from django.urls import path, include

from django_registration.backends.activation.views import RegistrationView

from matinee_auth.forms import MatineeRegistrationForm
import matinee_auth.views
import movie.views


urlpatterns = [
    path("admin/", admin.site.urls),
    # registration and login urls
    path("accounts/profile/", matinee_auth.views.profile, name="profile"),
    path(
        "accounts/register/",
        RegistrationView.as_view(form_class=MatineeRegistrationForm),
        name="django_registration_register",
    ),
    path("accounts/", include("django_registration.backends.activation.urls")),
    path("accounts/", include("django.contrib.auth.urls")),

    # main app urls
    path("", movie.views.index),
]
