# -*- coding: utf-8 -*-
# @Author: Your name
# @Date:   2025-02-26 20:15:12
# @Last Modified by:   Zana Saedpanah
# @Last Modified time: 2025-02-26 20:20:50
import os


def create_structure(base_path):
    structure = [
        "app/__init__.py",
        "app/models/__init__.py",
        "app/models/movie.py",
        "app/models/tvshow.py",
        "app/routes/__init__.py",
        "app/routes/main.py",
        "app/routes/movie.py",
        "app/routes/tvshow.py",
        "app/scanner/__init__.py",
        "app/scanner/file_scanner.py",
        "app/scanner/metadata_fetcher.py",
        "app/static/css/",
        "app/static/js/",
        "app/static/img/",
        "app/templates/base.html",
        "app/templates/index.html",
        "app/templates/movies/",
        "app/templates/tvshows/",
        "config.py",
        "requirements.txt",
        "run.py"
    ]

    for path in structure:
        full_path = os.path.join(base_path, path)
        if path.endswith("/"):
            os.makedirs(full_path, exist_ok=True)
        else:
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, "w") as f:
                f.write("" if path.endswith(".py")
                        or path.endswith(".html") else "")


if __name__ == "__main__":
    base_dir = "D:/python/Movieshelf/MovieShelf"
    os.makedirs(base_dir, exist_ok=True)
    create_structure(base_dir)
    print(f"Project structure created inside {base_dir}/")
