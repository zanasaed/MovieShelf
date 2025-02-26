# -*- coding: utf-8 -*-
# @Author: Zana Saedpanah
# @Date:   2025-02-26 20:15:51
# @Last Modified by:   Zana Saedpanah
# @Last Modified time: 2025-02-26 20:26:17

from app.models import movie, tvshow
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
