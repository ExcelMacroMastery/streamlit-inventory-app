import pandas as pd
import streamlit as st
from data.customers_schema import CUSTOMERS
import data.database as db

@st.cache_data
def load_data() -> pd.DataFrame:
    return db.load_data(CUSTOMERS)

def add_row(row: dict) -> None:
    db.add_row(CUSTOMERS, row)

def update_row(row: dict) -> None:
    db.update_row(CUSTOMERS, row)

def delete_row(pk_value: int) -> None:
    db.delete_row(CUSTOMERS, pk_value)
