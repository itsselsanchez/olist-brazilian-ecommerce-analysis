from src.config.brazil_map_template import MAP_CRS
import geopandas as gpd
import shapely
import numpy as np


def to_project_crs(gdf):
    """Convert to the project's coordinate system."""
    return gdf.to_crs(MAP_CRS)

def make_clockwise(gdf):
    """Rewrite polygons so their points run counterclockwise."""
    oriented = shapely.orient_polygons(gdf.geometry.values, exterior_cw=True)
    return gdf.assign(geometry=gpd.GeoSeries(oriented, index=gdf.index, crs=gdf.crs))

def standardize_geometry(gdf):
    """Apply both project geometry rules: project CRS + counterclockwise polygons."""
    return make_clockwise(to_project_crs(gdf))

def bezier_arc(lat0, lon0, lat1, lon1, height=0.2, n=50):
    dx, dy = lon1 - lon0, lat1 - lat0
    ctrl_lat = (lat0 + lat1) / 2 - dx * height
    ctrl_lon = (lon0 + lon1) / 2 + dy * height
    t = np.linspace(0, 1, n)
    lats = (1-t)**2 * lat0 + 2*(1-t)*t * ctrl_lat + t**2 * lat1
    lons = (1-t)**2 * lon0 + 2*(1-t)*t * ctrl_lon + t**2 * lon1
    return lats, lons