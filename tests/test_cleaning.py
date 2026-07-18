"""Unit tests for src/cleaning.py — run with:  python -m pytest

No network, no real API data: every test feeds tiny hand-made inputs
so failures point straight at the function that broke.
"""

import numpy as np
import pandas as pd
import pytest

from src.cleaning import (
    clean_movies,
    extract_collection_name,
    extract_director,
    extract_names,
)


# ---------- extract_names ----------

def test_extract_names_joins_with_pipe():
    genres = [{"id": 28, "name": "Action"}, {"id": 12, "name": "Adventure"}]
    assert extract_names(genres) == "Action|Adventure"

def test_extract_names_custom_key():
    langs = [{"iso_639_1": "en", "english_name": "English"}]
    assert extract_names(langs, key="english_name") == "English"

def test_extract_names_empty_list_is_nan():
    assert pd.isna(extract_names([]))

def test_extract_names_none_is_nan():
    assert pd.isna(extract_names(None))


# ---------- extract_collection_name ----------

def test_collection_name_from_dict():
    coll = {"id": 86311, "name": "The Avengers Collection"}
    assert extract_collection_name(coll) == "The Avengers Collection"

def test_collection_none_is_nan():
    assert pd.isna(extract_collection_name(None))


# ---------- extract_director ----------

def test_director_found_among_crew():
    credits = {"crew": [
        {"name": "Kevin Feige", "job": "Producer"},
        {"name": "Anthony Russo", "job": "Director"},
    ]}
    assert extract_director(credits) == "Anthony Russo"

def test_director_missing_is_nan():
    assert pd.isna(extract_director({"crew": [{"name": "X", "job": "Editor"}]}))


# ---------- clean_movies (pipeline behavior) ----------

def make_raw_movie(**overrides):
    """A minimal but complete fake API response; override any field per test."""
    movie = {
        "id": 1, "title": "Test Movie", "tagline": "A tagline",
        "release_date": "2020-01-15", "status": "Released",
        "genres": [{"id": 28, "name": "Action"}],
        "belongs_to_collection": None,
        "original_language": "en",
        "budget": 100_000_000, "revenue": 250_000_000, "runtime": 120,
        "production_companies": [{"name": "Test Studio"}],
        "production_countries": [{"name": "United States of America"}],
        "spoken_languages": [{"english_name": "English"}],
        "vote_count": 500, "vote_average": 7.5, "popularity": 50.0,
        "overview": "A test overview.", "poster_path": "/x.jpg",
        "credits": {
            "cast": [{"name": "Actor One"}, {"name": "Actor Two"}],
            "crew": [{"name": "Jane Doe", "job": "Director"}],
        },
        # columns the pipeline should drop
        "adult": False, "imdb_id": "tt0000001", "original_title": "Test Movie",
        "video": False, "homepage": "",
    }
    movie.update(overrides)
    return movie


def test_zero_budget_becomes_nan_and_musd_conversion():
    df = clean_movies([make_raw_movie(budget=0)])
    assert pd.isna(df.loc[0, "budget_musd"])
    assert df.loc[0, "revenue_musd"] == 250.0  # 250_000_000 -> millions

def test_zero_votes_invalidates_rating():
    df = clean_movies([make_raw_movie(vote_count=0, vote_average=10.0)])
    assert pd.isna(df.loc[0, "vote_average"])

def test_unreleased_movies_are_dropped():
    df = clean_movies([make_raw_movie(), make_raw_movie(id=2, status="Rumored")])
    assert df["id"].tolist() == [1]

def test_duplicate_ids_are_deduplicated():
    df = clean_movies([make_raw_movie(), make_raw_movie()])
    assert len(df) == 1

def test_credits_flattened_into_four_columns():
    df = clean_movies([make_raw_movie()])
    row = df.iloc[0]
    assert row["cast"] == "Actor One|Actor Two"
    assert row["cast_size"] == 2
    assert row["director"] == "Jane Doe"
    assert row["crew_size"] == 1

def test_dropped_columns_are_gone_and_order_is_final():
    df = clean_movies([make_raw_movie()])
    for col in ["adult", "imdb_id", "original_title", "video", "homepage", "status", "credits"]:
        assert col not in df.columns
    assert df.columns[0] == "id" and df.columns[-1] == "crew_size"
