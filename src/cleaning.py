"""Cleaning & transformation of raw TMDB data (project Step 2).

The raw API responses contain nested JSON (lists of dicts inside single
fields), zeros that really mean "unknown", and columns we don't need.
These functions turn that into a flat, typed, analysis-ready table.

Small extractor functions live at the top; `clean_movies` composes them
into the full pipeline so every notebook (and test) runs the exact same
transformation.
"""

import numpy as np
import pandas as pd

DROP_COLUMNS = ["adult", "imdb_id", "original_title", "video", "homepage"]

# Text the API uses when it has nothing to say — treat as missing.
PLACEHOLDERS = ["No Data", "No overview found.", ""]

FINAL_COLUMNS = [
    "id", "title", "tagline", "release_date", "genres", "belongs_to_collection",
    "original_language", "budget_musd", "revenue_musd", "production_companies",
    "production_countries", "vote_count", "vote_average", "popularity", "runtime",
    "overview", "spoken_languages", "poster_path", "cast", "cast_size",
    "director", "crew_size",
]


def extract_names(items, key="name", sep="|"):
    """Flatten a list of dicts into a single string: 'Action|Adventure'.

    Returns NaN for anything that isn't a non-empty list, so missing and
    empty values end up looking the same to Pandas.
    """
    if not isinstance(items, list) or len(items) == 0:
        return np.nan
    names = [item[key] for item in items if item.get(key)]
    return sep.join(names) if names else np.nan


def extract_collection_name(collection):
    """belongs_to_collection is a single dict (or None) — pull out its name."""
    if isinstance(collection, dict):
        return collection.get("name", np.nan)
    return np.nan


def extract_director(credits):
    """Find the crew member whose job is 'Director'."""
    if not isinstance(credits, dict):
        return np.nan
    for member in credits.get("crew", []):
        if member.get("job") == "Director":
            return member["name"]
    return np.nan


def clean_movies(raw_movies):
    """Full Step-2 pipeline: list of raw API dicts -> analysis-ready DataFrame."""
    df = pd.DataFrame(raw_movies)

    # 1. Irrelevant columns out first — less to look at in every later step.
    df = df.drop(columns=[c for c in DROP_COLUMNS if c in df.columns])

    # 2-3. Flatten the nested JSON columns.
    df["belongs_to_collection"] = df["belongs_to_collection"].apply(extract_collection_name)
    for col in ["genres", "production_countries", "production_companies"]:
        df[col] = df[col].apply(extract_names)
    df["spoken_languages"] = df["spoken_languages"].apply(
        lambda x: extract_names(x, key="english_name")
    )

    # Credits -> cast, cast_size, director, crew_size.
    df["cast"] = df["credits"].apply(
        lambda c: extract_names(c.get("cast")) if isinstance(c, dict) else np.nan
    )
    df["cast_size"] = df["credits"].apply(
        lambda c: len(c.get("cast", [])) if isinstance(c, dict) else 0
    )
    df["director"] = df["credits"].apply(extract_director)
    df["crew_size"] = df["credits"].apply(
        lambda c: len(c.get("crew", [])) if isinstance(c, dict) else 0
    )
    df = df.drop(columns=["credits"])

    # 5. Types: coerce turns anything unparseable into NaN instead of crashing.
    for col in ["budget", "id", "popularity"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df["release_date"] = pd.to_datetime(df["release_date"], errors="coerce")

    # 6. A budget/revenue/runtime of 0 means "unknown", not "free to make".
    df[["budget", "revenue", "runtime"]] = df[["budget", "revenue", "runtime"]].replace(0, np.nan)
    df["budget_musd"] = df["budget"] / 1e6
    df["revenue_musd"] = df["revenue"] / 1e6
    df = df.drop(columns=["budget", "revenue"])

    # A rating averaged over zero votes is meaningless — mark it missing.
    df.loc[df["vote_count"] == 0, "vote_average"] = np.nan
    df[["overview", "tagline"]] = df[["overview", "tagline"]].replace(PLACEHOLDERS, np.nan)

    # 7-9. Row-level filters.
    df = df.drop_duplicates(subset="id")
    df = df.dropna(subset=["id", "title"])
    df = df.dropna(thresh=10)
    df = df[df["status"] == "Released"].drop(columns=["status"])

    # 10-11. Final shape.
    return df[FINAL_COLUMNS].reset_index(drop=True)


def validate(df):
    """Data checks at the pipeline boundary — fail loudly, not silently."""
    assert df["id"].is_unique, "duplicate movie ids"
    assert df["title"].notna().all(), "movie without a title"
    assert str(df["release_date"].dtype).startswith("datetime64"), "release_date not datetime"
    assert (df["budget_musd"].dropna() > 0).all(), "non-positive budget"
    assert (df["revenue_musd"].dropna() > 0).all(), "non-positive revenue"
    assert list(df.columns) == FINAL_COLUMNS, "unexpected column order"
    print(f"All validation checks passed ✔  ({len(df)} movies, {df.shape[1]} columns)")
