from pathlib import Path

# Project root directory
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Data directories
RAW_DATA = PROJECT_ROOT / "data" / "raw"
REFERENCE_DATA = PROJECT_ROOT / "data" / "reference"
PROCESSED_DATA = PROJECT_ROOT / "data" / "processed"
EXTERNAL_DATA = PROJECT_ROOT / "data" / "external"
