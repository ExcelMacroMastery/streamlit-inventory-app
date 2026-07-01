import streamlit as st

from .schema import TableSchema
from .utils import to_float


def draw_form(schema: TableSchema, row: dict) -> dict:
    """Renders form fields from a schema and returns the current values.
    Used by both add and edit dialogs."""
    updated = {}
    col1, col2 = st.columns(2)
    cols = [c for c in schema.columns if c.widget != "hidden"]

    for i, col in enumerate(cols):
        with col1 if i % 2 == 0 else col2:
            if col.widget == "text":
                updated[col.name] = st.text_input(
                    col.label, value=row.get(col.name, col.default), key=f"form_{col.name}"
                )
            elif col.widget == "number":
                updated[col.name] = st.number_input(
                    col.label, value=int(row.get(col.name, col.default) or 0), step=1, key=f"form_{col.name}"
                )
            elif col.widget == "select":
                options = schema.categories.get(col.name, [])
                current = row.get(col.name, col.default)
                index = options.index(current) if current in options else 0
                updated[col.name] = st.selectbox(col.label, options, index=index, key=f"form_{col.name}")
            elif col.widget == "currency":
                price_input = st.text_input(
                    f"{col.label} ($)", value=str(row.get(col.name, col.default)), key=f"form_{col.name}"
                )
                try:
                    updated[col.name] = to_float(price_input)
                except ValueError:
                    st.error(f"Please enter a valid {col.label}")
                    updated[col.name] = col.default
    return updated
