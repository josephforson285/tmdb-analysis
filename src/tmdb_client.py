"""Client for the TMDB API (v3).

Docs: https://developer.themoviedb.org/reference/movie-details
We request `append_to_response=credits` so each movie comes with its
cast and crew in the same call — the project needs cast, cast_size,
director and crew_size later, and this avoids a second request per movie.
"""

import json
from pathlib import Path

import requests

BASE_URL = "https://api.themoviedb.org/3/movie/{movie_id}"


def fetch_movie(movie_id, api_key, session=None):
    """Fetch one movie as a dict, or None if TMDB doesn't know the id.

    A 404 (e.g. the intentionally-invalid id 0) is an expected outcome,
    so we return None instead of raising. Any other error (bad key,
    rate limit, network issue) is a real problem and raises.
    """
    http = session or requests
    response = http.get(
        BASE_URL.format(movie_id=movie_id),
        params={"api_key": api_key, "append_to_response": "credits"},
        timeout=10,
    )
    if response.status_code == 404:
        return None
    response.raise_for_status()
    return response.json()


def fetch_movies(movie_ids, api_key):
    """Fetch many movies, skipping ids the API doesn't know.

    Uses one Session so all requests share a connection (faster than
    opening a new one per movie). Returns a list of raw JSON dicts.
    """
    movies = []
    with requests.Session() as session:
        for movie_id in movie_ids:
            movie = fetch_movie(movie_id, api_key, session=session)
            if movie is None:
                print(f"id {movie_id}: not found, skipped")
            else:
                movies.append(movie)
                print(f"id {movie_id}: {movie['title']}")
    return movies


def save_raw(movies, path):
    """Save the raw API responses untouched — the 'never edit raw data' rule."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(movies, indent=2))
    print(f"Saved {len(movies)} movies to {path}")


def load_raw(path):
    """Load previously saved raw responses (so we never re-hit the API)."""
    return json.loads(Path(path).read_text())
