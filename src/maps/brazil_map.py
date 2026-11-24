import plotly.graph_objects as go
import geopandas as gpd
from src.config.brazil_map_template import (
    brazil_dark, 
    SURROUNDING_COUNTRY_CODES, 
    COUNTRY_LABELS, 
)
from src.config.colors import (
    LABEL,
    TRANSPARENT,
    LAND_MUTED,
    OUTLINE,
    BORDER,
    LAND
)

class BrazilMap:
    def __init__(
            self,
            brazil_outline: gpd.GeoDataFrame,
            height: int = 800,
            width: int = 750,
            template: go.layout.Template = brazil_dark,
            **custom_layout_kwargs
        ):
        """A dark-themed base map with surrounding countries, outline, and labels."""
        self.template = template
        self.width = width
        self.height = height
        self.user_overrides = custom_layout_kwargs
        self.brazil_outline = brazil_outline
        self._create_base_map()
        self._add_surrounding_countries()
        self._add_brazil_country_outline()
        self._add_country_labels()

    # ---- base map ----
    
    def _create_base_map(self) -> None:
        """Create empty base map with custom template"""
        self.base_map = go.Figure()
        self.base_map.update_layout(
            template = self.template,
            width = self.width, 
            height = self.height,
            **self.user_overrides
        )
    
    def _add_surrounding_countries(self) -> None: 
        """Add surrounding countries to the base map with a distinct color."""
        self.base_map.add_trace(
            go.Choropleth(
                z=[0] * len(SURROUNDING_COUNTRY_CODES),
                locations = SURROUNDING_COUNTRY_CODES,
                locationmode = "ISO-3",
                colorscale = [[0, LAND_MUTED], [1, LAND_MUTED]],
                showscale = False,
                hoverinfo = "skip"
            )
        )
    
    def _add_brazil_country_outline(self) -> None:
        """Add Brazil country outline to the base map."""
        self.base_map.add_trace(
            go.Choropleth(
                geojson = self.brazil_outline.__geo_interface__,
                locations = self.brazil_outline.index,
                z=[0] * len(self.brazil_outline),
                colorscale = [[0, LAND], [1, LAND]],
                showscale = False,
                marker_line_color = OUTLINE,
                marker_line_width = 1.2,
                hoverinfo = "skip"
            )
        )

    def _add_country_labels(self) -> None:
        """Add country labels to the base map."""
        names, lats, lons = zip(*COUNTRY_LABELS)
        self.base_map.add_trace(
            go.Scattergeo(
                lat = lats,
                lon = lons,
                text = names,
                textfont = dict(color=LABEL, size=10),
                mode = "text",
                hoverinfo = "skip",
                showlegend = False,
            )
        )
    # ---- inner boundaries ----
    
    def _add_boundary_layer(
            self, 
            gdf: gpd.GeoDataFrame, 
            line_width: float
        ) -> "BrazilMap":
        """Add a boundary layer to the base map."""
        self.base_map.add_trace(
            go.Choropleth(
                geojson = gdf.__geo_interface__,
                locations = gdf.index,
                z = [1] * len(gdf),
                colorscale = [[0, LAND], [1, LAND]],
                showscale = False,
                marker_line_color = BORDER,
                marker_line_width = line_width,
                hoverinfo = "skip",
            )
        )
        return self
    
    def add_brazil_states(self, brazil_states: gpd.GeoDataFrame) -> "BrazilMap":
        """Add Brazil state boundaries to the base map."""
        return self._add_boundary_layer(brazil_states, line_width=0.7)

    def add_brazil_municipalities(self, brazil_municipalities: gpd.GeoDataFrame) -> "BrazilMap":
        """Add Brazil municipality boundaries to the base map."""
        return self._add_boundary_layer(brazil_municipalities, line_width=0.15)

    # ---- data layers ----
    
    def add_scatter(self, lat, lon, **kwargs) -> "BrazilMap":
        """Add a Scattergeo layer: markers, lines, or text."""
        defaults = dict(hoverinfo = "skip", showlegend = False)
        self.base_map.add_trace(
            go.Scattergeo(lat = lat, lon = lon, **{**defaults, **kwargs})
        )
        return self
    
    def add_density_layer(
        self,
        lat,
        lon,
        density,
        colorscale: str,
        title: str,
        name: str | None = None,
        opacity: float = 0.35,
        size: int = 1.7,
        show_colorbar: bool = True,
        colorbar_x: float = 1.0,
        colorbar_y: float = 0.5,
        length: float = 0.32,
    ) -> "BrazilMap":
        """Scatter points colored by a value + matching colorbar."""
        self.base_map.add_trace(
            go.Scattergeo(
                lat = lat,
                lon = lon,
                name = name,
                mode = "markers",
                marker = dict(
                    color = density, 
                    colorscale = colorscale, 
                    opacity = opacity, 
                    size = size
                ),
                showlegend = name is not None,
                hoverinfo = "skip",
            )
        )
        if show_colorbar:
            self._add_colorbar(
                density, 
                colorscale, 
                title,
                colorbar_x = colorbar_x, 
                colorbar_y = colorbar_y, 
                length = length,
            )
        return self

    def _add_colorbar(
        self,
        values,
        colorscale: str,
        title: str,
        colorbar_x: float = 1.0,
        colorbar_y: float = 0.5,
        length: float = 0.32,
        low_label: str = "Low",
        high_label: str = "High",
    ) -> None:
        """Add a colorbar to the base map."""
        self.base_map.add_trace(
            go.Scattergeo(
                lat = [None],
                lon = [None],
                mode = "markers",
                marker = dict(
                    color = [values.min(), values.max()],
                    colorscale = colorscale,
                    cmin = values.min(),
                    cmax = values.max(),
                    showscale = True,
                    colorbar = dict(
                        title = dict(text = title, side = "top", font = dict(size = 10)),
                        orientation = "h",
                        x = colorbar_x,
                        y = colorbar_y,
                        xanchor = "center",
                        len = length,          
                        thickness = 5,
                        outlinecolor = TRANSPARENT,
                        ticks = "",
                        tickvals = [values.min(), values.max()],
                        ticktext = [low_label, high_label],
                        tickfont = dict(size=8),
                        bgcolor = TRANSPARENT,
                    ),
                ),
                showlegend = False,
                hoverinfo = "skip",
            )
        )
    
    # ---- access + render ----
    @property
    def figure(self) -> go.Figure:
        """Return the base map figure."""
        return self.base_map

    def show(self, renderer: str = "png") -> "BrazilMap":
        """Render the base map figure."""
        self.base_map.show(renderer=renderer)
        return self
    



        