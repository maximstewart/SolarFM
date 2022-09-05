import json
import sys

from .lib.tmdbscraper.tmdb import TMDBMovieScraper
from .lib.tmdbscraper.fanarttv import get_details as get_fanarttv_artwork
from .lib.tmdbscraper.imdbratings import get_details as get_imdb_details
from .lib.tmdbscraper.traktratings import get_trakt_ratinginfo
from .scraper_datahelper import combine_scraped_details_info_and_ratings, \
    combine_scraped_details_available_artwork, find_uniqueids_in_text, get_params
from .scraper_config import configure_scraped_details, PathSpecificSettings, \
    configure_tmdb_artwork, is_fanarttv_configured






def get_tmdb_scraper():
    language       = 'en-US'
    certcountry    = 'us'
    ADDON_SETTINGS = None
    return TMDBMovieScraper(ADDON_SETTINGS, language, certcountry)
