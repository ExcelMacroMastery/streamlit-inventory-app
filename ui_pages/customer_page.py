import pandas as pd
import streamlit as st
import data.suppliers_db as suppliers_db
from data.customers_schema import CUSTOMERS
from business.models import compute_bucketed_column
from streamlit_crud import draw_add_form 
from streamlit_crud import draw_edit_form
from streamlit_crud import draw_grid, DEFAULT_STATUS_STYLES


def draw_action_buttons():    
    btn_col1, _ = st.columns([1, 1])
    with btn_col1:
        if st.button("➕ Add Item", type="primary"):
            st.session_state.adding_row = True

def render():
    st.header("Customers")
    
    df = suppliers_db.load_data()

    draw_action_buttons()

    draw_grid(df, CUSTOMERS, badge_styles=DEFAULT_STATUS_STYLES)

    if st.session_state.get("adding_row"):
        draw_add_form(
            schema=CUSTOMERS,
            add_row=suppliers_db.add_row,
            clear_cache=suppliers_db.load_data.clear,
            title="Add Product",
        )          

    if st.session_state.get("editing_row") is not None:
        draw_edit_form(
            schema=CUSTOMERS,
            update_row=suppliers_db.update_row,
            delete_row=suppliers_db.delete_row,
            clear_cache=suppliers_db.load_data.clear,
            existing_row=st.session_state.editing_row,
            title="Edit Customer",
        )    
 