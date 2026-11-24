import pandas as pd
import plotly.graph_objects as go
import numpy as np
from plotly.colors import sample_colorscale
from src.config.colors import TEAL, CORAL, SKY


def select_representative_routes(
    df: pd.DataFrame,
    distance_col: str,
    bucket_edges: list[float],
    n_per_bucket: int = 15,
    random_state: int = 42,
) -> pd.DataFrame:
    """
    Return up to n_per_bucket sampled routes per distance bucket,
    with a 'bucket_count' column for line-width scaling.
    """
    buckets = pd.cut(df[distance_col], bins=bucket_edges)
    counts = df.groupby(buckets, observed=True).size()

    reps = []
    for bucket, group in df.groupby(buckets, observed=True):
        if group.empty:
            continue
        sample = group.sample(n=min(len(group), n_per_bucket), random_state=random_state).copy()
        sample["bucket_count"] = counts[bucket]
        reps.append(sample)

    return pd.concat(reps, ignore_index=True)

def add_route_endpoints(
    fig: go.Figure,
    df: pd.DataFrame,
    start_lat_col: str,
    start_lon_col: str,
    end_lat_col: str,
    end_lon_col: str,
    start_color: str = CORAL,    # seller
    end_color: str = TEAL,       # customer
    size: int = 3,
) -> go.Figure:
    """
    Add start (circle) and end (x) markers for each route.
    """
    fig.add_trace(go.Scattergeo(
        lat = df[start_lat_col],
        lon = df[start_lon_col],
        mode = "markers",
        marker = dict(symbol = "circle", color = start_color, size = size),
        hoverinfo = "skip",
        showlegend = False,
    ))

    fig.add_trace(go.Scattergeo(
        lat = df[end_lat_col],
        lon = df[end_lon_col],
        mode = "markers",
        marker = dict(symbol="x", color=end_color, size=size),
        hoverinfo = "skip",
        showlegend = False,
    ))
    return fig

def add_representative_routes(
    fig: go.Figure,
    df: pd.DataFrame,
    start_lat_col: str,
    start_lon_col: str,
    end_lat_col: str,
    end_lon_col: str,
    count_col: str = "bucket_count",
    color: str = SKY,
    min_width: float = 0.5,
    max_width: float = 4.0,
    opacity: float = 0.5,
) -> go.Figure:
    """
    Draw one white line per route, width scaled to count_col.
    """
    counts = df[count_col]
    c_min, c_max = counts.min(), counts.max()

    for _, row in df.iterrows():
        norm = (row[count_col] - c_min) / (c_max - c_min) if c_max > c_min else 0.5
        width = min_width + norm * (max_width - min_width)

        fig.add_trace(go.Scattergeo(
            lat = [row[start_lat_col], row[end_lat_col]],
            lon = [row[start_lon_col], row[end_lon_col]],
            mode = "lines",
            line = dict(color = color, width = width),
            opacity = opacity,
            hoverinfo = "skip",
            showlegend = False,
        ))
    return fig

def find_density_peak(
    lat: pd.Series,
    lon: pd.Series,
    density: np.ndarray,
) -> tuple[float, float]:
    """
    Return the (lat, lon) of the highest-density point.
    """
    idx = np.argmax(density)
    return float(lat.iloc[idx]), float(lon.iloc[idx])

def add_radius_circle(
    fig: go.Figure,
    center_lat: float,
    center_lon: float,
    radius_miles: float,
    color: str = TEAL,
    opacity: float = 0.4,
    width: float = 1.0,
    n_points: int = 100,
) -> go.Figure:
    """
    Draw a great-circle radius around a point on a Scattergeo map.
    """
    radius_deg = radius_miles / 69.0  # rough miles-per-degree
    angles = np.linspace(0, 2 * np.pi, n_points)
    lats = center_lat + radius_deg * np.cos(angles)
    lons = center_lon + radius_deg * np.sin(angles) / np.cos(np.radians(center_lat))

    fig.add_trace(go.Scattergeo(
        lat = lats, 
        lon = lons,
        mode = "lines",
        line = dict(color = color, width = width, dash = "dot"),
        opacity = opacity,
        hoverinfo = "skip",
        showlegend = False,
    ))
    return fig

def select_quantile_routes(
    df: pd.DataFrame,
    distance_col: str,
    quantiles: list[float] = [0.25, 0.50, 0.75, 1.0],
    random_state: int = 42,
) -> pd.DataFrame:
    """
    Pick one route per quantile, closest to that quantile's distance.
    Ties broken randomly.
    """
    rng = np.random.default_rng(random_state)
    targets = df[distance_col].quantile(quantiles).values

    picks = []
    for q, target in zip(quantiles, targets):
        diffs = (df[distance_col] - target).abs()
        candidates = df[diffs == diffs.min()]
        pick = candidates.sample(n = 1, random_state = rng.integers(0, 1_000_000)).copy()
        pick["quantile"] = q
        pick["target_distance"] = target
        picks.append(pick)

    return pd.concat(picks, ignore_index=True)


def add_curved_routes(
    fig: go.Figure,
    df: pd.DataFrame,
    start_lat_col: str,
    start_lon_col: str,
    end_lat_col: str,
    end_lon_col: str,
    distance_col: str,
    colorscale: str = "OrRd",
    line_width: float = 2.5,
    opacity: float = 0.9,
    n_arc_points: int = 50,
    arc_height: float = 0.15,
) -> go.Figure:
    """
    Draw curved routes colored by distance, with arrow at the end.
    """
    dist_min = df[distance_col].min()
    dist_max = df[distance_col].max()

    for _, row in df.sort_values(distance_col).iterrows():
        normalized = (row[distance_col] - dist_min) / (dist_max - dist_min) if dist_max > dist_min else 0.5
        color = sample_colorscale(colorscale, [normalized])[0]

        # Build arc using quadratic Bezier
        t = np.linspace(0, 1, n_arc_points)
        mid_lat = (row[start_lat_col] + row[end_lat_col]) / 2
        mid_lon = (row[start_lon_col] + row[end_lon_col]) / 2
        # Offset midpoint perpendicular to the line for curvature
        dx = row[end_lon_col] - row[start_lon_col]
        dy = row[end_lat_col] - row[start_lat_col]
        length = np.sqrt(dx**2 + dy**2)
        mid_lat += -dx / length * arc_height * length
        mid_lon += dy / length * arc_height * length

        lats = (1-t)**2 * row[start_lat_col] + 2*(1-t)*t * mid_lat + t**2 * row[end_lat_col]
        lons = (1-t)**2 * row[start_lon_col] + 2*(1-t)*t * mid_lon + t**2 * row[end_lon_col]

        fig.add_trace(go.Scattergeo(
            lat = lats, 
            lon = lons,
            mode = "lines",
            line = dict(color = color, width = line_width),
            opacity = opacity,
            hoverinfo = "skip",
            showlegend = False,
        ))

    return fig