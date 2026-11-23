from plotly.subplots import make_subplots
from src.config.charts_template import custom_dark
from src.config.colors import SKY, MAGENTA
from src.charts.distributions import calculate_distribution_metrics, create_distribution_bars, create_percentage_line


def build_cumulative_combo_chart(
    series,
    bins=15,
    title="Distribution Analysis",
    x_label="Value Axis",
    y_left_label="Count",
    bar_name="Items",
    bar_color=SKY,
    line_color=MAGENTA,
):
    """Build a histogram with a cumulative-percentage line on a second axis."""
    metrics = calculate_distribution_metrics(series, bins=bins)
    
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        create_distribution_bars(metrics, bar_color, bar_name=bar_name), 
        secondary_y=False
    )
    fig.add_trace(
        create_percentage_line(metrics, line_color), 
        secondary_y=True
    )

    fig.update_layout(
        template=custom_dark,
        title=title,
        bargap=0.00,
        barmode="overlay",
        showlegend=False,
    )
    fig.update_xaxes(title_text=x_label)
    fig.update_yaxes(
        title_text=y_left_label, 
        secondary_y=False, 
        showgrid=False
    )
    fig.update_yaxes(
        title_text="Cumulative %", 
        range=[0, 100], 
        secondary_y=True, 
        showgrid=False
    )

    return fig