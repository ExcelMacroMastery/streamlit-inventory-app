import pandas as pd
import streamlit as st
from data.products_schema import PRODUCTS
from data.database import get_connection

DB_PATH = "inventory.sqlite"
TABLE = "products"

@st.cache_data
def load_products_data() -> pd.DataFrame:
    with get_connection() as conn:
        return pd.read_sql_query(f"SELECT * FROM {PRODUCTS.table}", conn)

def create_placeholders(count: int) -> str:
    return ", ".join("?" * count) # creates (?, ?, ?, ?, ?)    

def add_products_row(row: dict) -> None:
    col_str = PRODUCTS.col_names_commas(exclude_pk=True)
    values = PRODUCTS.col_values(row, exclude_pk=True)
    placeholders = create_placeholders(len(values))
    with get_connection() as conn:
        conn.execute(f"INSERT INTO {PRODUCTS.table} ({col_str}) VALUES ({placeholders})", values)            

def add_products_bulk(df: pd.DataFrame) -> None:
    try:
        with get_connection() as conn:
            df.to_sql(TABLE, con=conn, if_exists="append", index=False)
    except Exception as inst:
        print(f"Error is: {inst}") 

def update_products_row(row: dict) -> None:
    values = PRODUCTS.col_values(row, exclude_pk=True)
    set_clause = ", ".join(f"{c} = ?" for c in PRODUCTS.col_names(exclude_pk=True))
    set_clause = PRODUCTS.col_names_clause(exclude_pk=True)
    pk_value = row[PRODUCTS.primary_key]

    with get_connection() as conn:
        conn.execute(
            f"UPDATE {PRODUCTS.table} SET {set_clause} WHERE {PRODUCTS.primary_key} = ?",
            (*values, pk_value)
        )


def delete_products_row(id: int) -> None:
    with get_connection() as conn:
        conn.execute(f"DELETE FROM {TABLE} WHERE id = ?", (id,))

""" def sku_exists(sku: str) -> bool:
    with get_connection() as conn:
        cursor = conn.execute("SELECT 1 FROM items WHERE sku = ?", (sku,))
        return cursor.fetchone() is not None """