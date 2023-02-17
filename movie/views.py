from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone

from movie.forms import SearchForm
from movie.models import Movie, Showtime, Invitation
from .omdb_integration import search_and_save

import logging
from datetime import timedelta

logger = logging.getLogger(__name__)


def index(request):
    return render(request, "movie/index.html")


@login_required
def movie_search(request):
    search_form = SearchForm(request.POST)

    if search_form.is_valid() and search_form.cleaned_data["term"]:
        term = search_form.cleaned_data["term"]
        search_and_save(term)
        movie_list = Movie.objects.filter(title__icontains=term)
        searched = True
    else:
        movie_list = []
        searched = False

    return render(
        request,
        "movie/search.html",
        {
            "page_group": "search",
            "search_form": search_form,
            "film_list": movie_list,
            "searched": searched,
        },
    )


@login_required
def showtime_list(request):
    start_time_after = timezone.now() - timedelta(hours=2)
    created_showtimes = Showtime.objects.filter(
        creator=request.user, start_time__gt=start_time_after
    )
    invited_showtimes = Showtime.objects.filter(
        start_time__gt=start_time_after,
        invites__in=Invitation.objects.filter(invitee=request.user),
    )

    return render(
        request,
        "movies/showtime_list.html",
        {
            "page_group": "showtimes",
            "created_showtimes": created_showtimes,
            "invited_showtimes": invited_showtimes,
        },
    )
