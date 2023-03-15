from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework.authtoken import views


from movie.api.views import MovieViewSet, ShowtimeViewSet, InvitationViewSet, GenreViewSet

schema_view = get_schema_view(
    openapi.Info(
        title="Matinee API",
        default_version="v1",
        description="API for Matinee",
    ),
    public=True,
)


router = DefaultRouter()
router.register("movies", MovieViewSet)
router.register("showtimes", ShowtimeViewSet, basename="showtime")
router.register(
    "showtime-invitations",
    InvitationViewSet,
    basename="invitation",
)
router.register("genres", GenreViewSet)

urlpatterns = [path("", include(router.urls))]

urlpatterns += [
    path("auth/", include("rest_framework.urls")),
    path("token-auth/", views.obtain_auth_token),
    re_path(r"^swagger(?P<format>\.json|\.yaml)$",
            schema_view.without_ui(cache_timeout=0), name="schema-json"),
    path("swagger/", schema_view.with_ui("swagger",
         cache_timeout=0), name="schema-swagger-ui"),
]
