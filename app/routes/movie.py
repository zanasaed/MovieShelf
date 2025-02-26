# -*- coding: utf-8 -*-
# @Author: Zana Saedpanah
# @Date:   2025-02-26 20:15:51
# @Last Modified by:   Zana Saedpanah
# @Last Modified time: 2025-02-26 20:23:34
from flask import Blueprint, render_template, redirect, url_for, request, current_app, abort
from app.models.movie import Movie
from app import db
import os
import json

bp = Blueprint('movie', __name__)


@bp.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['ITEMS_PER_PAGE']

    # Get query parameters for filtering
    genre = request.args.get('genre', '')
    sort_by = request.args.get('sort_by', 'title')

    # Base query
    query = Movie.query

    # Apply filters
    if genre:
        query = query.filter(Movie.genres.ilike(f'%{genre}%'))

    # Apply sorting
    if sort_by == 'title':
        query = query.order_by(Movie.title)
    elif sort_by == 'date_added':
        query = query.order_by(Movie.date_added.desc())
    elif sort_by == 'release_date':
        query = query.order_by(Movie.release_date.desc())

    # Paginate results
    movies = query.paginate(page=page, per_page=per_page, error_out=False)

    # Get distinct genres for filter dropdown
    all_genres = set()
    for movie in Movie.query.all():
        if movie.genres:
            genres = movie.genres.split(',')
            all_genres.update([g.strip() for g in genres])

    return render_template('movies/index.html',
                           movies=movies,
                           genres=sorted(all_genres),
                           current_genre=genre,
                           current_sort=sort_by)


@bp.route('/<int:id>')
def movie_detail(id):
    movie = Movie.query.get_or_404(id)

    # Parse cast JSON if available
    cast_list = []
    if movie.cast:
        try:
            # Limit to top 10 cast members
            cast_list = json.loads(movie.cast)[:10]
        except json.JSONDecodeError:
            pass

    return render_template('movies/detail.html',
                           movie=movie,
                           cast=cast_list)


@bp.route('/<int:id>/play')
def play_movie(id):
    movie = Movie.query.get_or_404(id)

    # Check if file exists
    if not os.path.exists(movie.file_path):
        abort(404)

    # In a real application, you would stream the video file
    # For this example, we'll redirect to a play page
    return render_template('movies/play.html', movie=movie)
