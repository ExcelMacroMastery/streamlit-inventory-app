import streamlit as st
from forms import draw_form
from data.schema import TableSchema, ValidationError


def close_edit_form():
    st.session_state.editing_row = None
    st.session_state.confirm_delete = False
    st.session_state.grid_key += 1
    st.rerun()


def save_row(schema: TableSchema, db_module, row: dict, existing_row: dict):
    schema.validate(row, exclude_pk=True)
    row[schema.primary_key] = existing_row[schema.primary_key]
    db_module.update_row(row)
    db_module.load_data.clear()
    close_edit_form()


def draw_edit_buttons(schema: TableSchema, db_module, row: dict, existing_row: dict):
    save_col, cancel_col, delete_col = st.columns(3)
    with save_col:
        if st.button("Save Changes", type="primary", width="stretch", key="edit_save"):
            try:
                save_row(schema, db_module, row, existing_row)
            except ValidationError as e:
                st.error("\n".join(e.errors))
            except Exception as e:
                st.error(f"Unexpected error: {e}")
    with cancel_col:
        if st.button("Cancel", width="stretch", key="edit_cancel"):
            close_edit_form()
    with delete_col:
        if st.button("🗑️ Delete", width="stretch", key="edit_delete"):
            st.session_state.confirm_delete = True


def draw_delete_confirmation(schema: TableSchema, db_module, existing_row: dict):
    if st.session_state.get("confirm_delete"):
        st.warning(f"Delete **{existing_row.get('name', existing_row[schema.primary_key])}**? This cannot be undone.")
        confirm_col, abort_col = st.columns(2)
        with confirm_col:
            if st.button("Yes, delete", type="primary", width="stretch", key="confirm_yes"):
                try:
                    db_module.delete_row(existing_row[schema.primary_key])
                    db_module.load_data.clear()
                    close_edit_form()
                except Exception as e:
                    st.error(f"Unexpected error: {e}")
        with abort_col:
            if st.button("Cancel", width="stretch", key="confirm_no"):
                st.session_state.confirm_delete = False
                st.rerun()


@st.dialog("Edit Item")
def draw_edit_form(schema: TableSchema, db_module, existing_row: dict):
    row = draw_form(schema, existing_row)

    draw_edit_buttons(schema, db_module, row, existing_row)

    if st.session_state.get("confirm_delete"):
        draw_delete_confirmation(schema, db_module, existing_row)