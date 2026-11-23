import numpy as np
import plotly.graph_objects as go
from src.utils.color_mixer import with_alpha


def calculate_distribution_metrics(series, bins=15):
    """Compute histogram counts and the cumulative percentage at each bin edge."""
    clean_data = series.dropna()

    counts, edges = np.histogram(clean_data, bins=bins)
    centers = (edges[:-1] + edges[1:]) / 2
    cum_pct = np.cumsum(counts) / counts.sum() * 100

    return {
        "counts": counts,
        "centers": centers,
        "edges": edges,
        "cum_pct": np.concatenate([[0], cum_pct]),
    }


def create_distribution_bars(metrics, color_hex, bar_name="Items"):
    """Generate a frequency bar trace."""
    return go.Bar(
        x=metrics["centers"],
        y=metrics["counts"],
        marker=dict(
            color=with_alpha(color_hex, 0.45),
            line=dict(color=color_hex, width=0.8),
        ),
        name=bar_name,
    )


def create_percentage_line(metrics, color_hex, line_name="Cumulative %"):
    """Generate the cumulative-percentage line trace."""
    return go.Scatter(
        x=metrics["edges"],
        y=metrics["cum_pct"],
        mode="lines",
        line=dict(color=color_hex, width=2.5),
        name=line_name,
    )