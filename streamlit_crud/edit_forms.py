from typing import Callable

import streamlit as st

from .forms import draw_form
from .schema import TableSchema, ValidationError


def close_edit_form(
    editing_key: str = "editing_row",
    confirm_key: str = "confirm_delete",
    grid_key: str = "grid_key",
):
    st.session_state[editing_key] = None
    st.session_state[confirm_key] = False
    st.session_state[grid_key] = st.session_state.get(grid_key, 0) + 1
    st.rerun()


def save_row(
    schema: TableSchema,
    update_row: Callable[[dict], None],
    clear_cache: Callable[[], None],
    row: dict,
    existing_row: dict,
    editing_key: str = "editing_row",
    confirm_key: str = "confirm_delete",
    grid_key: str = "grid_key",
):
    schema.validate(row, exclude_pk=True)
    row[schema.primary_key] = existing_row[schema.primary_key]
    update_row(row)
    clear_cache()
    close_edit_form(editing_key, confirm_key, grid_key)


def draw_edit_buttons(
    schema: TableSchema,
    update_row: Callable[[dict], None],
    clear_cache: Callable[[], None],
    row: dict,
    existing_row: dict,
    editing_key: str = "editing_row",
    confirm_key: str = "confirm_delete",
    grid_key: str = "grid_key",
):
    save_col, cancel_col, delete_col = st.columns(3)
    with save_col:
        if st.button("Save Changes", type="primary", width="stretch", key="edit_save"):
            try:
                save_row(schema, update_row, clear_cache, row, existing_row, editing_key, confirm_key, grid_key)
            except ValidationError as e:
                st.error("\n".join(e.errors))
            except Exception as e:
                st.error(f"Unexpected error: {e}")
    with cancel_col:
        if st.button("Cancel", width="stretch", key="edit_cancel"):
            close_edit_form(editing_key, confirm_key, grid_key)
    with delete_col:
        if st.button("🗑️ Delete", width="stretch", key="edit_delete"):
            st.session_state[confirm_key] = True


def draw_delete_confirmation(
    schema: TableSchema,
    delete_row: Callable[[object], None],
    clear_cache: Callable[[], None],
    existing_row: dict,
    confirm_key: str = "confirm_delete",
    editing_key: str = "editing_row",
    grid_key: str = "grid_key",
    display_field: str = "name",
):
    if st.session_state.get(confirm_key):
        label = existing_row.get(display_field, existing_row[schema.primary_key])
        st.warning(f"Delete **{label}**? This cannot be undone.")
        confirm_col, abort_col = st.columns(2)
        with confirm_col:
            if st.button("Yes, delete", type="primary", width="stretch", key="confirm_yes"):
                try:
                    delete_row(existing_row[schema.primary_key])
                    clear_cache()
                    close_edit_form(editing_key, confirm_key, grid_key)
                except Exception as e:
                    st.error(f"Unexpected error: {e}")
        with abort_col:
            if st.button("Cancel", width="stretch", key="confirm_no"):
                st.session_state[confirm_key] = False
                st.rerun()


def draw_edit_form_body(
    schema: TableSchema,
    update_row: Callable[[dict], None],
    delete_row: Callable[[object], None],
    clear_cache: Callable[[], None],
    existing_row: dict,
    confirm_key: str = "confirm_delete",
    editing_key: str = "editing_row",
    grid_key: str = "grid_key",
    display_field: str = "name",
):
    """Renders the edit-item form body. Wrap this in your own @st.dialog so the
    dialog title can be customized per-table."""
    row = draw_form(schema, existing_row)

    draw_edit_buttons(schema, update_row, clear_cache, row, existing_row, editing_key, confirm_key, grid_key)

    if st.session_state.get(confirm_key):
        draw_delete_confirmation(
            schema, delete_row, clear_cache, existing_row, confirm_key, editing_key, grid_key, display_field
        )


def draw_edit_form(
    schema: TableSchema,
    update_row: Callable[[dict], None],
    delete_row: Callable[[object], None],
    clear_cache: Callable[[], None],
    existing_row: dict,
    title: str = "Edit Item",
    confirm_key: str = "confirm_delete",
    editing_key: str = "editing_row",
    grid_key: str = "grid_key",
    display_field: str = "name",
):
    """Convenience wrapper with a fixed dialog title. For a custom title per
    table, use draw_edit_form_body inside your own @st.dialog instead."""

    @st.dialog(title)
    def _dialog():
        draw_edit_form_body(
            schema, update_row, delete_row, clear_cache, existing_row,
            confirm_key, editing_key, grid_key, display_field,
        )

    _dialog()
