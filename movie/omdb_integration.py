import logging
import re
from datetime import timedelta

from django.utils.timezone import now

from movie.models import Genre, SearchTerm, Movie
from .omdb_django_client import get_client

logger = logging.getLogger(__name__)


def get_or_create_genres(genre_names):
    for genre_name in genre_names:
        genre, created = Genre.objects.get_or_create(name=genre_name)
        yield genre


# fetches full details of film from OMDb, save to the DB, if the movie already has a full record does nothing
def fill_movie_details(movie):
    if movie.is_full_record:
        logger.warning(
            f"{movie.title} is full record."
        )
        return
    omdb_client = get_client()
    movie_details = omdb_client.get_by_imdb_id(movie.imdb_id)
    movie.title = movie_details.title
    movie.year = movie_details.year
    movie.plot = movie_details.plot
    movie.runtime_minutes = movie_details.runtime_minutes
    movie.genres.clear()
    for genre in get_or_create_genres(movie_details.genres):
        movie.genres.add(genre)
    movie.is_full_record = True
    movie.save()


# performes a search for search_term against the API if it has not been searched in the past 1 day. Save each result to the database as a partial record.
def search_and_save(search):

    # lowercase the search, replace multiple spaces
    normalized = re.sub(r"\s+", " ", search.lower())

    search_term, created = SearchTerm.objects.get_or_create(
        term=normalized)

    if not created and (search_term.last_search > now() - timedelta(days=1)):
        logger.warning(
            f"Search for '{normalized}' was performed in the past 24 hours so not searching again."
        )
        return

    omdb_client = get_client()

    for omdb_movie in omdb_client.search(search):
        logger.info(
            f"Saving movie: '{omdb_movie.title}' / '{omdb_movie.imdb_id}'")
        movie, created = Movie.objects.get_or_create(
            imdb_id=omdb_movie.imdb_id,
            defaults={
                "title": omdb_movie.title,
                "year": omdb_movie.year,
            },
        )

        if created:
            logger.info("Movie created: '%s'", movie.title)

    search_term.save()
