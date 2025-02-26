# -*- coding: utf-8 -*-
# @Author: Zana Saedpanah
# @Date:   2025-02-26 20:15:51
# @Last Modified by:   Zana Saedpanah
# @Last Modified time: 2025-02-26 20:26:11
I'll help you develop the MovieShelf application! Based on your description, this looks like a Flask-based media manager project that helps organize and display movie and TV show collections.

Looking at the files you've shared, I can see:
1. A `.gitignore` file set up for Python projects
2. A basic README.md that outlines the core functionality

Let's develop a plan to build this application. We'll need to establish:
- Project structure
- Core functionality
- Database design
- API integration for metadata
- Frontend development

Let's start with setting up the project structure and implementing the core functionality.

First, let's create a basic project structure:

```bash
MovieShelf/
├── app/
│   ├── __init__.py               # Flask application initialization
│   ├── models/                   # Database models
│   │   ├── __init__.py
│   │   ├── movie.py              # Movie model
│   │   └── tvshow.py             # TV Show model
│   ├── routes/                   # Flask routes
│   │   ├── __init__.py
│   │   ├── main.py               # Main routes
│   │   ├── movie.py              # Movie-related routes
│   │   └── tvshow.py             # TV Show-related routes
│   ├── scanner/                  # File scanning functionality
│   │   ├── __init__.py
│   │   ├── file_scanner.py       # File discovery and analysis
│   │   └── metadata_fetcher.py   # API integration for metadata
│   ├── static/                   # Static files (CSS, JS, images)
│   │   ├── css/
│   │   ├── js/
│   │   └── img/
│   └── templates/                # HTML templates
│       ├── base.html             # Base template
│       ├── index.html            # Homepage
│       ├── movies/               # Movie-related templates
│       └── tvshows/              # TV Show-related templates
├── config.py                     # Configuration file
├── requirements.txt              # Project dependencies
└── run.py                        # Application entry point

```

Now, let's implement the core components of the application:

1. First, let's create the requirements.txt file to manage dependencies:

```text
Flask==2.3.3
Flask-SQLAlchemy==3.1.1
Flask-Migrate==4.0.5
requests==2.31.0
python-dotenv==1.0.0
tmdbv3api==1.7.7     # For The Movie Database API
guessit==3.7.1       # For parsing filenames
SQLAlchemy==2.0.23
Werkzeug==2.3.7
Jinja2==3.1.2
click==8.1.7
itsdangerous==2.1.2
packaging==23.2
blinker==1.6.2
alembic==1.12.1
Mako==1.2.4
psycopg2-binary==2.9.9  # PostgreSQL adapter (optional)

```

2. Let's create the application configuration file:

```python
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # Flask configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    
    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Media directories to scan
    MEDIA_DIRECTORIES = os.environ.get('MEDIA_DIRECTORIES', '').split(',')
    
    # The Movie Database API key
    TMDB_API_KEY = os.environ.get('TMDB_API_KEY', '')
    
    # Application settings
    ITEMS_PER_PAGE = 24  # Number of items to display per page
    
    # File extensions to scan
    VIDEO_EXTENSIONS = ['.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm', '.m4v']
    
    # Poster image cache directory
    POSTER_CACHE_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'app', 'static', 'img', 'posters')

```

3. Let's create the application entry point:

```python
from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

```

4. Now, let's create the Flask application initialization:

```python
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Create necessary directories
    import os
    if not os.path.exists(app.config['POSTER_CACHE_DIR']):
        os.makedirs(app.config['POSTER_CACHE_DIR'])
    
    # Register blueprints
    from app.routes import main_bp, movie_bp, tvshow_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(movie_bp, url_prefix='/movies')
    app.register_blueprint(tvshow_bp, url_prefix='/tvshows')
    
    return app

# Import models to ensure they are registered with SQLAlchemy
from app.models import movie, tvshow

```

5. Let's define the database models:

