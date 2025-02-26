# -*- coding: utf-8 -*-
# @Author: Zana Saedpanah
# @Date:   2025-02-26 20:15:51
# @Last Modified by:   Zana Saedpanah
# @Last Modified time: 2025-02-26 20:24:34
import os
import json
from datetime import datetime
from guessit import guessit
from app import db
from app.models.movie import Movie
from app.models.tvshow import TVShow, Episode
from app.scanner.metadata_fetcher import TMDBFetcher
from flask import current_app
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def scan_directories(directories):
    """
    Scan directories for media files and update the database

    Args:
        directories: List of directory paths to scan
    """
    logger.info(f"Starting scan of {len(directories)} directories")

    # Initialize TMDB fetcher
    tmdb_fetcher = TMDBFetcher(current_app.config['TMDB_API_KEY'])

    # Get list of valid video extensions
    video_extensions = current_app.config['VIDEO_EXTENSIONS']

    # Track found files to identify removed ones
    found_movie_paths = []
    found_episode_paths = []
    found_tvshow_dirs = []

    # Process each directory
    for directory in directories:
        if not os.path.exists(directory):
            logger.warning(f"Directory not found: {directory}")
            continue

        logger.info(f"Scanning directory: {directory}")

        # Walk through directory
        for root, dirs, files in os.walk(directory):
            # Process files
            for filename in files:
                if any(filename.lower().endswith(ext) for ext in video_extensions):
                    file_path = os.path.join(root, filename)

                    # Parse filename
                    try:
                        guess = guessit(filename)

                        # Determine if it's a movie or TV show episode
                        if guess.get('type') == 'movie':
                            process_movie(file_path, guess, tmdb_fetcher)
                            found_movie_paths.append(file_path)
                        elif guess.get('type') == 'episode':
                            process_episode(file_path, guess,
                                            root, tmdb_fetcher)
                            found_episode_paths.append(file_path)
                            # Track TV show directory
                            tvshow_dir = find_tvshow_directory(root)
                            if tvshow_dir:
                                found_tvshow_dirs.append(tvshow_dir)
                    except Exception as e:
                        logger.error(
                            f"Error processing file {file_path}: {str(e)}")

    # Remove entries for deleted files
    cleanup_database(found_movie_paths, found_episode_paths, found_tvshow_dirs)

    logger.info("Scan completed")


def find_tvshow_directory(path):
    """Find the main TV show directory from an episode path"""
    # This is a simplified approach - in reality, you might need more complex logic
    # to identify the TV show root directory
    parts = path.split(os.sep)
    if len(parts) >= 2:
        # Assume the parent directory is the TV show directory
        return os.path.dirname(path)
    return None


def process_movie(file_path, guess_data, tmdb_fetcher):
    """Process a movie file and update the database"""
    # Check if movie already exists in database
    existing_movie = Movie.query.filter_by(file_path=file_path).first()

    if existing_movie:
        # If file hasn't changed, skip processing
        if os.path.getmtime(file_path) <= existing_movie.last_updated.timestamp():
            return existing_movie

    # Get basic info from filename
    title = guess_data.get('title', os.path.basename(file_path))
    year = guess_data.get('year')

    # Get file size and other properties
    file_size = os.path.getsize(file_path)
    resolution = guess_data.get('screen_size', 'Unknown')

    # Fetch metadata from TMDB
    metadata = {}
    if title:
        query = title
        if year:
            query += f" {year}"
        metadata = tmdb_fetcher.fetch_movie_metadata(query)

    # Create or update movie record
    if existing_movie:
        # Update existing record
        movie = existing_movie
    else:
        # Create new record
        movie = Movie(file_path=file_path)

    # Update basic properties
    movie.title = metadata.get('title', title)
    movie.original_title = metadata.get('original_title')
    movie.tmdb_id = metadata.get('id')
    movie.imdb_id = metadata.get('imdb_id')
    movie.overview = metadata.get('overview')
    movie.release_date = metadata.get('release_date')
    movie.runtime = metadata.get('runtime')
    movie.poster_path = metadata.get('poster_path')
    movie.backdrop_path = metadata.get('backdrop_path')
    movie.file_size = file_size
    movie.resolution = str(resolution)

    # Handle genres
    if 'genres' in metadata:
        movie.genres = ','.join([genre['name']
                                for genre in metadata['genres']])

    # Handle cast and crew
    if 'credits' in metadata:
        # Save cast information
        if 'cast' in metadata['credits']:
            movie.cast = json.dumps(metadata['credits']['cast'])

        # Find director
        if 'crew' in metadata['credits']:
            directors = [crew['name'] for crew in metadata['credits']
                         ['crew'] if crew['job'] == 'Director']
            if directors:
                movie.director = ', '.join(directors)

    # Save to database
    if not existing_movie:
        db.session.add(movie)
    db.session.commit()

    return movie


