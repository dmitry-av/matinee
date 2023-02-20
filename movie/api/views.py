from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from django.shortcuts import redirect

from movie.omdb_integration import fill_movie_details, search_and_save
from movie.api.permissions import IsCreatorPermission, IsInvitedPermission
from movie.api.serializers import MovieSerializer, ShowtimeSerializer, InvitationSerializer, GenreSerializer, MovieSearchSerializer, InvitationCreationSerializer, ShowtimeCreateSerializer
from movie.models import Showtime, Invitation, Genre, Movie


class MovieViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer

    def get_object(self):
        movie = super().get_object()
        fill_movie_details(movie)
        return movie

    @action(methods=["get"], detail=False)
    def search(self, request):
        search_serializer = MovieSearchSerializer(data=request.GET)

        if not search_serializer.is_valid():
            return Response(search_serializer.errors)

        term = search_serializer.data["term"]

        search_and_save(term)

        movies = self.get_queryset().filter(title__icontains=term)

        page = self.paginate_queryset(movies)

        if page is not None:
            serializer = MovieSerializer(
                page, many=True, context={"request": request})
            return self.get_paginated_response(serializer.data)

        return Response(
            MovieSerializer(movies, many=True, context={
                            "request": request}).data
        )


class ShowtimeViewSet(viewsets.ModelViewSet):
    queryset = Showtime.objects.all()
    permission_classes = [IsAuthenticated | IsCreatorPermission]

    def get_serializer_class(self):
        if self.action in ("create"):
            return ShowtimeCreateSerializer
        return ShowtimeSerializer

    def get_object(self):
        showtime = super(ShowtimeViewSet, self).get_object()
        if (
            showtime.creator != self.request.user
            and showtime.invites.filter(invited=self.request.user).count() == 0
        ):
            raise PermissionDenied()
        return showtime

    def get_queryset(self):
        if self.action == "list":
            return self.queryset.filter(creator=self.request.user)
        return super(ShowtimeViewSet, self).get_queryset()

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)

    @action(detail=False)
    def invited(self, request):
        showtimes = Showtime.objects.filter(
            invites__in=Invitation.objects.filter(
                invited=request.user)
        )

        page = self.paginate_queryset(showtimes)

        if page is not None:
            serializer = ShowtimeSerializer(
                page, many=True, context={"request": request}
            )
            return self.get_paginated_response(serializer.data)

        return Response(
            ShowtimeSerializer(
                showtimes, many=True, context={"request": request}
            ).data
        )

    @action(methods=["post"], detail=True)
    def invite(self, request, pk):
        showtime = self.get_object()
        if showtime.creator != self.request.user:
            raise PermissionDenied()

        serializer = InvitationCreationSerializer(
            showtime, data=request.data, context={"request": request}
        )

        if not serializer.is_valid():
            return Response(serializer.errors)

        serializer.save()
        return redirect("showtime-detail", (showtime.pk,))


class InvitationViewSet(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = InvitationSerializer
    permission_classes = [IsAuthenticated | IsInvitedPermission]

    def get_queryset(self):
        return Invitation.objects.filter(invited=self.request.user)


class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
