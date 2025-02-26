# -*- coding: utf-8 -*-
# @Author: Zana Saedpanah
# @Date:   2025-02-26 20:15:51
# @Last Modified by:   Zana Saedpanah
# @Last Modified time: 2025-02-26 20:23:22
from app import db
from app.scanner.file_scanner import scan_directories
from app.models.tvshow import TVShow
from app.models.movie import Movie
from flask import Blueprint, render_template, redirect, url_for, request, current_app
app/routes/main.py


bp = Blueprint('main', __name__)


@bp.route('/')
def index():
    # Get recent movies and TV shows
    recent_movies = Movie.query.order_by(
        Movie.date_added.desc()).limit(12).all()
    recent_tvshows = TVShow.query.order_by(
        TVShow.date_added.desc()).limit(12).all()

    # Get counts
    movie_count = Movie.query.count()
    tvshow_count = TVShow.query.count()

    return render_template('index.html',
                           recent_movies=recent_movies,
                           recent_tvshows=recent_tvshows,
                           movie_count=movie_count,
                           tvshow_count=tvshow_count)


@bp.route('/search')
def search():
    query = request.args.get('q', '')
    if not query:
        return redirect(url_for('main.index'))

    # Search for movies
    movies = Movie.query.filter(Movie.title.ilike(f'%{query}%')).all()

    # Search for TV shows
    tvshows = TVShow.query.filter(TVShow.title.ilike(f'%{query}%')).all()

    return render_template('search_results.html',
                           query=query,
                           movies=movies,
                           tvshows=tvshows)


@bp.route('/scan', methods=['POST'])
def scan():
    directories = current_app.config['MEDIA_DIRECTORIES']
    if not directories or directories == ['']:
        # If no directories configured, redirect with error
        return redirect(url_for('main.index'))

    # Trigger the scan
    scan_directories(directories)

    return redirect(url_for('main.index'))
