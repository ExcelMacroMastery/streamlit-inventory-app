import pandas as pd


def to_float(value) -> float:
    """Parse a currency-style string (handles $, commas) into a float."""
    if isinstance(value, (int, float)):
        return float(value)
    cleaned = str(value).replace("$", "").replace(",", "").strip()
    if cleaned == "":
        raise ValueError("Empty value")
    return float(cleaned)


def compute_bucketed_column(
    df: pd.DataFrame,
    source_col: str,
    bins: list[float],
    labels: list[str],
    output_col: str = "status",
) -> pd.DataFrame:
    """Derive a categorical column from a numeric column using bin thresholds.

    Example:
        compute_bucketed_column(
            df,
            source_col="quantity",
            bins=[-1, 0, 10, float("inf")],
            labels=["Out of Stock", "Low Stock", "In Stock"],
            output_col="status",
        )
    """
    df = df.copy()
    df[output_col] = pd.cut(df[source_col], bins=bins, labels=labels).astype(str)
    return df
