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

    # movie urls
    path("", movie.views.index),
    path("search/", movie.views.movie_search, name="movie_search"),
    path("showtimes/", movie.views.showtime_list, name="showtime_list"),
    path("showtime/<int:pk>/", movie.views.showtime_detail,
         name="showtime_detail"),
    path("movies/<slug:imdb_id>/", movie.views.movie_detail, name="movie_detail"),
    path("showtimes/<int:pk>/", movie.views.showtime_detail,
         name="showtime_detail"),
]
