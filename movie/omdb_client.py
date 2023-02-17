import logging
import requests

logger = logging.getLogger(__name__)

OMDB_API_URL = "https://www.omdbapi.com/"


class OmdbMovie:
    # Class to represent movie data coming from OMDb and transform to Python

    def __init__(self, data):
        self.data = data  # data is the raw JSON returned from OMDb API

    def check_for_detail_data_key(self, key):

        if key not in self.data:
            raise AttributeError(
                f"{key} is not in data, please make sure this is a detail response."
            )  # some keys are only in the detail response, exception raised if key is not found

    @property
    def imdb_id(self):
        return self.data["imdbID"]

    @property
    def title(self):
        return self.data["Title"]

    @property
    def year(self):
        return int(self.data["Year"])

    @property
    def runtime_minutes(self):
        self.check_for_detail_data_key("Runtime")

        try:
            runtime, units = self.data["Runtime"].split(" ")
        except ValueError:
            return None

        if units != "min":
            raise ValueError(
                f"'Minutes' must be for runtime, instead '{units}")

        return int(runtime)

    @property
    def genres(self):
        self.check_for_detail_data_key("Genre")

        return self.data["Genre"].split(", ")

    @property
    def plot(self):
        self.check_for_detail_data_key("Plot")
        return self.data["Plot"]


class OmdbClient:
    def __init__(self, api_key):
        self.api_key = api_key

    # makes GET request to the API, adding the apikey to parameters
    def make_request(self, params):
        params["apikey"] = self.api_key
        response = requests.get(OMDB_API_URL, params=params)
        response.raise_for_status()
        return response

    # get a movie by its IMDb id
    def get_by_imdb_id(self, imdb_id):
        logger.info(f"Getting details for IMDb id {imdb_id}")
        response = self.make_request({"i": imdb_id})
        return OmdbMovie(response.json())

    # searches for movies by title. This is a generator so all results from all pages will be iterated across
    def search(self, search):
        page = 1
        seen_results = 0
        total_results = None

        logger.info(f"Serching for {search}")

        while True:
            logger.info("Fetching page %d", page)
            resp = self.make_request(
                {"s": search, "type": "movie", "page": str(page)})
            resp_body = resp.json()
            if total_results is None:
                total_results = int(resp_body["totalResults"])

            for movie in resp_body["Search"]:
                seen_results += 1
                yield OmdbMovie(movie)

            if seen_results >= total_results:
                break

            page += 1
