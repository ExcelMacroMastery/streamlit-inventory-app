import pandas as pd
import streamlit as st
import data.customers_db as customers_db
from data.customers_schema import CUSTOMERS
from business.models import compute_bucketed_column
from ui.add_forms import draw_add_form
from ui.edit_forms import draw_edit_form
from ui.import_forms import draw_import_form
from ui.grid_builder import draw_grid, DEFAULT_STATUS_STYLES

def draw_action_buttons():    
    btn_col1, _ = st.columns([1, 1])
    with btn_col1:
        if st.button("➕ Add Item", type="primary"):
            st.session_state.adding_row = True

def render():
    st.header("Customers")
    
    df = customers_db.load_data()

    draw_action_buttons()

    draw_grid(df, CUSTOMERS, badge_styles=DEFAULT_STATUS_STYLES)

    if st.session_state.get("adding_row"):
        draw_add_form(CUSTOMERS, customers_db)

    if st.session_state.get("editing_row") is not None:
        draw_edit_form(CUSTOMERS, customers_db, st.session_state.editing_row)
    
    if st.session_state.get("importing"):      
        draw_import_form()