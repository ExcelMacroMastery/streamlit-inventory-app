import pandas as pd
import streamlit as st
from constants import GridDefaults
from data.schema import TableSchema
from st_aggrid import GridOptionsBuilder, AgGrid, JsCode, GridUpdateMode, DataReturnMode

custom_css = {
    ".ag-cell": {"font-size": "14px !important"},
    ".ag-header-cell-text": {"font-size": "14px !important", "font-weight": "600 !important"},
}     

def draw_grid(df: pd.DataFrame, products: TableSchema):

    grid_builder = GridOptionsBuilder.from_dataframe(df)
    grid_builder.configure_pagination(paginationAutoPageSize=False,paginationPageSize=GridDefaults.ROWS_PER_PAGE)
    grid_builder.configure_grid_options(
        rowHeight=GridDefaults.ROW_HEIGHT,
        headerHeight=GridDefaults.HEADER_HEIGHT, #44
        getRowID ="params.data.id"
    )
    grid_builder.configure_selection(
        selection_mode="single",
        use_checkbox=False
    )
    grid_builder.configure_default_column(
        filter=True,
        filterParams={"buttons": ["reset"]},
    )

    # Create and configure the columns
    for col in products.columns:
        if col.hide:
            grid_builder.configure_column(col.name, hide=True)
            continue

        if col.format == "currency":
            grid_builder.configure_column(
                col.name,
                headerName=col.label,
                width=col.width,
                type=["numericColumn"],
                valueFormatter=f"data.{col.name}.toLocaleString('en-US', {{style: 'currency', currency: 'USD'}})",
            )        
        else:
            grid_builder.configure_column(
                col.name,
                headerName=col.label,
                width=col.width
            )

    # Configure the status column with colors are based on the status
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
        "status",
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
        height=GridDefaults.HEIGHT,
    )

    if grid_response["selected_rows"] is not None and st.session_state.editing_row is None:
        selected_row_data = grid_response["selected_rows"].iloc[0].to_dict()
        st.session_state.editing_row = selected_row_data
        st.rerun()