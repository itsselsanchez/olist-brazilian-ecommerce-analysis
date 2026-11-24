import pandas as pd


def get_num_observations(df: pd.DataFrame) -> int:
    """Return the number of observations (rows) in the dataset."""
    return df.shape[0]

def get_num_features(df: pd.DataFrame) -> int:
    """Return the number of features (columns) in the dataset."""
    return df.shape[1]

def get_purchase_window(df: pd.DataFrame) -> tuple[pd.Timestamp, pd.Timestamp]:
    """Return the first and last purchase timestamps."""
    return (df["order_purchase_timestamp"].min(), df["order_purchase_timestamp"].max())
