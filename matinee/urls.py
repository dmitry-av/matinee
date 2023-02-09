"""matinee URL Configuration
"""
from django.contrib import admin
from django.urls import path

import movie.views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", movie.views.index),
]
