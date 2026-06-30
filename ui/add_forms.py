import streamlit as st
from forms import draw_form
from data.schema import TableSchema, ValidationError


def close_add_form():
    st.session_state.adding_row = False
    st.session_state.grid_key += 1
    st.rerun()


@st.dialog("Add Item")
def draw_add_form(schema: TableSchema, db_module):
    row = draw_form(schema, {})

    save_col, cancel_col = st.columns(2)
    with save_col:
        if st.button("Add Item", type="primary", width="stretch", key="add_save"):
            try:
                schema.validate(row, exclude_pk=True)
                db_module.add_row(row)
                db_module.load_data.clear()
                close_add_form()
            except ValidationError as e:
                st.error("\n".join(e.errors))
            except Exception as e:
                st.error(f"Unexpected error: {e}")
    with cancel_col:
        if st.button("Cancel", width="stretch", key="add_cancel"):
            close_add_form()