from typing import Callable

import streamlit as st

from .forms import draw_form
from .schema import TableSchema, ValidationError


def close_add_form(flag_key: str = "adding_row", grid_key: str = "grid_key"):
    st.session_state[flag_key] = False
    st.session_state[grid_key] = st.session_state.get(grid_key, 0) + 1
    st.rerun()


def draw_add_form_body(
    schema: TableSchema,
    add_row: Callable[[dict], None],
    clear_cache: Callable[[], None],
    flag_key: str = "adding_row",
    grid_key: str = "grid_key",
):
    """Renders the add-item form body. Wrap this in your own @st.dialog so the
    dialog title can be customized per-table (e.g. 'Add Product', 'Add Customer')."""
    row = draw_form(schema, {})

    save_col, cancel_col = st.columns(2)
    with save_col:
        if st.button("Add Item", type="primary", width="stretch", key="add_save"):
            try:
                schema.validate(row, exclude_pk=True)
                add_row(row)
                clear_cache()
                close_add_form(flag_key, grid_key)
            except ValidationError as e:
                st.error("\n".join(e.errors))
            except Exception as e:
                st.error(f"Unexpected error: {e}")
    with cancel_col:
        if st.button("Cancel", width="stretch", key="add_cancel"):
            close_add_form(flag_key, grid_key)


def draw_add_form(
    schema: TableSchema,
    add_row: Callable[[dict], None],
    clear_cache: Callable[[], None],
    title: str = "Add Item",
    flag_key: str = "adding_row",
    grid_key: str = "grid_key",
):
    """Convenience wrapper with a fixed dialog title. For a custom title per
    table, use draw_add_form_body inside your own @st.dialog instead."""

    @st.dialog(title)
    def _dialog():
        draw_add_form_body(schema, add_row, clear_cache, flag_key, grid_key)

    _dialog()
