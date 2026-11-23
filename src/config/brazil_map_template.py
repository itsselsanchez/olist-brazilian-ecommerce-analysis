import plotly.graph_objects as go
from src.config.colors import (
    BACKGROUND,
    LAND_MUTED,
    LABEL,
    TITLE,
)

MAP_CRS = 4326

SURROUNDING_COUNTRY_CODES = [
    "ARG", "CHL", "PER", "BOL", "PRY",
    "URY", "COL", "VEN", "ECU", "GUY",
    "SUR", "GUF", "FLK",
]

COUNTRY_LABELS = [
    ("Brazil",    -9,    -53),
    ("Argentina", -30,   -65),
    ("Chile",     -23.3, -69),
    ("Peru",      -10,   -75),
    ("Bolivia",   -17,   -65),
    ("Paraguay",  -23.2, -58),
    ("Uruguay",   -33,   -56),
    ("Colombia",   4,    -73),
    ("Venezuela",  7,    -66),
    ("Ecuador",   -1,    -78),
]

# Dark-themed Plotly template for Brazil-focused geographic maps.
brazil_dark = go.layout.Template(
    layout=dict(
        # Page background
        paper_bgcolor=BACKGROUND,
        plot_bgcolor=BACKGROUND,

        # Margins default to zero to maximize map area
        margin=dict(l=0, r=0, t=0, b=0),

        # Default text
        font=dict(color=LABEL),
        title=dict(font=dict(color=TITLE)),

        geo=dict(
            # Map background 
            bgcolor=BACKGROUND,
            showframe=False,

            visible=False,
            showland=True,
            landcolor=LAND_MUTED,        
            showcountries=False,
            showlakes=False,
            showcoastlines=False,

            # Brazil-focused view 
            projection=dict(type="equirectangular"),
            lonaxis=dict(range=[-74.5, -34]),
            lataxis=dict(range=[-34, 6]),
            
            # Full figure canvas
            domain=dict(x=[0, 1], y=[0, 1]),

            # Silhouette detail for the land shapes
            resolution=50,
        ),
    )
)