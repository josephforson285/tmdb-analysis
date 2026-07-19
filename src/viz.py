"""Shared plotting style for the visualization stage (project Step 4).

One place defines the look — colors, grid, spines, saving — so every chart
in notebook 04 is consistent and the plotting cells stay about the *data*.

Colors follow a validated palette: one blue for single-series charts, green
only when a second identity appears (e.g. Standalone vs Franchise). Identity
is never carried by color alone — bars/points are also named by tick labels
or direct annotations.
"""

from pathlib import Path

# palette (light surface)
BLUE = "#2a78d6"        # primary series
BLUE_DARK = "#104281"   # emphasis (medians, annotations)
GREEN = "#008300"       # second series
INK = "#0b0b0b"         # titles
MUTED = "#898781"       # axis labels, secondary text
GRID = "#e1e0d9"        # hairline gridlines
BASELINE = "#c3c2b7"    # visible spines
SURFACE = "#fcfcfb"     # chart background

FIGURES_DIR = Path(__file__).resolve().parent.parent / "reports" / "figures"


def apply_style(ax, title=None, xlabel=None, ylabel=None):
    """Recessive chrome: light grid under the data, minimal spines, muted ink."""
    ax.set_facecolor(SURFACE)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(BASELINE)
    ax.tick_params(colors=MUTED, labelsize=9)
    ax.grid(True, color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)          # grid behind the marks, never over them
    if title:
        ax.set_title(title, color=INK, fontsize=12, loc="left", pad=12)
    if xlabel:
        ax.set_xlabel(xlabel, color=MUTED, fontsize=10)
    if ylabel:
        ax.set_ylabel(ylabel, color=MUTED, fontsize=10)


def label_points(ax, df, titles, x, y, dx=6, dy=4, fontsize=8.5):
    """Direct-label a *selection* of scatter points (never every point)."""
    for _, row in df[df["title"].isin(titles)].iterrows():
        ax.annotate(
            row["title"], (row[x], row[y]),
            xytext=(dx, dy), textcoords="offset points",
            fontsize=fontsize, color=INK,
        )


def save_fig(fig, name):
    """Save to reports/figures/ for embedding in the final report."""
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    path = FIGURES_DIR / name
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor=SURFACE)
    print(f"saved -> reports/figures/{name}")
