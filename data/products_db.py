import pandas as pd
import streamlit as st
from data.products_schema import PRODUCTS
from streamlit_crud import database as db
from constants import DB_PATH


DB_PATH = "inventory.sqlite"

@st.cache_data
def load_data() -> pd.DataFrame:
    return db.load_data(PRODUCTS, DB_PATH)

def add_row(row: dict) -> None:
    db.add_row(PRODUCTS, DB_PATH, row)

def add_bulk(df: pd.DataFrame) -> None:
    db.add_bulk(PRODUCTS, DB_PATH, df)

def update_row(row: dict) -> None:
    db.update_row(PRODUCTS, DB_PATH, row)

def delete_row(pk_value: int) -> None:
    db.delete_row(PRODUCTS, DB_PATH, pk_value)
