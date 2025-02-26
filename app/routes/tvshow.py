# -*- coding: utf-8 -*-
# @Author: Zana Saedpanah
# @Date:   2025-02-26 20:15:51
# @Last Modified by:   Zana Saedpanah
# @Last Modified time: 2025-02-26 20:24:16
from flask import Blueprint, render_template, redirect, url_for, request, current_app, abort
from app.models.tvshow import TVShow, Episode
from app import db
import os
import json

bp = Blueprint('tvshow', __name__)


@bp.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['ITEMS_PER_PAGE']

    # Get query parameters for filtering
    genre = request.args.get('genre', '')
    sort_by = request.args.get('sort_by', 'title')

    # Base query
    query = TVShow.query

    # Apply filters
    if genre:
        query = query.filter(TVShow.genres.ilike(f'%{genre}%'))

    # Apply sorting
    if sort_by == 'title':
        query = query.order_by(TVShow.title)
    elif sort_by == 'date_added':
        query = query.order_by(TVShow.date_added.desc())
    elif sort_by == 'first_air_date':
        query = query.order_by(TVShow.first_air_date.desc())

    # Paginate results
    tvshows = query.paginate(page=page, per_page=per_page, error_out=False)

    # Get distinct genres for filter dropdown
    all_genres = set()
    for tvshow in TVShow.query.all():
        if tvshow.genres:
            genres = tvshow.genres.split(',')
            all_genres.update([g.strip() for g in genres])

    return render_template('tvshows/index.html',
                           tvshows=tvshows,
                           genres=sorted(all_genres),
                           current_genre=genre,
                           current_sort=sort_by)


@bp.route('/<int:id>')
def tvshow_detail(id):
    tvshow = TVShow.query.get_or_404(id)

    # Get seasons and episodes
    seasons = {}
    for episode in tvshow.episodes.order_by(Episode.season_number, Episode.episode_number).all():
        if episode.season_number not in seasons:
            seasons[episode.season_number] = []
        seasons[episode.season_number].append(episode)

    # Parse cast JSON if available
    cast_list = []
    if tvshow.cast:
        try:
            # Limit to top 10 cast members
            cast_list = json.loads(tvshow.cast)[:10]
        except json.JSONDecodeError:
            pass

    return render_template('tvshows/detail.html',
                           tvshow=tvshow,
                           seasons=seasons,
                           cast=cast_list)


@bp.route('/episode/<int:id>/play')
def play_episode(id):
    episode = Episode.query.get_or_404(id)

    # Check if file exists
    if not os.path.exists(episode.file_path):
        abort(404)

    # In a real application, you would stream the video file
    # For this example, we'll redirect to a play page
    return render_template('tvshows/play.html', episode=episode)


Last edited 12 minutes ago
