import pandas as pd
import plotly.graph_objects as go

from src.config.charts_template import custom_dark
from src.config.colors import SKY


def build_time_series_chart(
    monthly_df: pd.DataFrame,  
    title: str,
    y_label: str,
    color: str = SKY,
) -> go.Figure:
    """
    Build a single-line monthly time series chart.
    """
    fig = go.Figure(go.Scatter(
        x=monthly_df["month"].dt.strftime("%Y-%m-%d"),
        y=monthly_df["value"],
        mode="lines+markers",
        line=dict(color=color, width=2.5),
        marker=dict(size=5),
    ))

    fig.update_layout(template=custom_dark, title=title, showlegend=False)
    fig.update_xaxes(title_text="Month")
    fig.update_yaxes(title_text=y_label, showgrid=False)
    return fig
