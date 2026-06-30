import streamlit as st
import data.products_db as products_db
from business.models import to_float
from data.products_schema import PRODUCTS
from data.schema import TableSchema
#from data.schema import ValidationError

#def draw_product_form(schema: TableSchema, row: dict) -> dict:
def draw_form(schema: TableSchema, row: dict) -> dict:
    """Renders form fields and returns the current values. Used by both add and edit dialogs."""
    updated = {}
    col1, col2 = st.columns(2)
    #cols = [c for c in PRODUCTS.columns if c.widget != "hidden"]
    cols = [c for c in schema.columns if c.widget != "hidden"]
    
    for i, col in enumerate(cols):
        with col1 if i % 2 == 0 else col2:
            if col.widget == "text":
                updated[col.name] = st.text_input(col.name.title(), value=row.get(col.name, col.default), key=f"form_{col.name}")
            elif col.widget == "number":
                updated[col.name] = st.number_input(col.name.title(), value=int(row.get(col.name, col.default)), step=1, key=f"form_{col.name}")
            elif col.widget == "select":
                options = schema.categories[col.name]
                current = row.get(col.name, col.default)
                updated[col.name] = st.selectbox(col.name.title(), options, index=options.index(current), key=f"form_{col.name}")
            elif col.widget == "currency":
                price_input = st.text_input(f"{col.name.title()} ($)", value=str(row.get(col.name, col.default)), key=f"form_{col.name}")
                try:
                    updated[col.name] = to_float(price_input)
                except ValueError:
                    st.error(f"Please enter a valid {col.name}")
                    updated[col.name] = col.default
    return updated


   






