from datetime import timedelta

from django.db import models
from django.contrib.auth import get_user_model

UserModel = get_user_model()


class Genre(models.Model):
    class Meta:
        ordering = ["name"]

    name = models.TextField(unique=True)

    def __str__(self):
        return self.name


class Movie(models.Model):
    class Meta:
        ordering = ["title", "year"]

    title = models.TextField()
    year = models.PositiveIntegerField()
    imdb_id = models.SlugField(unique=True)  # unique field
    duration = models.PositiveIntegerField(null=True)  # minutes
    genres = models.ManyToManyField(Genre, related_name="movies")
    plot = models.TextField(null=True, blank=True)
    is_full_record = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.title} ({self.year})"


class Showtime(models.Model):
    class Meta:
        ordering = ["creator", "start_time"]

    movie = models.ForeignKey(Movie, on_delete=models.PROTECT)
    start_time = models.DateTimeField()
    creator = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    start_notification_sent = models.BooleanField(default=False)

    @property
    def end_time(self):
        if not self.movie.duration:
            return None

        return self.start_time + timedelta(minutes=self.movie.duration)

    def __str__(self):
        return f"`{self.movie}` showtime, created {self.creator.email}"


class Invitation(models.Model):
    showtime = models.ForeignKey(
        Showtime, on_delete=models.CASCADE, related_name="invites"
    )
    invited = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    attendance_confirmed = models.BooleanField(default=False)
    is_attending = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.showtime} / {self.invited.email}"


class SearchTerm(models.Model):
    term = models.TextField(unique=True)
    last_search = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.term
