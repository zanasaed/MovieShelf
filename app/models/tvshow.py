# -*- coding: utf-8 -*-
# @Author: Zana Saedpanah
# @Date:   2025-02-26 20:15:51
# @Last Modified by:   Zana Saedpanah
# @Last Modified time: 2025-02-26 20:26:15
from app import db
from datetime import datetime


class TVShow(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    original_title = db.Column(db.String(255))
    tmdb_id = db.Column(db.Integer, unique=True)
    overview = db.Column(db.Text)
    first_air_date = db.Column(db.Date)
    last_air_date = db.Column(db.Date)
    status = db.Column(db.String(50))  # e.g., "Ended", "Returning Series"
    number_of_seasons = db.Column(db.Integer)
    number_of_episodes = db.Column(db.Integer)
    poster_path = db.Column(db.String(255))
    backdrop_path = db.Column(db.String(255))
    genres = db.Column(db.String(255))  # Comma-separated list of genres

    # Directory information
    directory_path = db.Column(db.String(1024), nullable=False, unique=True)

    # Cast and crew (stored as JSON strings)
    cast = db.Column(db.Text)  # JSON string of main cast
    creators = db.Column(db.String(255))

    # Timestamps
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    last_updated = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship with episodes
    episodes = db.relationship(
        'Episode', backref='tvshow', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<TVShow {self.title}>'


class Episode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tvshow_id = db.Column(db.Integer, db.ForeignKey(
        'tv_show.id'), nullable=False)
    season_number = db.Column(db.Integer, nullable=False)
    episode_number = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(255))
    overview = db.Column(db.Text)
    air_date = db.Column(db.Date)
    still_path = db.Column(db.String(255))

    # File information
    file_path = db.Column(db.String(1024), nullable=False, unique=True)
    file_size = db.Column(db.BigInteger)  # Size in bytes
    resolution = db.Column(db.String(20))  # e.g., "1080p", "4K"

    # Timestamps
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    last_updated = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Ensure each episode is unique within a TV show
    __table_args__ = (
        db.UniqueConstraint('tvshow_id', 'season_number',
                            'episode_number', name='_tvshow_season_episode_uc'),
    )

    def __repr__(self):
        return f'<Episode S{self.season_number:02d}E{self.episode_number:02d}: {self.title}>'
