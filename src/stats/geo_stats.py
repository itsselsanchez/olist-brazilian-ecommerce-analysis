from scipy.stats import gaussian_kde
import numpy as np
import pandas as pd
from src.io.storage import memory

@memory.cache
def compute_concentration(lat: pd.Series,  lon: pd.Series) -> np.ndarray:     
    """Compute the relative concentration of geographic points using Gaussian KDE."""
    coords = np.vstack([lon, lat])
    return gaussian_kde(coords)(coords)