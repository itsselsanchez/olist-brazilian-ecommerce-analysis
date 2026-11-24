import numpy as np
import pandas as pd
import geopandas as gpd
import plotly.graph_objects as go
from matplotlib.colors import to_rgb, to_hex
from src.maps.brazil_map import BrazilMap
from src.config.brazil_map_template import SURROUNDING_COUNTRY_CODES
from src.config.colors import (
    BIVARIATE_LOW, 
    BIVARIATE_X_HIGH, 
    BIVARIATE_Y_HIGH,
    LAND_MUTED,
    TRANSPARENT,
    BIVARIATE_BACKGROUND,
    BIVARIATE_COUNTRY_LINE,
    BIVARIATE_OUTLINE,
    BIVARIATE_EMPTY_CITY,
    BIVARIATE_CITY_LINE,
    LABEL,
)


def bivariate_index(
    x: pd.Series, 
    y: pd.Series, 
    n_bins: int = 3
) -> pd.Series:
    """
    Quantile-bin two variables and combine them into one class index.
    index = y_bin * n_bins + x_bin, so 0 is low/low and n_bins**2 - 1 is high/high.
    NaNs in either input produce a NaN index.
    """
    labels = list(range(n_bins))
    x_bin = pd.qcut(x, q = n_bins, labels = labels, duplicates = "drop").astype(float)
    y_bin = pd.qcut(y, q = n_bins, labels = labels, duplicates = "drop").astype(float)
    return y_bin * n_bins + x_bin


def build_bivariate_palette(
    low: str = BIVARIATE_LOW,
    x_high: str = BIVARIATE_X_HIGH,
    y_high: str = BIVARIATE_Y_HIGH,
    n_bins: int = 3,
) -> list[str]:
    """
    Blend a low/low anchor toward two high-axis anchors.
    Returns n_bins**2 hex colors ordered to match bivariate_index.
    """
    low, x_high, y_high = (np.array(to_rgb(c)) for c in (low, x_high, y_high))
    palette = []
    for y_bin in range(n_bins):
        for x_bin in range(n_bins):
            x_t, y_t = x_bin / (n_bins - 1), y_bin / (n_bins - 1)
            rgb = low + x_t * (x_high - low) + y_t * (y_high - low)
            palette.append(to_hex(np.clip(rgb, 0, 1)))
    return palette


def stepped_colorscale(palette: list[str]) -> list[list]:
    """Hard-edged colorscale so each integer class renders as one flat color."""
    n = len(palette)
    scale = []
    for i, color in enumerate(palette):
        scale.append([i / n, color])
        scale.append([(i + 1) / n, color])
    return scale


