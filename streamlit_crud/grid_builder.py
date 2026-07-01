import pandas as pd
import streamlit as st
from st_aggrid import GridOptionsBuilder, AgGrid, JsCode, GridUpdateMode

from .schema import TableSchema

DEFAULT_STATUS_STYLES = {
    "In Stock":     {"bg": "#e6f9f0", "color": "#27ae60", "border": "#a8e6c8"},
    "Low Stock":    {"bg": "#fff8e6", "color": "#f39c12", "border": "#ffd980"},
    "Out of Stock": {"bg": "#fdecea", "color": "#e74c3c", "border": "#f5c6c2"},
}

DEFAULT_CUSTOM_CSS = {
    ".ag-cell": {"font-size": "14px !important"},
    ".ag-header-cell-text": {"font-size": "14px !important", "font-weight": "600 !important"},
}


def _badge_cell_renderer(styles: dict) -> JsCode:
    styles_js = str(styles).replace("'", '"')
    return JsCode(f"""
    class BadgeRenderer {{
        init(params) {{
            const value = params.value;
            const styles = {styles_js};
            const style = styles[value] || {{ bg: '#f0f0f0', color: '#888', border: '#ccc' }};
            this.eGui = document.createElement('span');
            this.eGui.innerHTML = value;
            this.eGui.style.cssText = `
                display: inline-block;
                padding: 3px 12px;
                border-radius: 12px;
                font-size: 13px;
                font-weight: 500;
                background-color: ${{style.bg}};
                color: ${{style.color}};
                border: 1px solid ${{style.border}};
            `;
        }}
        getGui() {{ return this.eGui; }}
    }}
    """)


def draw_grid(
    df: pd.DataFrame,
    schema: TableSchema,
    row_height: int = 40,
    header_height: int = 44,
    rows_per_page: int = 20,
    height: int = 500,
    badge_column: str | None = None,
    badge_styles: dict | None = None,
    custom_css: dict | None = None,
    editing_key: str = "editing_row",
    grid_key: str = "grid_key",
):
    """Generic AgGrid for any TableSchema.

    To render a column as colored badges (like a status column), pass:
        badge_column="status", badge_styles=DEFAULT_STATUS_STYLES
    Works for any column name, not just 'status'.
    """
    custom_css = custom_css or DEFAULT_CUSTOM_CSS

    grid_builder = GridOptionsBuilder.from_dataframe(df)
    grid_builder.configure_pagination(paginationAutoPageSize=False, paginationPageSize=rows_per_page)
    grid_builder.configure_grid_options(
        rowHeight=row_height,
        headerHeight=header_height,
        getRowID="params.data.id",
    )
    grid_builder.configure_selection(selection_mode="single", use_checkbox=False)
    grid_builder.configure_default_column(filter=True, filterParams={"buttons": ["reset"]})

    for col in schema.columns:
        if col.hide:
            grid_builder.configure_column(col.name, hide=True)
            continue
        if col.name == badge_column:
            continue

        if col.format == "currency":
            grid_builder.configure_column(
                col.name,
                headerName=col.label,
                width=col.width,
                type=["numericColumn"],
                valueFormatter=f"data.{col.name}.toLocaleString('en-US', {{style: 'currency', currency: 'USD'}})",
            )
        elif col.widget == "text":
            grid_builder.configure_column(
                col.name,
                headerName=col.label,
                width=col.width,
                type=["textColumn"],
            )
        else:
            grid_builder.configure_column(
                col.name,
                headerName=col.label,
                width=col.width,
            )

    if badge_column and badge_styles and badge_column in df.columns:
        grid_builder.configure_column(
            badge_column,
            cellRenderer=_badge_cell_renderer(badge_styles),
            width=90,
            cellStyle={"display": "flex", "alignItems": "center", "justifyContent": "center", "paddingTop": "4px"},
        )

    grid_options = grid_builder.build()
    grid_response = AgGrid(
        data=df,
        gridOptions=grid_options,
        key=f"grid_{st.session_state.get(grid_key, 0)}",
        allow_unsafe_jscode=True,
        update_mode=GridUpdateMode.SELECTION_CHANGED,
        custom_css=custom_css,
        height=height,
    )

    if grid_response["selected_rows"] is not None and st.session_state.get(editing_key) is None:
        selected_row_data = grid_response["selected_rows"].iloc[0].to_dict()
        st.session_state[editing_key] = selected_row_data
        st.rerun()
