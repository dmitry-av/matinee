from rest_framework import serializers

from matinee_auth.models import User
from movie.models import Showtime, Invitation, Movie, Genre


class GenreField(serializers.SlugRelatedField):
    def to_internal_value(self, data):
        try:
            return self.get_queryset().get_or_create(name=data)[0]
        except (TypeError, ValueError):
            self.fail(f"Tag value {data} is invalid")


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = "__all__"


class MovieSerializer(serializers.ModelSerializer):
    genres = GenreField(slug_field="name", many=True, read_only=True)

    class Meta:
        model = Movie
        fields = "__all__"
        read_only_fields = [
            "title",
            "year",
            "runtime_minutes",
            "imdb_id",
            "genres",
            "plot",
            "is_full_record",
        ]


class MovieTitleAndUrlSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedRelatedField("movie-detail", read_only=True)

    class Meta:
        model = Movie
        fields = ["title", "url"]


class InvitationSerializer(serializers.ModelSerializer):
    invited = serializers.HyperlinkedRelatedField(
        "user-detail", read_only=True, lookup_field="email"
    )

    class Meta:
        model = Invitation
        fields = "__all__"
        read_only_fields = ["attendance_confirmed", "showtime", "invited"]


class InvitationCreationSerializer(serializers.ModelSerializer):
    invited = serializers.HyperlinkedRelatedField(
        "user-detail", queryset=User.objects.all(), lookup_field="email"
    )

    class Meta:
        model = Invitation
        fields = ["invited"]

    def __init__(self, showtime, *args, **kwargs):
        self.showtime = showtime
        super(InvitationCreationSerializer,
              self).__init__(*args, **kwargs)

    def save(self, **kwargs):
        kwargs["showtime"] = self.showtime
        return super(InvitationCreationSerializer, self).save(**kwargs)

    def validate_invited(self, invited):
        existing_invitation = Invitation.objects.filter(
            invited=invited, showtime=self.showtime
        ).first()
        if existing_invitation:
            raise serializers.ValidationError(
                f"{invited.email} has already been invited to this Matinee showtime event"
            )
        return invited


class ShowtimeSerializer(serializers.ModelSerializer):
    movie = MovieTitleAndUrlSerializer(read_only=True)
    creator = serializers.HyperlinkedRelatedField(
        "user-detail", read_only=True, lookup_field="email"
    )
    invites = InvitationSerializer(read_only=True, many=True)

    class Meta:
        model = Showtime
        fields = "__all__"
        read_only_fields = ["movie", "creator",
                            "start_notification_sent", "invites"]


class ShowtimeCreateSerializer(ShowtimeSerializer):
    movie = serializers.HyperlinkedRelatedField(
        view_name="movie-detail", queryset=Movie.objects.all()
    )

    class Meta(ShowtimeSerializer.Meta):
        read_only_fields = ["start_notification_sent", "invites"]


class MovieSearchSerializer(serializers.Serializer):
    term = serializers.CharField()
