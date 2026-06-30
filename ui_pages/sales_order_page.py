import streamlit as st
import ui.sales_order_form as sales_order_form
import ui.sales_order_history as sales_order_history


def render():
    new_tab, history_tab = st.tabs(["New Order", "Order History"])
    with new_tab:
        sales_order_form.render()
    with history_tab:
        sales_order_history.render()