def process_episode(file_path, guess_data, directory, tmdb_fetcher):
    """Process a TV show episode and update the database"""
    # Get basic info from filename
    title = guess_data.get('title')
    season_number = guess_data.get('season', 1)
    episode_number = guess_data.get('episode', 1)

    # Find or create TV show
    tvshow_dir = find_tvshow_directory(directory)
    if not tvshow_dir:
        return None

    tvshow = TVShow.query.filter_by(directory_path=tvshow_dir).first()

    # If TV show doesn't exist, create it
    if not tvshow and title:
        # Fetch metadata from TMDB
        metadata = tmdb_fetcher.fetch_tvshow_metadata(title)

        if metadata:
            tvshow = TVShow(
                title=metadata.get('name', title),
                original_title=metadata.get('original_name'),
                tmdb_id=metadata.get('id'),
                overview=metadata.get('overview'),
                first_air_date=metadata.get('first_air_date'),
                last_air_date=metadata.get('last_air_date'),
                status=metadata.get('status'),
                number_of_seasons=metadata.get('number_of_seasons'),
                number_of_episodes=metadata.get('number_of_episodes'),
                poster_path=metadata.get('poster_path'),
                backdrop_path=metadata.get('backdrop_path'),
                directory_path=tvshow_dir
            )

            # Handle genres
            if 'genres' in metadata:
                tvshow.genres = ','.join([genre['name']
                                         for genre in metadata['genres']])

            # Handle cast and creators
            if 'credits' in metadata:
                if 'cast' in metadata['credits']:
                    tvshow.cast = json.dumps(metadata['credits']['cast'])

                if 'crew' in metadata['credits']:
                    creators = [crew['name'] for crew in metadata['credits']
                                ['crew'] if crew['job'] == 'Creator']
                    if creators:
                        tvshow.creators = ', '.join(creators)

            db.session.add(tvshow)
            db.session.commit()
        else:
            # If no metadata found, create a basic TV show entry
            tvshow = TVShow(
                title=title,
                directory_path=tvshow_dir
            )
            db.session.add(tvshow)
            db.session.commit()

    # If we still don't have a TV show record, we can't add the episode
    if not tvshow:
        return None

    # Check if episode already exists
    existing_episode = Episode.query.filter_by(file_path=file_path).first()

    if existing_episode:
        # If file hasn't changed, skip processing
        if os.path.getmtime(file_path) <= existing_episode.last_updated.timestamp():
            return existing_episode
        episode = existing_episode
    else:
        # Create new episode
        episode = Episode(
            tvshow_id=tvshow.id,
            season_number=season_number,
            episode_number=episode_number,
            file_path=file_path
        )

    # Get file size and other properties
    episode.file_size = os.path.getsize(file_path)
    episode.resolution = str(guess_data.get('screen_size', 'Unknown'))

    # Try to fetch episode-specific metadata
    if tvshow.tmdb_id:
        episode_metadata = tmdb_fetcher.fetch_episode_metadata(
            tvshow.tmdb_id, season_number, episode_number
        )

        if episode_metadata:
            episode.title = episode_metadata.get(
                'name', f"S{season_number:02d}E{episode_number:02d}")
            episode.overview = episode_metadata.get('overview')
            episode.air_date = episode_metadata.get('air_date')
            episode.still_path = episode_metadata.get('still_path')

    # If we still don't have an episode title, use a default format
    if not episode.title:
        episode.title = f"S{season_number:02d}E{episode_number:02d}"

    # Save to database
    if not existing_episode:
        db.session.add(episode)
    db.session.commit()

    return episode


def cleanup_database(found_movie_paths, found_episode_paths, found_tvshow_dirs):
    """Remove database entries for files that no longer exist"""
    # Remove movies that were not found
    movies_to_delete = Movie.query.filter(
        ~Movie.file_path.in_(found_movie_paths)).all()
    for movie in movies_to_delete:
        db.session.delete(movie)

    # Remove episodes that were not found
    episodes_to_delete = Episode.query.filter(
        ~Episode.file_path.in_(found_episode_paths)).all()
    for episode in episodes_to_delete:
        db.session.delete(episode)

    # Remove TV shows with no episodes and not found in directories
    tvshows_to_check = TVShow.query.filter(
        ~TVShow.directory_path.in_(found_tvshow_dirs)).all()
    for tvshow in tvshows_to_check:
        if tvshow.episodes.count() == 0:
            db.session.delete(tvshow)


Last edited 12 minutes ago
