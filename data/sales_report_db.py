from data.connection import get_connection
import streamlit as st
import pandas as pd

@st.cache_data
def load_sales_by_day() -> pd.DataFrame:
    with get_connection() as conn:
        return pd.read_sql_query("""
            SELECT
                date(created_at) AS day,
                SUM(total) AS revenue
            FROM sales_orders
            GROUP BY day
            ORDER BY day
        """, conn)


@st.cache_data
def load_sales_by_category() -> pd.DataFrame:
    with get_connection() as conn:
        return pd.read_sql_query("""
            SELECT
                p.category,
                SUM(sol.line_total) AS revenue
            FROM sales_order_lines sol
            JOIN products p ON p.id = sol.product_id
            GROUP BY p.category
            ORDER BY revenue DESC
        """, conn)