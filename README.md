# TMDB Movie Data Analysis

A movie data analysis pipeline built with Python, Pandas, and the [TMDB API](https://developer.themoviedb.org/docs).
Fetches movie data, cleans and transforms it, computes KPIs (revenue, ROI, ratings),
and analyzes franchise/director performance.

## Pipeline

| Stage | Notebook | Reads | Writes |
|---|---|---|---|
| 1. Extraction | `notebooks/01_data_extraction.ipynb` | TMDB API | `data/raw/movies_raw.json` |
| 2. Cleaning | `notebooks/02_data_cleaning.ipynb` | `data/raw/` | `data/processed/movies_clean.csv` |
| 3. KPI Analysis | `notebooks/03_kpi_analysis.ipynb` | `data/processed/` | tables in notebook |
| 4. Visualization | `notebooks/04_visualization.ipynb` | `data/processed/` | `reports/figures/` |

Reusable logic lives in `src/` (API client, cleaning functions, ranking helpers).

## Setup

1. Create a virtual environment (Python 3.12) and install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Get a free API key from [TMDB](https://www.themoviedb.org/settings/api) and put it in a `.env` file
   in the project root:

   ```
   TMDB_API_KEY=your_key_here
   ```

3. Run the notebooks in order (01 → 04).
