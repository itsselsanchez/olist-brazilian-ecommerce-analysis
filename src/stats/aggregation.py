import numpy as np
import pandas as pd

def binned_aggregate(
    df: pd.DataFrame,
    bin_col: str,
    value_col: str,
    agg: str = "median",
    width: int = 200,
    min_n: int = 20,
) -> pd.DataFrame:
    """
    Bucket rows by bin_col into fixed-width bins and aggregate value_col within each bucket.
    """
    bins = np.arange(0, df[bin_col].max() + width, width)
    binned = (
        df.assign(_bin = pd.cut(df[bin_col], bins = bins))
        .groupby("_bin", observed = True)
        .agg(value = (value_col, agg), n = ("order_id", "size"))
        .reset_index()
    )
    binned["bin_mid"] = binned["_bin"].apply(lambda b: b.mid)
    return binned[binned["n"] >= min_n]


def monthly_aggregate(
    df: pd.DataFrame,
    date_col: str,
    value_col: str,
    agg: str = "mean",
) -> pd.DataFrame:
    """
    Aggregate value_col by calendar month of date_col.
    """
    return (
        df.dropna(subset = [date_col, value_col])
        .assign(month = lambda d: d[date_col].dt.to_period("M").dt.to_timestamp())
        .groupby("month")
        .agg(value = (value_col, agg), n = (value_col, "size"))
        .reset_index()
    )
