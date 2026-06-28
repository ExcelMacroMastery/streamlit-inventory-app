import pandas as pd
import streamlit as st
import data.products_db as products_db
from business.models import compute_status

from st_aggrid import GridOptionsBuilder, AgGrid, JsCode, GridUpdateMode, DataReturnMode

custom_css = {
    ".ag-cell": {"font-size": "14px !important"},
    ".ag-header-cell-text": {"font-size": "14px !important", "font-weight": "600 !important"},
}

GRID_CONFIG = {
    "name":     {"label": "Name",     "width": 130},
    "sku":      {"label": "SKU",      "width": 100},
    "category": {"label": "Category", "width": 100},
    "quantity": {"label": "Quantity", "width": 65},
    "price":    {"label": "Price",    "width": 65, "format": "currency"},
}

def to_float(x):
    if isinstance(x, (int, float)):
        return float(x)
    return float(str(x).replace("$", "").replace(",", ""))



@st.dialog("Import CSV")
def draw_import_form():
    st.markdown("Upload a CSV file with columns: **name, sku, category, quantity, price**")

    if False:
        st.markdown("""
        <style>
            /* File uploader outer container */
            div[data-testid="stFileUploader"] {
                background-color: #f0f2f6 !important;
                padding: 10px;
                border-radius: 6px;
            }
                    
            /* Force hover color */
            div[data-testid="stFileUploader"] button:hover {
                background-color: #b5b9c0 !important;
                color: black !important;
            }                

            /* The drag-and-drop area */
            div[data-testid="stFileUploader"] section {
                background-color: #f0f2f6 !important;
                border-radius: 6px;
            }

            /* The "Browse files" button */
            div[data-testid="stFileUploader"] button {
                background-color: #d0d4db !important;
                color: black !important;
                border: none !important;
            }
        </style>
        """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv", key="csv_uploader")

    if uploaded_file is not None:
        try:
            import_df = pd.read_csv(uploaded_file)

            required_cols = ["name", "sku", "category", "quantity", "price"]
            missing = set(required_cols) - set(import_df.columns)
            if missing:
                st.error(f"Missing required columns: {', '.join(missing)}")
            else:
                import_df["price"] = import_df["price"].apply(to_float)
                import_df["quantity"] = import_df["quantity"].astype(int)
                preview_df = compute_status(import_df[list(required_cols)])
                st.dataframe(preview_df, use_container_width=True, hide_index=True)
                st.caption(f"{len(import_df)} row(s) ready to import")

                save_col, cancel_col = st.columns(2)
                with save_col:
                    if st.button("Import", type="primary", use_container_width=True, key="import_save"):
                        products_db.add_products_bulk(import_df[required_cols])
                        products_db.load_products_data.clear()
                        st.session_state.importing = False
                        st.session_state.grid_key += 1
                        st.success(f"Imported {len(import_df)} item(s)!")
                        st.rerun()
                with cancel_col:
                    if st.button("Cancel", use_container_width=True, key="import_cancel"):
                        st.session_state.importing = False
                        st.session_state.grid_key += 1
                        st.rerun()
        except Exception as e:
            st.error(f"Failed to parse CSV: {e}")
    else:
        if st.button("Cancel", use_container_width=True, key="import_cancel_empty"):
            st.session_state.importing = False
            st.session_state.grid_key += 1
            st.rerun()

@st.dialog("Add Item")
def draw_add_form():
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Name", key="add_products_name")
        sku = st.text_input("SKU", key="add_sku")
        categories = ["Apparel", "Electronics", "Furniture", "Groceries", "Home"]
        category = st.selectbox("Category", categories, key="add_category")
    with col2:
        quantity = st.number_input("Quantity", value=0, step=1, key="add_quantity")
        price_input = st.text_input("Price ($)", value="0.00", key="add_price")
        try:
            price = to_float(price_input)
        except ValueError:
            st.error("Please enter a valid price")
            price = 0.0

    save_col, cancel_col = st.columns(2)
    with save_col:
        if st.button("Add Item", type="primary", use_container_width=True, key="add_save"):
            if not name or not sku:
                st.error("name and SKU are required.")
            else:
                new_row = {
                    "name": name,
                    "sku": sku,
                    "category": category,
                    "quantity": quantity,
                    "price": price,
                }
                products_db.add_products_row(new_row)
                products_db.load_products_data.clear()
                st.session_state.grid_key += 1
                st.rerun()
    with cancel_col:
        if st.button("Cancel", use_container_width=True, key="add_cancel"):
            st.session_state.adding_product = False  
            st.session_state.grid_key += 1
            st.rerun()

@st.dialog("Edit Item")
def draw_edit_form(row):
    with st.container(border=True):
        st.subheader("Edit Item")

        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("name", value=row["name"], key="edit_products_name")
            sku = st.text_input("sku", value=row["sku"], key="edit_sku")

            categories = ["Apparel", "Electronics", "Furniture", "Groceries", "Home"]
            category = st.selectbox(
                "Category",
                categories,
                index=categories.index(row["category"]),
                key="edit_category"
            )
        with col2:
            quantity = st.number_input("Quantity", value=int(row["quantity"]), step=1, key="edit_quantity")
            price_input = st.text_input("Price ($)", value=str(to_float(row["price"])), key="edit_price")
            try:
                price = to_float(price_input)
            except ValueError:
                st.error("Please enter a valid price")
                price = to_float(row["price"])

        save_col, cancel_col, delete_col = st.columns(3)

        with save_col:
            if st.button("Save Changes", type="primary", use_container_width=True, key="edit_save"):
                df = products_db.load_products_data()
                df.loc[df["sku"] == sku, ["name", "category", "quantity", "price"]] = [
                    name, category, quantity, price
                ]
                row = df[df["sku"] == sku].iloc[0]
                products_db.update_products_row(row)
                products_db.load_products_data.clear()
                st.session_state.editing_row = None
                st.session_state.grid_key += 1
                st.rerun()

        with cancel_col:
            if st.button("Cancel", use_container_width=True, key="edit_cancel"):
                st.session_state.editing_row = None
                st.session_state.grid_key += 1
                st.rerun()
        
        with delete_col:
            if st.button("🗑️ Delete", use_container_width=True, key="edit_delete"):
                st.session_state.confirm_delete = True

        if st.session_state.get("confirm_delete"):
            st.warning(f"Delete **{row['name']}**? This cannot be undone.")
            confirm_col, abort_col = st.columns(2)
            with confirm_col:
                if st.button("Yes, delete", type="primary", use_container_width=True, key="confirm_yes"):
                    products_db.delete_products_row(row["sku"])
                    products_db.load_products_data.clear()
                    st.session_state.editing_row = None
                    st.session_state.confirm_delete = False
                    st.session_state.grid_key += 1
                    st.rerun()
            with abort_col:
                if st.button("Cancel", use_container_width=True, key="confirm_no"):
                    st.session_state.confirm_delete = False
                    st.rerun()

def draw_grid(df: pd.DataFrame):
    #df = compute_status(db.load_products_data())   # ← Status derived here

    grid_builder = GridOptionsBuilder.from_dataframe(df)
    grid_builder.configure_grid_options(
        rowHeight=40,
        headerHeight=44,
    )
    grid_builder.configure_selection(
        selection_mode="single",
        use_checkbox=False
    )
    grid_builder.configure_default_column(
        filter=True,
        filterParams={"buttons": ["reset"]},
    )
    grid_builder.configure_column("name", width=130)
    grid_builder.configure_column("sku", width=100)
    grid_builder.configure_column("Category", width=100)
    grid_builder.configure_column("Quantity", width=65)
    grid_builder.configure_column(
        "Price",
        width=65,
        type=["numericColumn"],
        valueFormatter="data.Price.toLocaleString('en-US', {style: 'currency', currency: 'USD'})",
    )

    cell_renderer_status = JsCode("""
    class StatusRenderer {
        init(params) {
            const value = params.value;
            const styles = {
                'In Stock':     { bg: '#e6f9f0', color: '#27ae60', border: '#a8e6c8' },
                'Low Stock':    { bg: '#fff8e6', color: '#f39c12', border: '#ffd980' },
                'Out of Stock': { bg: '#fdecea', color: '#e74c3c', border: '#f5c6c2' },
            };
            const style = styles[value] || { bg: '#f0f0f0', color: '#888', border: '#ccc' };
            this.eGui = document.createElement('span');
            this.eGui.innerHTML = value;
            this.eGui.style.cssText = `
                display: inline-block;
                padding: 3px 12px;
                border-radius: 12px;
                font-size: 13px;
                font-weight: 500;
                background-color: ${style.bg};
                color: ${style.color};
                border: 1px solid ${style.border};
            `;
        }
        getGui() { return this.eGui; }
    }
    """)

    grid_builder.configure_column(
        "Status",
        cellRenderer=cell_renderer_status,
        width=90,
        cellStyle={"display": "flex", "alignItems": "center", "justifyContent": "center", "paddingTop": "4px"},
    )

    grid_options = grid_builder.build()
    grid_response = AgGrid(
        data=df,
        gridOptions=grid_options,
        key=f"grid_{st.session_state.grid_key}",
        allow_unsafe_jscode=True,
        update_mode=GridUpdateMode.SELECTION_CHANGED,
        custom_css=custom_css,
    )

    if grid_response["selected_rows"] is not None and st.session_state.editing_row is None:
        row_id = int(grid_response.selected_rows_id[0])
        selected = grid_response["data"].iloc[row_id]
        st.session_state.editing_row = selected
        st.rerun()


def draw_metrics(df: pd.DataFrame):
    #df = compute_status(db.load_products_data())   # ← metrics also use derived Status

    st.header("Dashboard")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total SKUs", len(df))
    c2.metric("Total Units in Stock", df["quantity"].sum())
    c3.metric("Low Stock Items", (df["status"] == "Low Stock").sum())
    c4.metric("Out of Stock", (df["status"] == "Out of Stock").sum())

    st.write("")
    total_value = (df["price"] * df["quantity"]).sum()
    st.metric("Estimated Inventory Value", f"${total_value:,.2f}")

    # Buttons above the grid
def draw_action_buttons():    
    btn_col1, btn_col2, _ = st.columns([1, 1, 6])
    with btn_col1:
        if st.button("➕ Add Item", type="primary"):
            st.session_state.adding_product = True
    with btn_col2:
        if st.button("📥 Import CSV"):          
            st.session_state.importing = True

def render():

    df = compute_status(products_db.load_products_data())   # ← metrics also use derived Status

    draw_metrics(df)

    draw_action_buttons()

    draw_grid(df)

    if st.session_state.get("adding_product"):
        draw_add_form()

    if st.session_state.get("importing"):      
        draw_import_form()

    if st.session_state.get("editing_row") is not None:
        draw_edit_form(st.session_state.editing_row)