# -*- coding: utf-8 -*-
# @Author: Zana Saedpanah
# @Date:   2025-02-26 20:15:51
# @Last Modified by:   Zana Saedpanah
# @Last Modified time: 2025-02-26 20:26:04
import requests
import logging
import os
from datetime import datetime
from flask import current_app

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TMDBFetcher:
    """Class to handle fetching metadata from The Movie Database (TMDb)"""

    BASE_URL = "https://api.themoviedb.org/3"
    POSTER_BASE_URL = "https://image.tmdb.org/t/p/w500"
    BACKDROP_BASE_URL = "https://image.tmdb.org/t/p/original"

    def __init__(self, api_key):
        self.api_key = api_key

    def _make_request(self, endpoint, params=None):
        """Make a request to the TMDb API"""
        if params is None:
            params = {}

        params['api_key'] = self.api_key

        try:
            response = requests.get(
                f"{self.BASE_URL}{endpoint}", params=params)
            response.raise_for_status()  # Raise exception for 4XX/5XX responses
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error making request to TMDb: {str(e)}")
            return None

    def fetch_movie_metadata(self, query):
        """
        Fetch metadata for a movie

        Args:
            query: Movie title (with optional year)

        Returns:
            Dictionary of movie metadata or empty dict if not found
        """
        if not self.api_key:
            logger.warning("No TMDb API key provided")
            return {}

        # First search for the movie
        search_params = {
            'query': query,
            'include_adult': 'false'
        }

        search_results = self._make_request("/search/movie", search_params)

        if not search_results or not search_results.get('results'):
            logger.info(f"No results found for movie query: {query}")
            return {}

        # Get the first result
        movie_id = search_results['results'][0]['id']

        # Fetch detailed movie info
        movie_details = self._make_request(
            f"/movie/{movie_id}",
            {'append_to_response': 'credits,recommendations'}
        )

        if not movie_details:
            return {}

        # Process image paths
        if movie_details.get('poster_path'):
            movie_details['poster_path'] = self.POSTER_BASE_URL + \
                movie_details['poster_path']

            # Download poster for local caching
            self._cache_image(
                movie_details['poster_path'], f"movie_{movie_id}_poster.jpg")

        if movie_details.get('backdrop_path'):
            movie_details['backdrop_path'] = self.BACKDROP_BASE_URL + \
                movie_details['backdrop_path']

        # Parse dates
        if movie_details.get('release_date'):
            try:
                movie_details['release_date'] = datetime.strptime(
                    movie_details['release_date'], '%Y-%m-%d'
                ).date()
            except ValueError:
                movie_details['release_date'] = None

        return movie_details

    def fetch_tvshow_metadata(self, title):
        """
        Fetch metadata for a TV show

        Args:
            title: TV show title

        Returns:
            Dictionary of TV show metadata or empty dict if not found
        """
        if not self.api_key:
            logger.warning("No TMDb API key provided")
            return {}

        # First search for the TV show
        search_params = {
            'query': title,
            'include_adult': 'false'
        }

        search_results = self._make_request("/search/tv", search_params)

        if not search_results or not search_results.get('results'):
            logger.info(f"No results found for TV show query: {title}")
            return {}

        # Get the first result
        tvshow_id = search_results['results'][0]['id']

        # Fetch detailed TV show info
        tvshow_details = self._make_request(
            f"/tv/{tvshow_id}",
            {'append_to_response': 'credits,recommendations'}
        )

        if not tvshow_details:
            return {}

        # Process image paths
        if tvshow_details.get('poster_path'):
            tvshow_details['poster_path'] = self.POSTER_BASE_URL + \
                tvshow_details['poster_path']

            # Download poster for local caching
            self._cache_image(
                tvshow_details['poster_path'], f"tvshow_{tvshow_id}_poster.jpg")

        if tvshow_details.get('backdrop_path'):
            tvshow_details['backdrop_path'] = self.BACKDROP_BASE_URL + \
                tvshow_details['backdrop_path']

        # Parse dates
        for date_field in ['first_air_date', 'last_air_date']:
            if tvshow_details.get(date_field):
                try:
                    tvshow_details[date_field] = datetime.strptime(
                        tvshow_details[date_field], '%Y-%m-%d'
                    ).date()
                except ValueError:
                    tvshow_details[date_field] = None

        return tvshow_details

    def fetch_episode_metadata(self, tvshow_id, season_number, episode_number):
        """
        Fetch metadata for a TV show episode

        Args:
            tvshow_id: TMDb ID of the TV show
            season_number: Season number
            episode_number: Episode number

        Returns:
            Dictionary of episode metadata or empty dict if not found
        """
        if not self.api_key:
            logger.warning("No TMDb API key provided")
            return {}

        # Fetch episode info
        episode_details = self._make_request(
            f"/tv/{tvshow_id}/season/{season_number}/episode/{episode_number}"
        )

        if not episode_details:
            return {}

        # Process still image path
        if episode_details.get('still_path'):
            episode_details['still_path'] = self.POSTER_BASE_URL + \
                episode_details['still_path']

        # Parse air date
        if episode_details.get('air_date'):
            try:
                episode_details['air_date'] = datetime.strptime(
                    episode_details['air_date'], '%Y-%m-%d'
                ).date()
            except ValueError:
                episode_details['air_date'] = None

        return episode_details

    def _cache_image(self, image_url, filename):
        """Download and cache an image locally"""
        try:
            if not current_app.config.get('POSTER_CACHE_DIR'):
                return

            cache_dir = current_app.config['POSTER_CACHE_DIR']
            filepath = os.path.join(cache_dir, filename)

            # Skip if file already exists
            if os.path.exists(filepath):
                return

            # Download image
            response = requests.get(image_url)
            response.raise_for_status()

            # Save to file
            with open(filepath, 'wb') as f:
                f.write(response.content)

            logger.debug(f"Cached image: {filename}")

        except Exception as e:
            logger.error(f"Error caching image {filename}: {str(e)}")
