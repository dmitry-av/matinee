import logging
from datetime import timedelta


from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.core.exceptions import PermissionDenied
from django.utils import timezone

from movie.models import Movie, Showtime, Invitation
from movie.forms import SearchForm, ShowtimeForm, InviteForm, AttendForm
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
            "movie_list": movie_list,
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
        invites__in=Invitation.objects.filter(invited=request.user),
    )

    return render(
        request,
        "movie/showtime_list.html",
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
        if showtime_form.is_valid():
            showtime = showtime_form.save(False)
            showtime.movie = movie
            showtime.creator = request.user
            showtime.save()
            return redirect("showtime_detail", showtime.pk)
    else:
        showtime_form = ShowtimeForm()
    return render(
        request,
        "movie/movie_detail.html",
        {"page_group": "search",
         "movie": movie,
         "showtime_form": showtime_form},
    )


@login_required
def showtime_detail(request, pk):
    showtime = get_object_or_404(Showtime, pk=pk)

    is_creator = showtime.creator == request.user

    invite_form = None
    attend_form = None

    inviteds = {invitation.invited for invitation in showtime.invites.all()}

    in_the_past = showtime.start_time < timezone.now()

    if not is_creator:
        if request.user not in inviteds:
            raise PermissionDenied(
                "You do not have access to this Showtime event")

        invitation = showtime.invites.filter(invited=request.user).first()

        if not in_the_past and request.method == "POST":
            attend_form = AttendForm(request.POST, instance=invitation)
            if attend_form.is_valid():
                attend_form.save()
                # invitation.attendance_confirmed = not invitation.attendance_confirmed
                # invitation.save()
        else:
            attend_form = AttendForm(instance=invitation)
    else:
        if not in_the_past and request.method == "POST":
            invite_form = InviteForm(request.POST)

            if invite_form.is_valid():
                invited = invite_form._user

                if invited == request.user or invited in inviteds:
                    invite_form.add_error(
                        "email", "That user is the creator or already invited"
                    )
                else:
                    Invitation.objects.create(
                        invited=invited, showtime=showtime
                    )
                    # reload the page
                    return redirect(request.path)
        else:
            invite_form = InviteForm()

    return render(
        request,
        "movie/showtime_detail.html",
        {
            "page_group": "showtimes",
            "showtime": showtime,
            "is_creator": is_creator,
            "invite_form": invite_form,
            "attend_form": attend_form,
            "in_the_past": in_the_past,
        },
    )
