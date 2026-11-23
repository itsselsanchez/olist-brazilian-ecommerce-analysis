import plotly.graph_objects as go
from src.config.colors import (
    BACKGROUND, 
    LABEL,
    TITLE, 
    GRIDLINE,
    CATEGORY_PALETTE, 
    SEQ_TEAL, 
    DIV_CORAL_TEAL,
)

custom_dark = go.layout.Template()

custom_dark.layout = dict(
    paper_bgcolor=BACKGROUND,
    plot_bgcolor=BACKGROUND,
    font=dict(color=LABEL),
    title=dict(font=dict(color=TITLE), x=0.5),

    colorway=CATEGORY_PALETTE,
    colorscale=dict(
        sequential=SEQ_TEAL,
        sequentialminus=SEQ_TEAL,
        diverging=DIV_CORAL_TEAL,
    ),
    coloraxis=dict(colorbar=dict(outlinewidth=0, ticks="", thickness=12)),

    xaxis=dict(
        gridcolor=GRIDLINE, 
        linecolor=GRIDLINE, 
        zerolinecolor=GRIDLINE,
        tickcolor=GRIDLINE, 
        ticks="outside", 
        automargin=True,
        title=dict(standoff=15),
    ),
    yaxis=dict(
        gridcolor=GRIDLINE, 
        linecolor=GRIDLINE, 
        zerolinecolor=GRIDLINE,
        tickcolor=GRIDLINE, 
        ticks="outside", 
        automargin=True,
        title=dict(standoff=15),
    ),
)