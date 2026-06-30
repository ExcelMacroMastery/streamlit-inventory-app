import pandas as pd

def compute_bucketed_column(
    df: pd.DataFrame,
    source_col: str,
    bins: list[float],
    labels: list[str],
    output_col: str = "status",
) -> pd.DataFrame:
    """Derive a categorical column from a numeric column using bin thresholds.

    Example (original quantity → status use case):
        compute_bucketed_column(
            df,
            source_col="quantity",
            bins=[-1, 0, 10, float("inf")],
            labels=["Out of Stock", "Low Stock", "In Stock"],
            output_col="status",
        )
    """
    df = df.copy()
    df[output_col] = pd.cut(
        df[source_col],
        bins=bins,
        labels=labels,
    ).astype(str)
    return df

def to_float(x):
    if isinstance(x, (int, float)):
        return float(x)
    return float(str(x).replace("$", "").replace(",", ""))