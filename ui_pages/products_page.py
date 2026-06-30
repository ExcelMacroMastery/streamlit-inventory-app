import pandas as pd
import streamlit as st
import data.products_db as products_db
#from constants import GridDefaults
from data.products_schema import PRODUCTS
#from data.schema import TableSchema
from business.models import compute_status
from ui.add_forms import draw_add_form
from ui.edit_forms import draw_edit_form
from ui.import_forms import draw_import_form
from ui.grid_builder import draw_grid
#from st_aggrid import GridOptionsBuilder, AgGrid, JsCode, GridUpdateMode, DataReturnMode


def draw_metrics(df: pd.DataFrame):

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total SKUs", len(df))
    c2.metric("Total Units in Stock", df["quantity"].sum())
    c3.metric("Low Stock Items", (df["status"] == "Low Stock").sum())
    c4.metric("Out of Stock", (df["status"] == "Out of Stock").sum())

    st.write("")
    total_value = (df["price"] * df["quantity"]).sum()
    st.metric("Estimated Inventory Value", f"${total_value:,.2f}")

def draw_action_buttons():    
    btn_col1, btn_col2, _ = st.columns([1, 1, 6])
    with btn_col1:
        if st.button("➕ Add Item", type="primary"):
            st.session_state.adding_row = True
    with btn_col2:
        if st.button("📥 Import CSV"):          
            st.session_state.importing = True

def render():
    st.header("Products")
    
    df = compute_status(products_db.load_data())   # ← metrics also use derived Status

    draw_metrics(df)

    draw_action_buttons()

    draw_grid(df, PRODUCTS)

    if st.session_state.get("adding_row"):
        draw_add_form(PRODUCTS, products_db)

    if st.session_state.get("importing"):      
        draw_import_form()

    if st.session_state.get("editing_row") is not None:
        draw_edit_form(PRODUCTS, products_db, st.session_state.editing_row)