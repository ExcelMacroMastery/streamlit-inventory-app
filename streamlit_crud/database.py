import sqlite3
from contextlib import contextmanager

import pandas as pd

from .schema import TableSchema


@contextmanager
def get_connection(db_path: str):
    conn = sqlite3.connect(db_path)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def _create_placeholders(count: int) -> str:
    return ", ".join("?" * count)


def load_data(schema: TableSchema, db_path: str) -> pd.DataFrame:
    with get_connection(db_path) as conn:
        return pd.read_sql_query(f"SELECT * FROM {schema.table}", conn)


def add_row(schema: TableSchema, db_path: str, row: dict) -> None:
    col_str = schema.col_names_commas(exclude_pk=True)
    values = schema.col_values(row, exclude_pk=True)
    placeholders = _create_placeholders(len(values))
    with get_connection(db_path) as conn:
        conn.execute(f"INSERT INTO {schema.table} ({col_str}) VALUES ({placeholders})", values)


def add_bulk(schema: TableSchema, db_path: str, df: pd.DataFrame) -> None:
    with get_connection(db_path) as conn:
        df.to_sql(schema.table, con=conn, if_exists="append", index=False)


def update_row(schema: TableSchema, db_path: str, row: dict) -> None:
    values = schema.col_values(row, exclude_pk=True)
    set_clause = schema.col_names_clause(exclude_pk=True)
    pk_value = row[schema.primary_key]
    with get_connection(db_path) as conn:
        conn.execute(
            f"UPDATE {schema.table} SET {set_clause} WHERE {schema.primary_key} = ?",
            (*values, pk_value),
        )


def delete_row(schema: TableSchema, db_path: str, pk_value) -> None:
    with get_connection(db_path) as conn:
        conn.execute(
            f"DELETE FROM {schema.table} WHERE {schema.primary_key} = ?",
            (pk_value,),
        )
