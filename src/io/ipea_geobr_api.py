import io
from pathlib import Path
import geopandas as gpd
import requests
from src.utils.geometry import standardize_geometry
from src.io.storage import save_geo_frame

RELEASE_URL = "https://api.github.com/repos/ipea/geobr_prep_data/releases/tags/v2.0.0"

def _matches_tags_flexibly(filename: str, tags: list[str]) -> bool:
    """Check if the filename contains all specified tags (case-insensitive)."""
    filename_lower = filename.lower()
    return all(tag.lower() in filename_lower for tag in tags)

def _find_matching_assets(tags: list[str]) -> list[dict]:
    """Return all release assets whose names contain every tag."""
    response = requests.get(RELEASE_URL, timeout=30)
    response.raise_for_status()
    assets = response.json().get("assets", [])
    matches = [a for a in assets if _matches_tags_flexibly(a["name"], tags)]
    if not matches:
        raise ValueError(f"No assets found matching all tags: {tags}")
    return matches

def _fetch_one_asset(tags: list[str], out_dir: str | Path) -> Path:
    """Download exactly one matching asset. Raises if zero or multiple match."""
    matches = _find_matching_assets(tags)   # already raises on zero
    if len(matches) > 1:
        names = [a["name"] for a in matches]
        raise ValueError(f"Tags {tags} are ambiguous, matched: {names}")
    asset = matches[0]
    resp = requests.get(asset["browser_download_url"], timeout=300)
    resp.raise_for_status()
    gdf = gpd.read_parquet(io.BytesIO(resp.content))
    return save_geo_frame(gdf, f"br_{Path(asset['name']).stem}", out_dir)

def fetch_country_outline(year: int = 2018, out_dir: str | Path = "data/external") -> Path:
    """Download Brazil's national outline (simplified borders)."""
    return _fetch_one_asset(["country", str(year), "simplified"], out_dir)

def fetch_states(year: int = 2018, out_dir: str | Path = "data/external") -> Path:
    """Download Brazilian state boundaries (simplified borders)."""
    return _fetch_one_asset(["state", str(year), "simplified"], out_dir)

def fetch_municipalities(year: int = 2018, out_dir: str | Path = "data/external",
                        simplified: bool = True) -> Path:
    """Download Brazilian municipality boundaries."""
    tags = ["municipalities", str(year)]
    if simplified:
        tags.append("simplified")
    return _fetch_one_asset(tags, out_dir)

_FETCHERS = {
    "country": fetch_country_outline,
    "states": fetch_states,
    "municipalities": fetch_municipalities,
}

def load_geo(area: str, year: int = 2018, out_dir: str | Path = "data/external") -> gpd.GeoDataFrame:
    """Load boundary geometries (EPSG:4326, CCW — see standardize_geometry), fetching on first use."""
    if area not in _FETCHERS:
        raise ValueError(f"Unknown area {area!r}. Expected one of: {sorted(_FETCHERS)}")
    path = Path(out_dir) / f"br_{area}_{year}_simplified.parquet"
    if not path.exists():
        return gpd.read_parquet(_FETCHERS[area](year, out_dir))
    return standardize_geometry(gpd.read_parquet(path))