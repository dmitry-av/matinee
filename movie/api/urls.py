from django.urls import include, path
from rest_framework.routers import DefaultRouter

from movie.api.views import MovieViewSet, ShowtimeViewSet, InvitationViewSet, GenreViewSet

router = DefaultRouter()
router.register("movies", MovieViewSet)
router.register("movie-nights", ShowtimeViewSet, basename="showtime")
router.register(
    "showtime-invitations",
    InvitationViewSet,
    basename="showtimeinvitation",
)
router.register("genres", GenreViewSet)

urlpatterns = [path("", include(router.urls))]
