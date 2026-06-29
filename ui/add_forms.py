import streamlit as st
import data.products_db as products_db
from forms import draw_form
from data.products_schema import PRODUCTS
from data.schema import ValidationError

def close_add_form():
    st.session_state.adding_product = False
    st.session_state.grid_key += 1
    st.rerun()

@st.dialog("Add Item")
def draw_add_form():
    row = draw_form(PRODUCTS,{})

    save_col, cancel_col = st.columns(2)
    with save_col:
        if st.button("Add Item", type="primary", width="stretch", key="add_save"):
            try:
                PRODUCTS.validate(row, exclude_pk=True)
                products_db.add_products_row(row)
                products_db.load_products_data.clear()
                close_add_form()
            except ValidationError as e:
                st.error("\n".join(e.errors))
            except Exception as e:
                st.error(f"Unexpected error: {e}")
    with cancel_col:
        if st.button("Cancel", width="stretch", key="add_cancel"):
            close_add_form()