class BivariateBrazilMap(BrazilMap):
    """BrazilMap with a bivariate choropleth layer and a matching grid legend.
    Overrides the template's land colors with a darker scheme so the palette reads clearly.
    """

    def __init__(self, brazil_outline: gpd.GeoDataFrame, **kwargs):
        background = dict(
            paper_bgcolor = BIVARIATE_BACKGROUND,
            plot_bgcolor = BIVARIATE_BACKGROUND,
            geo = dict(bgcolor = BIVARIATE_BACKGROUND),
        )
        super().__init__(brazil_outline, **{**background, **kwargs})

    # ---- base map overrides ----

    def _add_surrounding_countries(self) -> None:
        self.base_map.add_trace(
            go.Choropleth(
                z = [0] * len(SURROUNDING_COUNTRY_CODES),
                locations = SURROUNDING_COUNTRY_CODES,
                locationmode = "ISO-3",
                colorscale = [[0, LAND_MUTED], [1, LAND_MUTED]],
                showscale = False,
                marker_line_color = BIVARIATE_COUNTRY_LINE,
                marker_line_width = 0.5,
                hoverinfo = "skip",
            )
        )

    def _add_brazil_country_outline(self) -> None:
        self.base_map.add_trace(
            go.Choropleth(
                geojson = self.brazil_outline.__geo_interface__,
                locations = self.brazil_outline.index,
                z = [0] * len(self.brazil_outline),
                colorscale = [[0, TRANSPARENT], [1, TRANSPARENT]],
                showscale = False,
                marker_line_color = BIVARIATE_OUTLINE,
                marker_line_width = 1.0,
                hoverinfo = "skip",
            )
        )

    def add_brazil_municipalities(
        self, 
        brazil_municipalities: gpd.GeoDataFrame
    ) -> "BivariateBrazilMap":
        """Faint outlines for every city, so unclassified ones still show."""
        self.base_map.add_trace(
            go.Choropleth(
                geojson = brazil_municipalities.__geo_interface__,
                locations = brazil_municipalities.index,
                z = [0] * len(brazil_municipalities),
                colorscale = [[0, BIVARIATE_EMPTY_CITY], [1, BIVARIATE_EMPTY_CITY]],
                showscale = False,
                marker_line_color = BIVARIATE_CITY_LINE,
                marker_line_width = 0.3,
                hoverinfo = "skip",
            )
        )
        return self

    # ---- data layers ----

    def add_bivariate_layer(
        self,
        gdf: gpd.GeoDataFrame,
        index_col: str = "bivar_idx",
        palette: list[str] | None = None,
        line_width: float = 0.1,
    ) -> "BivariateBrazilMap":
        """Fill polygons by their bivariate class. Rows with no class are skipped."""
        palette = palette or build_bivariate_palette()
        plottable = gdf.dropna(subset=[index_col])
        self.base_map.add_trace(
            go.Choropleth(
                geojson = plottable.__geo_interface__,
                locations = plottable.index,
                z = plottable[index_col],
                colorscale = stepped_colorscale(palette),
                zmin = -0.5,
                zmax = len(palette) - 0.5,
                showscale = False,
                marker_line_color = BIVARIATE_COUNTRY_LINE,
                marker_line_width = line_width,
                hoverinfo = "skip",
            )
        )
        return self

    def add_bivariate_legend(
        self,
        x_title: str,
        y_title: str,
        palette: list[str] | None = None,
        x: float = 0.80,
        y: float = 0.08,
        size: float = 0.14,
        low_label: str = "Low",
        high_label: str = "High",
    ) -> "BivariateBrazilMap":
        """
        Draw an n by n grid legend with its bottom-left corner at (x, y) in paper coords.
        size is the grid width as a fraction of the plot width; cells stay square.
        """
        palette = palette or build_bivariate_palette()
        n_bins = int(round(len(palette) ** 0.5))
        cell_w = size / n_bins
        cell_h = cell_w * self._plot_aspect()
        top, right = y + cell_h * n_bins, x + size

        for idx, color in enumerate(palette):
            row, col = divmod(idx, n_bins)
            self.base_map.add_shape(
                type = "rect", 
                xref = "paper", 
                yref = "paper",
                x0 = x + col * cell_w, x1=x + (col + 1) * cell_w,
                y0 = y + row * cell_h, y1=y + (row + 1) * cell_h,
                fillcolor = color,
                line = dict(color = BIVARIATE_BACKGROUND, width = 1),
            )
        axis_font = dict(color = LABEL, size = 10)
        tick_font = dict(color = LABEL, size = 8)
        gap = 0.012

        # Horizontal axis: Low → High under the columns, title below
        for text, cx in (
            (low_label, x + cell_w / 2), 
            ("→", (x + right) / 2), 
            (high_label, right - cell_w / 2)
        ):
            self._legend_text(
                text, 
                cx, 
                y - gap, 
                tick_font, 
                yanchor="top"
            )
        self._legend_text(
            x_title, 
            (x + right) / 2, 
            y - 3 * gap, 
            axis_font, 
            yanchor="top"
        )

        # Vertical axis: Low → High beside the rows (rotated, so the arrow points up), title to the left
        for text, cy in (
            (low_label, y + cell_h / 2), 
            ("→", (y + top) / 2), 
            (high_label, top - cell_h / 2)
        ):
            self._legend_text(
                text,
                x - gap,
                cy, tick_font, 
                xanchor="right", 
                textangle=-90
            )
        self._legend_text(
            y_title, 
            x - 3 * gap, 
            (y + top) / 2, 
            axis_font, 
            xanchor="right", 
            textangle=-90
        )
        return self

    # ---- helpers ----

    def _legend_text(
        self, 
        text: str, 
        x: float, 
        y: float, 
        font: dict, 
        **kwargs
    ) -> None:
        defaults = dict(xanchor = "center", yanchor = "middle")
        self.base_map.add_annotation(
            text = text, 
            xref = "paper", 
            yref = "paper", 
            x = x, 
            y = y,
            showarrow = False, 
            font = font, 
            **{**defaults, **kwargs},
        )

    def _plot_aspect(self) -> float:
        """Plot-area width / height. Keeps legend as squares."""
        m = self.base_map.layout.margin
        width = self.width - (m.l or 0) - (m.r or 0)
        height = self.height - (m.t or 0) - (m.b or 0)
        return width / height
