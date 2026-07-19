"""KPI helpers for the analysis stage (project Step 3).

`add_financial_metrics` derives profit and ROI once, so every ranking and
groupby works from the same numbers. `rank_movies` is the ranking UDF the
project asks for: one function that covers all ten "best/worst" questions
instead of ten copy-pasted sort blocks.
"""


def add_financial_metrics(df):
    """Add profit_musd and roi as derived columns (returns a copy).

    ROI here is revenue / budget (as the brief defines it): 2.0 means the
    movie earned twice its budget. NaN budgets propagate to NaN ROI —
    honest, since we can't know the return without knowing the cost.
    """
    out = df.copy()
    out["profit_musd"] = out["revenue_musd"] - out["budget_musd"]
    out["roi"] = out["revenue_musd"] / out["budget_musd"]
    return out


def rank_movies(df, by, top_n=10, ascending=False, min_budget=None, min_votes=None):
    """Rank movies by any metric, with the brief's optional filters.

    min_budget guards ROI rankings (a 1 M$ film earning 20 M$ would
    otherwise dominate), min_votes guards rating rankings (a 10/10 from
    three voters isn't a signal).
    """
    result = df
    if min_budget is not None:
        result = result[result["budget_musd"] >= min_budget]
    if min_votes is not None:
        result = result[result["vote_count"] >= min_votes]
    return (
        result.dropna(subset=[by])
        .sort_values(by, ascending=ascending)
        .head(top_n)
    )
