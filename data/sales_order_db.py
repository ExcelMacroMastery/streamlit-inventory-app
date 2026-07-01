import pandas as pd
import streamlit as st
from data.sales_order_schema import SALES_ORDERS, SALES_ORDER_LINES
from streamlit_crud import database as db
#from constants import DB_PATH
from data.connection import get_connection

@st.cache_data
def load_orders_data() -> pd.DataFrame:
    with get_connection() as conn:
        return pd.read_sql_query("""
            SELECT 
                so.id,
                c.name as customer_name,
                so.subtotal,
                so.tax,
                so.total,
                so.created_at
            FROM sales_orders so
            JOIN customers c ON c.id = so.customer_id
            ORDER BY so.created_at DESC
        """, conn)

@st.cache_data
def load_order_lines(order_id: int) -> pd.DataFrame:
    with get_connection() as conn:
        return pd.read_sql_query(
            "SELECT * FROM sales_order_lines WHERE order_id = ?",
            conn, params=(order_id,)
        )

def save_order(customer_id: int, lines: list[dict], subtotal: float, tax: float, total: float) -> int:
    with get_connection() as conn:
        cursor = conn.execute(
            """INSERT INTO sales_orders (customer_id, subtotal, tax, total, created_at)
               VALUES (?, ?, ?, ?, datetime('now'))""",
            (customer_id, subtotal, tax, total)
        )
        order_id = cursor.lastrowid

        for line in lines:
            conn.execute(
                """INSERT INTO sales_order_lines (order_id, product_id, product_name, price, quantity, line_total)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (order_id, line["product_id"], line["product_name"], 
                 line["price"], line["quantity"], line["line_total"])
            )
            conn.execute(
                "UPDATE products SET quantity = quantity - ? WHERE id = ?",
                (line["quantity"], line["product_id"])
            )

        return order_id

def delete_order(order_id: int) -> None:
    with get_connection() as conn:
        conn.execute("DELETE FROM sales_order_lines WHERE order_id = ?", (order_id,))
        conn.execute("DELETE FROM sales_orders WHERE id = ?", (order_id,))
