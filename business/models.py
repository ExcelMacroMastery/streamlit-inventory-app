import pandas as pd

def compute_status(df: pd.DataFrame) -> pd.DataFrame:
    """Derive Status from Quantity. Thresholds: 0 = Out of Stock, 1-10 = Low Stock, 11+ = In Stock."""
    df = df.copy()
    df["status"] = pd.cut(
        df["quantity"],
        bins=[-1, 0, 10, float("inf")],
        labels=["Out of Stock", "Low Stock", "In Stock"]
    ).astype(str)
    return df

def to_float(x):
    if isinstance(x, (int, float)):
        return float(x)
    return float(str(x).replace("$", "").replace(",", ""))