import streamlit as st
import data.products_db as products_db
from business.models import to_float
from data.schema import PRODUCTS, ValidationError

def draw_product_form(row: dict) -> dict:
    """Renders form fields and returns the current values. Used by both add and edit dialogs."""
    updated = {}
    col1, col2 = st.columns(2)
    cols = [c for c in PRODUCTS.columns if c.widget != "hidden"]

    for i, col in enumerate(cols):
        with col1 if i % 2 == 0 else col2:
            if col.widget == "text":
                updated[col.name] = st.text_input(col.name.title(), value=row.get(col.name, col.default), key=f"form_{col.name}")
            elif col.widget == "number":
                updated[col.name] = st.number_input(col.name.title(), value=int(row.get(col.name, col.default)), step=1, key=f"form_{col.name}")
            elif col.widget == "select":
                options = PRODUCTS.categories[col.name]
                current = row.get(col.name, col.default)
                updated[col.name] = st.selectbox(col.name.title(), options, index=options.index(current), key=f"form_{col.name}")
            elif col.widget == "currency":
                price_input = st.text_input(f"{col.name.title()} ($)", value=str(row.get(col.name, col.default)), key=f"form_{col.name}")
                try:
                    updated[col.name] = to_float(price_input)
                except ValueError:
                    st.error(f"Please enter a valid {col.name}")
                    updated[col.name] = col.default
    return updated

def draw_add_form():
    # Wrap the entire layout in a form block
    with st.form(key="add_product_form", clear_on_submit=False):
        row = draw_product_form({})
        save_col, cancel_col = st.columns(2)
        
        with save_col:
            # st.form_submit_button prevents page resets during validation errors
            submit_clicked = st.form_submit_button("Add Item", type="primary", use_container_width=True)
            
        with cancel_col:
            cancel_clicked = st.form_submit_button("Cancel", use_container_width=True)

    # Handle Cancel Actions (Outside the form processing)
    if cancel_clicked:
        close_form_and_refresh()

    # Handle Submit/Validation Actions
    if submit_clicked:
        # Note: Ensure missing_col_values checks the actual 'row' if necessary
        missing = PRODUCTS.missing_col_values(exclude_pk=True) 
        
        if missing:
            st.error(f"**Required fields missing:** {', '.join(missing)}")
        else:
            products_db.add_products_row(row)
            products_db.load_products_data.clear() # Clear the cache
            st.success("Product added successfully!")
            close_form_and_refresh()


def close_form_and_refresh():
    """Helper to cleanly reset state and refresh the UI."""
    st.session_state.adding_product = False
    st.session_state.grid_key += 1
    st.rerun()

def close_add_form():
    st.session_state.adding_product = False
    st.session_state.grid_key += 1
    st.rerun()

@st.dialog("Add Item")
def draw_add_form():
    row = draw_product_form({})

    save_col, cancel_col = st.columns(2)
    with save_col:
        if st.button("Add Item", type="primary", width="stretch", key="add_save"):
            try:
                PRODUCTS.validate(row, exclude_pk=True)
                products_db.add_products_row(row)
                products_db.load_products_data.clear()
                close_add_form()
            except ValidationError as e:
                st.error("\n".join(e.errors))
            except Exception as e:
                st.error(f"Unexpected error: {e}")
    with cancel_col:
        if st.button("Cancel", width="stretch", key="add_cancel"):
            close_add_form()

def close_edit_form():
    st.session_state.editing_row = None
    st.session_state.confirm_delete = False
    st.session_state.grid_key += 1
    st.rerun()

@st.dialog("Edit Item")
def draw_edit_form(existing_row: dict):
    row = draw_product_form(existing_row)

    save_col, cancel_col, delete_col = st.columns(3)
    with save_col:
        if st.button("Save Changes", type="primary", width="stretch", key="edit_save"):
            try:
                PRODUCTS.validate(row, exclude_pk=True)
                row[PRODUCTS.primary_key] = existing_row[PRODUCTS.primary_key]
                products_db.update_products_row(row)
                products_db.load_products_data.clear()
                close_edit_form()
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

    if st.session_state.get("confirm_delete"):
        st.warning(f"Delete **{existing_row['name']}**? This cannot be undone.")
        confirm_col, abort_col = st.columns(2)
        with confirm_col:
            if st.button("Yes, delete", type="primary", width="stretch", key="confirm_yes"):
                try:
                    products_db.delete_products_row(existing_row[PRODUCTS.primary_key])
                    products_db.load_products_data.clear()
                    close_edit_form()
                except Exception as e:
                    st.error(f"Unexpected error: {e}")
        with abort_col:
            if st.button("Cancel", width="stretch", key="confirm_no"):
                st.session_state.confirm_delete = False
                st.rerun()
