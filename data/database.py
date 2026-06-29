import pandas as pd
import streamlit as st
from data.schema import TableSchema
from data.connection import get_connection

def load_data(schema: TableSchema) -> pd.DataFrame:
    with get_connection() as conn:
        return pd.read_sql_query(f"SELECT * FROM {schema.table}", conn)

def create_placeholders(count: int) -> str:
    return ", ".join("?" * count)

def add_row(schema: TableSchema, row: dict) -> None:
    col_str = schema.col_names_commas(exclude_pk=True)
    values = schema.col_values(row, exclude_pk=True)
    placeholders = create_placeholders(len(values))
    with get_connection() as conn:
        conn.execute(f"INSERT INTO {schema.table} ({col_str}) VALUES ({placeholders})", values)

def add_bulk(schema: TableSchema, df: pd.DataFrame) -> None:
    try:
        with get_connection() as conn:
            df.to_sql(schema.table, con=conn, if_exists="append", index=False)
    except Exception as e:
        print(f"Error is: {e}")

def update_row(schema: TableSchema, row: dict) -> None:
    values = schema.col_values(row, exclude_pk=True)
    set_clause = schema.col_names_clause(exclude_pk=True)
    pk_value = row[schema.primary_key]
    with get_connection() as conn:
        conn.execute(
            f"UPDATE {schema.table} SET {set_clause} WHERE {schema.primary_key} = ?",
            (*values, pk_value)
        )

def delete_row(schema: TableSchema, pk_value: int) -> None:
    with get_connection() as conn:
        conn.execute(
            f"DELETE FROM {schema.table} WHERE {schema.primary_key} = ?",
            (pk_value,)
        )