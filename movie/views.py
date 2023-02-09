from django.shortcuts import render

from movie.models import Movie


def index(request):
    movies = Movie.objects.all()
    return render(request, "movie/index.html", {"movies": movies})
