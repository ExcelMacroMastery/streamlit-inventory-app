# ==============================================================================
# LIFECYCLE MANAGEMENT: MODAL FORM & AGGRID SELECTION CLEANUP
# ==============================================================================
# WHY THIS LOGIC EXISTS: 
# AgGrid retains its visual selection state even during standard Streamlit reruns. 
# To prevent an infinite loop where closing the modal immediately re-opens it 
# (because the row remains highlighted), we use a "Key-Resetting" strategy.
#
# 1. MODAL RENDERING RULE:
#    The modal visibility is tied to `st.session_state.viewing_order`.
#    - If NOT None: The app draws the modal form overlay.
#    - If None: The modal stays hidden.
#
# 2. OPENING THE MODAL (User selects a row):
#    We listen for row clicks ONLY when no modal is active:
#    `if grid_response["selected_rows"] is not None and st.session_state.get("viewing_order") is None:`
#    - When triggered, we save the selected row to `st.session_state.viewing_order`.
#    - We call `st.rerun()` to refresh the page, which triggers Step 1 to draw the modal.
#
# 3. CLOSING THE MODAL (The Reset Trick):
#    When the user closes the form, `close_order_details()` is executed to run two steps:
#    - Step A: Sets `viewing_order = None` so the form won't render on the next run.
#    - Step B: Increments `st.session_state.grid_key` (used in `AgGrid(key=...)`).
#
#    NOTE: Incrementing the key forces Streamlit to destroy the old grid and mount 
#          a completely brand-new one, successfully wiping out the residual row selection.
# ==============================================================================

import streamlit as st
import data.sales_order_db as sales_order_db
from constants import GridDefaults
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode

def close_order_detail():
    st.session_state.viewing_order = None
    st.session_state.grid_key += 1
    st.rerun()

@st.dialog("Order Detail")
def draw_order_detail(order: dict):
    st.markdown(f"**Customer:** {order['customer_name']}")
    st.markdown(f"**Date:** {order['created_at']}")
    st.divider()

    lines_df = sales_order_db.load_order_lines(order["id"])

    if lines_df.empty:
        st.caption("No lines found for this order.")
    else:
        st.dataframe(
            lines_df[["product_name", "price", "quantity", "line_total"]].rename(columns={
                "product_name": "Product",
                "price":        "Price",
                "quantity":     "Qty",
                "line_total":   "Total",
            }),
            hide_index=True,
            use_container_width=True,
        )

    st.divider()
    close_col, t2 = st.columns([3, 1], vertical_alignment="bottom")
    with t2:
        st.markdown(f"**Subtotal:** ${order['subtotal']:,.2f}")
        st.markdown(f"**Tax:** ${order['tax']:,.2f}")
        st.markdown(f"**Total: ${order['total']:,.2f}**")
    with close_col:
        if st.button("Close", width="stretch", key="edit_cancel"):
            close_order_detail()

def draw_orders_grid(df):
    grid_builder = GridOptionsBuilder.from_dataframe(df)
    grid_builder.configure_grid_options(
        rowHeight=GridDefaults.ROW_HEIGHT,
        headerHeight=GridDefaults.HEADER_HEIGHT,
        getRowID="params.data.id",
    )
    grid_builder.configure_pagination(
        paginationAutoPageSize=False,
        paginationPageSize=GridDefaults.ROWS_PER_PAGE,
    )
    grid_builder.configure_selection(selection_mode="single", use_checkbox=False)
    grid_builder.configure_default_column(filter=True, filterParams={"buttons": ["reset"]})

    grid_builder.configure_column("id",            hide=True)
    grid_builder.configure_column("customer_name", headerName="Customer",   width=150, type=["textColumn"])
    grid_builder.configure_column("created_at",    headerName="Date",       width=140, type=["textColumn"])
    grid_builder.configure_column("subtotal",      headerName="Subtotal",   width=100, type=["numericColumn"],
                                  valueFormatter="data.subtotal.toLocaleString('en-US', {style: 'currency', currency: 'USD'})")
    grid_builder.configure_column("tax",           headerName="Tax",        width=80,  type=["numericColumn"],
                                  valueFormatter="data.tax.toLocaleString('en-US', {style: 'currency', currency: 'USD'})")
    grid_builder.configure_column("total",         headerName="Total",      width=100, type=["numericColumn"],
                                  valueFormatter="data.total.toLocaleString('en-US', {style: 'currency', currency: 'USD'})")

    grid_options = grid_builder.build()
    grid_response = AgGrid(
        data=df,
        gridOptions=grid_options,
        key=f"grid_{st.session_state.grid_key}", # redraw grid when changed - removes selection
        allow_unsafe_jscode=True,
        update_mode=GridUpdateMode.SELECTION_CHANGED,
        height=GridDefaults.HEIGHT,
    )

    # Show the order_detail dialog when a row is 
    # draw_order_detail() is called in render if viewing_order is not none
    if grid_response["selected_rows"] is not None and st.session_state.get("viewing_order") is None:
        selected = grid_response["selected_rows"].iloc[0].to_dict()
        st.session_state.viewing_order = selected
        st.rerun()
   

def render():
    if "viewing_order" not in st.session_state:
        st.session_state.viewing_order = None

    st.header("Order History")

    df = sales_order_db.load_orders_data()

    if df.empty:
        st.info("No orders yet.")
        return

    st.caption(f"{len(df)} order(s) — click a row to view details. Use column headers to filter.")

    draw_orders_grid(df)

    if st.session_state.viewing_order is not None:
        draw_order_detail(st.session_state.viewing_order)
        st.session_state.viewing_order = None
