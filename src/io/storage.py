from pathlib import Path
import numpy as np
import pandas as pd
import geopandas as gpd
from joblib import Memory

cache_dir ="data/cache"
memory = Memory(cache_dir, verbose=0)

def _validate_basename(basename: str) -> None:
    """Validate that the name is a valid basename (no slashes)."""
    if "/" in basename or "\\" in basename:
        raise ValueError(f"Invalid characters in file name: {basename!r}")

def _format_extension(ext: str) -> str:
    """Ensure the extension always starts with a single dot."""
    return f".{ext.lstrip('.')}"

def _get_clean_basename(basename: str, safe_ext: str) -> str:
    """Strip the target extension if already present; leave other dots alone."""
    if basename.endswith(safe_ext):
        return basename[: -len(safe_ext)]
    return basename

def create_file_name(basename: str, ext: str) -> str:
    """Create a file name with the given extension."""
    _validate_basename(basename)
    safe_ext = _format_extension(ext)
    clean_basename = _get_clean_basename(basename, safe_ext)
    return f"{clean_basename}{safe_ext}"

def create_file_path(basename: str, ext: str, out_dir: str | Path = "data/artifacts") -> Path:
    """Creates the file path for a given name and extension."""
    file_name = create_file_name(basename, ext)
    file_path = Path(out_dir) / file_name
    return file_path

def _ensure_dir_exists(file_path: Path) -> None:
    """Ensure that the output directory exists."""
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
def save_array(arr: np.ndarray, file_name: str, out_dir: str | Path = "data/artifacts") -> Path:
    """Save a numpy array to {out_dir}/{file_name}.npy. Returns the written path."""
    path = create_file_path(file_name, ".npy", out_dir)
    _ensure_dir_exists(path)
    np.save(path, arr)
    return path

def save_frame(df: pd.DataFrame, file_name: str, out_dir: str | Path = "data/artifacts") -> Path:
    """Save a pandas DataFrame to {out_dir}/{file_name}.parquet. Returns the written path."""
    path = create_file_path(file_name, ".parquet", out_dir)
    _ensure_dir_exists(path)
    df.to_parquet(path)
    return path

def save_geo_frame(gdf: gpd.GeoDataFrame, file_name: str, out_dir: str | Path = "data/artifacts") -> Path:
    """Save a GeoPandas GeoDataFrame to {out_dir}/{file_name}.parquet. Returns the written path."""
    path = create_file_path(file_name, ".parquet", out_dir)
    _ensure_dir_exists(path)
    gdf.to_parquet(path)
    return path
