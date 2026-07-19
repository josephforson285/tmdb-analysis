"""Unit tests for src/analysis.py — run with:  python -m pytest"""

import numpy as np
import pandas as pd
import pytest

from src.analysis import add_financial_metrics, rank_movies


@pytest.fixture
def movies():
    """Four tiny movies exercising the edge cases the helpers must handle."""
    return pd.DataFrame({
        "title": ["Blockbuster", "Indie Hit", "Flop", "No Budget Data"],
        "budget_musd": [200.0, 5.0, 150.0, np.nan],
        "revenue_musd": [1000.0, 100.0, 75.0, 500.0],
        "vote_count": [5000, 200, 8, 1000],
        "vote_average": [8.0, 7.5, 9.9, 6.0],
    })


def test_profit_and_roi(movies):
    out = add_financial_metrics(movies)
    assert out.loc[0, "profit_musd"] == 800.0
    assert out.loc[1, "roi"] == 20.0            # 100 / 5
    assert pd.isna(out.loc[3, "roi"])           # unknown budget -> unknown ROI

def test_original_df_untouched(movies):
    add_financial_metrics(movies)
    assert "roi" not in movies.columns          # helper must not mutate input

def test_rank_descending_by_default(movies):
    top = rank_movies(movies, by="revenue_musd", top_n=2)
    assert top["title"].tolist() == ["Blockbuster", "No Budget Data"]

def test_rank_ascending_for_worst(movies):
    worst = rank_movies(movies, by="revenue_musd", top_n=1, ascending=True)
    assert worst["title"].tolist() == ["Flop"]

def test_min_budget_filter_guards_roi(movies):
    out = add_financial_metrics(movies)
    top_roi = rank_movies(out, by="roi", min_budget=10)
    assert "Indie Hit" not in top_roi["title"].tolist()   # 5 M$ budget excluded

def test_min_votes_filter_guards_ratings(movies):
    top_rated = rank_movies(movies, by="vote_average", min_votes=10)
    assert "Flop" not in top_rated["title"].tolist()      # 8 votes excluded

def test_nan_in_ranking_metric_is_dropped(movies):
    out = add_financial_metrics(movies)
    ranked = rank_movies(out, by="roi", top_n=10)
    assert "No Budget Data" not in ranked["title"].tolist()
