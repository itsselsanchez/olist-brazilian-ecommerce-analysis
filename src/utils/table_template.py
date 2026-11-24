import math
import re
import plotly.graph_objects as go
from src.config.colors import (
    TABLE_BACKGROUND,
    TABLE_TITLE_FONT_COLOR,
    TABLE_TITLE_BACKGROUND,
    TABLE_HEADER_FONT_COLOR,
    TABLE_LABEL_FONT_COLOR,
    TABLE_VALUE_FONT_COLOR,
    TABLE_CODE_FONT_COLOR,
    TABLE_BORDER_COLOR,
    TABLE_HEADER_BACKGROUND, 
    ROW_LIGHT, 
    ROW_DARK
)

# Ratio of char width to font size.
# Used to estimate how many lines Plotly will wrap a cell's text into.
CHAR_WIDTH_RATIO = 0.55

# Layout (pixels)
TABLE_WIDTH = 1000
TABLE_FONT_SIZE = 14
TABLE_TITLE_FONT_SIZE = 18
TABLE_LINE_HEIGHT = 20
TABLE_CELL_PADDING = 8
TABLE_TITLE_BAND_HEIGHT = 44


def _to_plotly_markup(value) -> str:
    """
    Translate the HTML used in table cells into the subset Plotly can render.
    """
    text = str(value)
    text = re.sub(
        r"<code>(.*?)</code>",
        rf'<span style="font-family:monospace;color:{TABLE_CODE_FONT_COLOR}">\1</span>',
        text,
    )
    return text.replace("<em>", "<i>").replace("</em>", "</i>")


def _estimate_lines(text: str, column_px: float) -> int:
    """
    Estimate how many lines Plotly will wrap a cell's text into.
    """
    chars_per_line = max(1, int(column_px / (TABLE_FONT_SIZE * CHAR_WIDTH_RATIO)))
    segments = re.split(r"<br\s*/?>", text)
    return sum(
        max(1, math.ceil(len(re.sub(r"<[^>]+>", "", s)) / chars_per_line))
        for s in segments
    )


def display_stylized_table(
    title: str,
    rows: list[tuple],
    headers: tuple | None = None,
) -> None:
    """
    Display a styled table with any number of columns.

    Rendered with Plotly on a transparent background, with every cell color set
    explicitly so the table stays legible regardless of the viewer's theme.
    """
    n_cols = len(rows[0])
    columns = [[_to_plotly_markup(row[c]) for row in rows] for c in range(n_cols)]

    # Size columns by their longest content
    content_lengths = [
        max(len(re.sub(r"<[^>]+>", "", cell)) for cell in col + ([str(headers[c])] if headers else []))
        for c, col in enumerate(columns)
    ]
    column_weights = [min(max(length, 8), 60) for length in content_lengths]
    column_px = [TABLE_WIDTH * w / sum(column_weights) - 2 * TABLE_CELL_PADDING for w in column_weights]

    row_heights = [
        max(_estimate_lines(columns[c][r], column_px[c]) for c in range(n_cols)) * TABLE_LINE_HEIGHT
        + 2 * TABLE_CELL_PADDING
        for r in range(len(rows))
    ]
    header_height = TABLE_LINE_HEIGHT + 2 * TABLE_CELL_PADDING if headers else 0

    fill_colors = [ROW_LIGHT if i % 2 == 0 else ROW_DARK for i in range(len(rows))]
    # Defaults to first column if there are no headers.
    font_colors = [
        [TABLE_LABEL_FONT_COLOR] * len(rows) if (c == 0 and headers is None) else [TABLE_VALUE_FONT_COLOR] * len(rows)
        for c in range(n_cols)
    ]
    if headers is None:
        columns[0] = [f"<b>{cell}</b>" for cell in columns[0]]

    fig = go.Figure(go.Table(
        columnwidth = column_weights,
        header = dict(
            values = [f"<b>{h}</b>" for h in headers] if headers else [""] * n_cols,
            fill_color = TABLE_HEADER_BACKGROUND,
            font = dict(color = TABLE_HEADER_FONT_COLOR, size = TABLE_FONT_SIZE),
            line_color = TABLE_BORDER_COLOR,
            align = "left",
            height = header_height if headers else 1,
        ),
        cells = dict(
            values = columns,
            fill_color = [fill_colors] * n_cols,
            font = dict(color = font_colors, size = TABLE_FONT_SIZE),
            line_color = TABLE_BORDER_COLOR,
            align = "left",
            height = TABLE_LINE_HEIGHT + 2 * TABLE_CELL_PADDING,
        ),
    ))

    title_band_height = TABLE_TITLE_BAND_HEIGHT
    bottom_margin = 4
    table_height = header_height + sum(row_heights) + 2  
    fig.add_shape(
        type = "rect", 
        xref = "paper", 
        yref = "paper",
        x0 = 0, 
        x1 = 1, 
        y0 = 1, 
        y1 = 1 + title_band_height / table_height,
        fillcolor = TABLE_TITLE_BACKGROUND, 
        line_width = 0,
    )
    fig.add_annotation(
        text = f"<b>{title}</b>", 
        xref = "paper", 
        yref = "paper",
        x = 0.5, 
        y = 1 + title_band_height / (2 * table_height),
        showarrow = False, 
        xanchor = "center", 
        yanchor = "middle",
        font = dict(
            size = TABLE_TITLE_FONT_SIZE, 
            color = TABLE_TITLE_FONT_COLOR
        ),
    )
    fig.update_layout(
        paper_bgcolor = TABLE_BACKGROUND,
        plot_bgcolor = TABLE_BACKGROUND,
        width = TABLE_WIDTH + 40,
        height = title_band_height + table_height + bottom_margin,
        margin = dict(
            l = 20, 
            r = 20, 
            t = title_band_height, 
            b = bottom_margin
        ),
    )
    fig.show(renderer = "png")
