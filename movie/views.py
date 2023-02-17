import logging
from datetime import timedelta


from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.core.exceptions import PermissionDenied
from django.utils import timezone

from movie.models import Movie, Showtime, Invitation
from movie.forms import SearchForm, ShowtimeForm, InviteeForm, AttendanceForm
from .omdb_integration import search_and_save, fill_movie_details

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


@login_required
def movie_detail(request, imdb_id):
    movie = get_object_or_404(Movie, imdb_id=imdb_id)
    fill_movie_details(movie)
    if request.method == "POST":
        showtime_form = ShowtimeForm(request.POST)
        if movie_night_form.is_valid():
            showtime = showtime_form.save(False)
            showtime.movie = movie
            showtime.creator = request.user
            showtime.save()
            return redirect("movie_night_detail_ui", showtime.pk)
    else:
        movie_night_form = ShowtimeForm()
    return render(
        request,
        "movies/movie_detail.html",
        {"page_group": "search", "movie": movie,
            "showtime_form": showtime_form},
    )


@login_required
def showtime_detail(request, pk):
    showtime = get_object_or_404(Showtime, pk=pk)

    is_creator = showtime.creator == request.user

    invitee_form = None
    attendance_form = None

    invitees = {invitation.invitee for invitation in showtime.invites.all()}

    in_the_past = showtime.start_time < timezone.now()

    if not is_creator:
        if request.user not in invitees:
            raise PermissionDenied(
                "You do not have access to this Showtime event")

        invitation = showtime.invites.filter(invitee=request.user).first()

        if not in_the_past and request.method == "POST":
            attendance_form = AttendanceForm(request.POST, instance=invitation)
            if attendance_form.is_valid():
                attendance_form.save()
        else:
            attendance_form = AttendanceForm(instance=invitation)
    else:
        if not in_the_past and request.method == "POST":
            invitee_form = InviteeForm(request.POST)

            if invitee_form.is_valid():
                invitee = invitee_form._user

                if invitee == request.user or invitee in invitees:
                    invitee_form.add_error(
                        "email", "That user is the creator or already invited"
                    )
                else:
                    Invitation.objects.create(
                        invitee=invitee, showtime=showtime
                    )
                    # effectively, just reload the page
                    return redirect(request.path)
        else:
            invitee_form = InviteeForm()

    return render(
        request,
        "movies/showtime_detail.html",
        {
            "page_group": "movie-nights",
            "showtime": showtime,
            "is_creator": is_creator,
            "invitee_form": invitee_form,
            "attendance_form": attendance_form,
            "in_the_past": in_the_past,
        },
    )
