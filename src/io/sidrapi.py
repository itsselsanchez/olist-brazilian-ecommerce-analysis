import sidrapy
from pathlib import Path
import pandas as pd
from src.io.storage import save_frame

def load_population_table(
    period: str,
    table_code: str = "6579",
    territorial_level: str = "6",
    ibge_territorial_code: str = "all",
    out_dir: str | Path = "data/external",
) -> pd.DataFrame:
    """Population by municipality for a specific year. Saved as a parquet."""
    
    path = Path(out_dir) / f"br_population_{period}.parquet"
    if path.exists():
        return pd.read_parquet(path)

    frame = sidrapy.get_table(
        table_code=table_code,
        territorial_level=territorial_level,
        ibge_territorial_code=ibge_territorial_code,
        period=period,
    )
    save_frame(frame, file_name=f"br_population_{period}", out_dir=out_dir)
    return frame