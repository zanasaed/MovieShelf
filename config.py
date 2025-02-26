# -*- coding: utf-8 -*-
# @Author: Zana Saedpanah
# @Date:   2025-02-26 20:15:51
# @Last Modified by:   Zana Saedpanah
# @Last Modified time: 2025-02-26 20:20:34


import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    # Flask configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'

    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + \
        os.path.join(os.path.abspath(os.path.dirname(__file__)), 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Media directories to scan
    MEDIA_DIRECTORIES = os.environ.get('MEDIA_DIRECTORIES', '').split(',')

    # The Movie Database API key
    TMDB_API_KEY = os.environ.get('TMDB_API_KEY', '')

    # Application settings
    ITEMS_PER_PAGE = 24  # Number of items to display per page

    # File extensions to scan
    VIDEO_EXTENSIONS = ['.mp4', '.mkv', '.avi',
                        '.mov', '.wmv', '.flv', '.webm', '.m4v']

    # Poster image cache directory
    POSTER_CACHE_DIR = os.path.join(os.path.abspath(
        os.path.dirname(__file__)), 'app', 'static', 'img', 'posters')
