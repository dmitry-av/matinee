from django.contrib import admin
from movie.models import Movie, Showtime, Invitation, Genre

admin.site.register(Movie)
admin.site.register(Showtime)
admin.site.register(Invitation)
admin.site.register(Genre)
