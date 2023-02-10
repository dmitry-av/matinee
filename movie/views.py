from django.shortcuts import render

from movie.models import Movie
import logging

logger = logging.getLogger(__name__)


def index(request):
    movies = Movie.objects.all()
    logger.debug("Got %d movie objects", len(movies))
    return render(request, "movie/index.html", {"movies": movies})
