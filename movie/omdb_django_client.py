from django.conf import settings

from .omdb_client import OmdbClient


def get_client():
    # creates an instance of an OmdbClient using the OMDB_KEY
    return OmdbClient(settings.OMDB_KEY)
