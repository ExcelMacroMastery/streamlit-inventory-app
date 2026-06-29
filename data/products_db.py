import pandas as pd
import streamlit as st
from data.products_schema import PRODUCTS
import data.database as db

@st.cache_data
def load_products_data() -> pd.DataFrame:
    return db.load_data(PRODUCTS)

def add_products_row(row: dict) -> None:
    db.add_row(PRODUCTS, row)

def add_products_bulk(df: pd.DataFrame) -> None:
    db.add_bulk(PRODUCTS, df)

def update_products_row(row: dict) -> None:
    db.update_row(PRODUCTS, row)

def delete_products_row(pk_value: int) -> None:
    db.delete_row(PRODUCTS, pk_value)