```python
from app import db
from datetime import datetime

class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    original_title = db.Column(db.String(255))
    tmdb_id = db.Column(db.Integer, unique=True)
    imdb_id = db.Column(db.String(20), unique=True)
    overview = db.Column(db.Text)
    release_date = db.Column(db.Date)
    runtime = db.Column(db.Integer)  # In minutes
    poster_path = db.Column(db.String(255))
    backdrop_path = db.Column(db.String(255))
    genres = db.Column(db.String(255))  # Comma-separated list of genres
    
    # File information
    file_path = db.Column(db.String(1024), nullable=False, unique=True)
    file_size = db.Column(db.BigInteger)  # Size in bytes
    resolution = db.Column(db.String(20))  # e.g., "1080p", "4K"
    
    # Cast and crew (stored as JSON strings)
    cast = db.Column(db.Text)  # JSON string of main cast
    director = db.Column(db.String(255))
    
    # Timestamps
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Movie {self.title}>'

```

```python
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
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship with episodes
    episodes = db.relationship('Episode', backref='tvshow', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<TVShow {self.title}>'

class Episode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tvshow_id = db.Column(db.Integer, db.ForeignKey('tv_show.id'), nullable=False)
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
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Ensure each episode is unique within a TV show
    __table_args__ = (
        db.UniqueConstraint('tvshow_id', 'season_number', 'episode_number', name='_tvshow_season_episode_uc'),
    )
    
    def __repr__(self):
        return f'<Episode S{self.season_number:02d}E{self.episode_number:02d}: {self.title}>'

```

6. Let's set up the route blueprints:

```python
from app.routes.main import bp as main_bp
from app.routes.movie import bp as movie_bp
from app.routes.tvshow import bp as tvshow_bp

# All blueprints are imported and made available to the application

```

```python
from flask import Blueprint, render_template, redirect, url_for, request, current_app
from app.models.movie import Movie
from app.models.tvshow import TVShow
from app.scanner.file_scanner import scan_directories
from app import db

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    # Get recent movies and TV shows
    recent_movies = Movie.query.order_by(Movie.date_added.desc()).limit(12).all()
    recent_tvshows = TVShow.query.order_by(TVShow.date_added.desc()).limit(12).all()
    
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

```

```python
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
            cast_list = json.loads(movie.cast)[:10]  # Limit to top 10 cast members
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

```

```python
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
            cast_list = json.loads(tvshow.cast)[:10]  # Limit to top 10 cast members
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

```

7. Now, let's implement the file scanner and metadata fetcher:

```python
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
                            process_episode(file_path, guess, root, tmdb_fetcher)
                            found_episode_paths.append(file_path)
                            # Track TV show directory
                            tvshow_dir = find_tvshow_directory(root)
                            if tvshow_dir:
                                found_tvshow_dirs.append(tvshow_dir)
                    except Exception as e:
                        logger.error(f"Error processing file {file_path}: {str(e)}")
    
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
        movie.genres = ','.join([genre['name'] for genre in metadata['genres']])
    
    # Handle cast and crew
    if 'credits' in metadata:
        # Save cast information
        if 'cast' in metadata['credits']:
            movie.cast = json.dumps(metadata['credits']['cast'])
        
        # Find director
        if 'crew' in metadata['credits']:
            directors = [crew['name'] for crew in metadata['credits']['crew'] if crew['job'] == 'Director']
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
                tvshow.genres = ','.join([genre['name'] for genre in metadata['genres']])
            
            # Handle cast and creators
            if 'credits' in metadata:
                if 'cast' in metadata['credits']:
                    tvshow.cast = json.dumps(metadata['credits']['cast'])
                
                if 'crew' in metadata['credits']:
                    creators = [crew['name'] for crew in metadata['credits']['crew'] if crew['job'] == 'Creator']
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
            episode.title = episode_metadata.get('name', f"S{season_number:02d}E{episode_number:02d}")
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
    movies_to_delete = Movie.query.filter(~Movie.file_path.in_(found_movie_paths)).all()
    for movie in movies_to_delete:
        db.session.delete(movie)
    
    # Remove episodes that were not found
    episodes_to_delete = Episode.query.filter(~Episode.file_path.in_(found_episode_paths)).all()
    for episode in episodes_to_delete:
        db.session.delete(episode)
    
    # Remove TV shows with no episodes and not found in directories
    tvshows_to_check = TVShow.query.filter(~TVShow.directory_path.in_(found_tvshow_dirs)).all()
    for tvshow in tvshows_to_check:
        if tvshow.episodes.count() == 0:
            db.session.delete(tvshow)
```