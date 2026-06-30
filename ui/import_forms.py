import streamlit as st
import pandas as pd
import data.products_db as products_db
from data.products_schema import PRODUCTS
from business.models import compute_bucketed_column, to_float

# In dashboard.py

def close_import_form():
    st.session_state.importing = False
    st.session_state.grid_key += 1
    st.rerun()

def save_import(import_df: pd.DataFrame):
    required_cols = [c.name for c in PRODUCTS.columns if c.name != PRODUCTS.primary_key]
    products_db.add_bulk(import_df[required_cols])
    products_db.load_data.clear()
    close_import_form()

@st.dialog("Import CSV")
def draw_import_form():
    required_cols = [c.name for c in PRODUCTS.columns if c.name != PRODUCTS.primary_key]
    col_names = ", ".join(f"**{c}**" for c in required_cols)
    st.markdown(f"Upload a CSV file with columns: {col_names}")

    uploaded_file = st.file_uploader("Choose a CSV file", type="csv", key="csv_uploader")

    if uploaded_file is not None:
        try:
            import_df = pd.read_csv(uploaded_file)

            missing = set(required_cols) - set(import_df.columns)
            if missing:
                st.error(f"Missing required columns: {', '.join(missing)}")
                return

            # Coerce types using the schema
            for col in PRODUCTS.columns:
                if col.name not in import_df.columns:
                    continue
                if col.widget == "currency":
                    import_df[col.name] = import_df[col.name].apply(to_float)
                elif col.widget == "number":
                    import_df[col.name] = import_df[col.name].astype(int)

            #preview_df = compute_status(import_df[required_cols])
            preview_df = compute_bucketed_column(
                    products_db.load_data(),
                    source_col="quantity",
                    bins=[-1, 0, 10, float("inf")],
                    labels=["Out of Stock", "Low Stock", "In Stock"],
                    output_col="status"
            )

            st.dataframe(preview_df, width="stretch", hide_index=True)
            st.caption(f"{len(import_df)} row(s) ready to import")

            save_col, cancel_col = st.columns(2)
            with save_col:
                if st.button("Import", type="primary", width="stretch", key="import_save"):
                    try:
                        save_import(import_df)
                    except Exception as e:
                        st.error(f"Unexpected error: {e}")
            with cancel_col:
                if st.button("Cancel", width="stretch", key="import_cancel"):
                    close_import_form()

        except Exception as e:
            st.error(f"Failed to parse CSV: {e}")
    else:
        if st.button("Cancel", width="stretch", key="import_cancel_empty"):
            close_import_form()