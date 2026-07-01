import pandas as pd
import streamlit as st
import data.products_db as products_db
from data.products_schema import PRODUCTS
from business.models import compute_bucketed_column

from streamlit_crud import draw_add_form
from streamlit_crud import draw_edit_form
from streamlit_crud import draw_grid, DEFAULT_STATUS_STYLES
from ui.import_forms import draw_import_form


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
    
    #df = compute_status(products_db.load_data())   # ← metrics also use derived Status
    df = compute_bucketed_column(
            products_db.load_data(),
            source_col="quantity",
            bins=[-1, 0, 10, float("inf")],
            labels=["Out of Stock", "Low Stock", "In Stock"],
            output_col="status"
    )
    
    draw_metrics(df)

    draw_action_buttons()

    draw_grid(df, PRODUCTS, badge_column="status", badge_styles=DEFAULT_STATUS_STYLES)

    if st.session_state.get("adding_row"):
        draw_add_form(
            schema=PRODUCTS,
            add_row=products_db.add_row,
            clear_cache=products_db.load_data.clear,
            title="Add Product",
        )       

    if st.session_state.get("editing_row") is not None:
        draw_edit_form(
            schema=PRODUCTS,
            update_row=products_db.update_row,
            delete_row=products_db.delete_row,
            clear_cache=products_db.load_data.clear,
            existing_row=st.session_state.editing_row,
            title="Edit Product",
        )

    
    if st.session_state.get("importing"):      
        draw_import_form()