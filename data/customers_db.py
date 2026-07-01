import pandas as pd
import streamlit as st
from data.customers_schema import CUSTOMERS
from constants import DB_PATH
from streamlit_crud import database as db

@st.cache_data
def load_data() -> pd.DataFrame:
    return db.load_data(CUSTOMERS, DB_PATH)

def add_row(row: dict) -> None:
    db.add_row(CUSTOMERS, DB_PATH, row)

def update_row(row: dict) -> None:
    db.update_row(CUSTOMERS, DB_PATH, row)

def delete_row(pk_value: int) -> None:
    db.delete_row(CUSTOMERS, DB_PATH, pk_value)
