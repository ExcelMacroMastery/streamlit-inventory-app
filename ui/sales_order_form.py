import streamlit as st
import data.suppliers_db as suppliers_db
import data.sales_order_db as sales_order_db
import data.products_db as products_db
from data.sales_order_schema import TAX_RATE


# ── Session state helpers ─────────────────────────────────────────────────────

def _init_state():
    if "so_lines" not in st.session_state:
        st.session_state.so_lines = []          # list of line dicts
    if "so_customer_id" not in st.session_state:
        st.session_state.so_customer_id = None


def _reset_state():
    st.session_state.so_lines = []
    st.session_state.so_customer_id = None


def _add_line():
    st.session_state.so_lines.append({
        "product_id":   None,
        "product_name": "",
        "price":        0.0,
        "quantity":     1,
        "line_total":   0.0,
    })


def _remove_line(i: int):
    st.session_state.so_lines.pop(i)


# ── Sub-sections ──────────────────────────────────────────────────────────────

def _draw_customer_section() -> dict | None:
    st.subheader("Customer")
    customers_df = suppliers_db.load_data()

    if customers_df.empty:
        st.warning("No customers found. Add customers first.")
        return None

    col, _ = st.columns([2, 4])  # ← constrain to left third of screen

    with col:
        options = ["— select —"] + customers_df["name"].tolist()
        choice = st.selectbox("Customer", options, key="so_customer_select", label_visibility="collapsed")

        if choice == "— select —":
            return None

        customer = customers_df[customers_df["name"] == choice].iloc[0].to_dict()
        st.session_state.so_customer_id = customer["id"]

        with st.container(border=True):
            st.markdown(f"**{customer['name']}**")
            st.markdown(customer.get("email", ""))
            st.markdown(customer.get("phone", ""))
            st.markdown(customer.get("address", ""))

    return customer


def _draw_lines_section(products_df):
    """Render each order line as a row of widgets."""
    st.subheader("Order Lines")

    if not st.session_state.so_lines:
        st.caption("No lines added yet.")
    else:
        # Header
        h1, h2, h3, h4, h5 = st.columns([4, 2, 1, 2, 0.5])
        h1.markdown("**Product**")
        h2.markdown("**Price**")
        h3.markdown("**Qty**")
        h4.markdown("**Line Total**")

        product_options = ["— select —"] + products_df["name"].tolist()

        for i, line in enumerate(st.session_state.so_lines):
            c1, c2, c3, c4, c5 = st.columns([4, 2, 1, 2, 0.5])

            with c1:
                current = line["product_name"] if line["product_name"] else "— select —"
                idx = product_options.index(current) if current in product_options else 0
                selected = st.selectbox("Product", product_options, index=idx,
                                        key=f"so_product_{i}", label_visibility="collapsed")
                if selected != "— select —" and selected != line["product_name"]:
                    product_row = products_df[products_df["name"] == selected].iloc[0]
                    st.session_state.so_lines[i]["product_id"]   = int(product_row["id"])
                    st.session_state.so_lines[i]["product_name"] = selected
                    st.session_state.so_lines[i]["price"]        = float(product_row["price"])
                    st.session_state.so_lines[i]["quantity"]     = 1
                    st.session_state.so_lines[i]["line_total"]   = float(product_row["price"])
                    st.rerun()

            with c2:
                price = line["price"]
                st.markdown(f"<div style='padding-top:8px'>${price:,.2f}</div>", unsafe_allow_html=True)

            with c3:
                qty = st.number_input("Qty", min_value=1, value=line["quantity"],
                                      step=1, key=f"so_qty_{i}", label_visibility="collapsed")
                if qty != line["quantity"]:
                    st.session_state.so_lines[i]["quantity"]   = qty
                    st.session_state.so_lines[i]["line_total"] = round(line["price"] * qty, 2)
                    st.rerun()

            with c4:
                total = line["line_total"]
                st.markdown(f"<div style='padding-top:8px'>${total:,.2f}</div>", unsafe_allow_html=True)

            with c5:
                if st.button("✕", key=f"so_remove_{i}"):
                    _remove_line(i)
                    st.rerun()

    if st.button("＋ Add Line"):
        _add_line()
        st.rerun()


def _draw_totals_section() -> tuple[float, float, float]:
    """Compute and display subtotal / tax / total. Returns the three values."""
    subtotal = round(sum(l["line_total"] for l in st.session_state.so_lines), 2)
    tax      = round(subtotal * TAX_RATE, 2)
    total    = round(subtotal + tax, 2)

    st.divider()
    t1, t2 = st.columns([3, 1])
    with t2:
        st.markdown(f"**Subtotal:** ${subtotal:,.2f}")
        st.markdown(f"**Tax ({int(TAX_RATE * 100)}%):** ${tax:,.2f}")
        st.markdown(f"**Total: ${total:,.2f}**")

    return subtotal, tax, total


def _validate(customer_id, lines, products_df) -> list[str]:
    errors = []
    if not customer_id:
        errors.append("Please select a customer.")
    if not lines:
        errors.append("Please add at least one order line.")
    for line in lines:
        if not line["product_id"]:
            errors.append(f"Line has no product selected.")
            continue
        product = products_df[products_df["id"] == line["product_id"]].iloc[0]
        if line["quantity"] > product["quantity"]:
            errors.append(f"{line['product_name']}: only {int(product['quantity'])} in stock.")
    return errors


# ── Main entry point ──────────────────────────────────────────────────────────

def render():
    _init_state()

    st.header("New Sales Order")

    if st.session_state.get("so_success_message"):
        st.success(st.session_state.so_success_message)
        st.session_state.so_success_message = None

    products_df = products_db.load_data()
    if products_df.empty:
        st.warning("No products found in inventory.")
        return

    customer = _draw_customer_section()

    st.divider()

    _draw_lines_section(products_df)

    subtotal, tax, total = _draw_totals_section()

    st.divider()

    save_col, cancel_col = st.columns([1, 5])
    with save_col:
        if st.button("Save Order", type="primary"):
            errors = _validate(st.session_state.so_customer_id, st.session_state.so_lines,products_df)
            if errors:
                for e in errors:
                    st.error(e)
            else:
                try:
                    order_id = sales_order_db.save_order(
                        customer_id=st.session_state.so_customer_id,
                        lines=st.session_state.so_lines,
                        subtotal=subtotal,
                        tax=tax,
                        total=total,
                    )
                    sales_order_db.load_orders_data.clear()
                    products_db.load_data.clear() 
                    _reset_state()
                    st.session_state.so_success_message = f"Order #{order_id} saved successfully! You can view it in **Order History**."
                    st.rerun()
                except Exception as e:
                    st.error(f"Unexpected error: {e}")
    with cancel_col:
        if st.button("Clear"):
            _reset_state()
            st.rerun()

