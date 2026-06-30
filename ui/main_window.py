import streamlit as st
import importlib
from streamlit_option_menu import option_menu
from constants import AppColours

st.set_page_config(layout="wide")

# Initialize state
st.session_state.setdefault("editing_row", None)
st.session_state.setdefault("adding_product", False)
st.session_state.setdefault("importing", False)
st.session_state.setdefault("confirm_delete", False)
st.session_state.setdefault("grid_key", 0)
st.session_state.setdefault("selected_page", None)

st.markdown("""
<style>
[data-testid="stSidebar"] {
    background-color: #182235 !important;
}
</style>
""", unsafe_allow_html=True)

PAGES = [
    {"name": "Products",     "icon": "house",        "module": "ui_pages.products_page"},
    {"name": "Customers",    "icon": "list-task",     "module": "ui_pages.customer_page"},
    {"name": "Sales Orders", "icon": "cloud-upload", "module": "ui_pages.sales_order_page"},    
    {"name": "Reports",      "icon": "list-task",     "module": None},
    {"name": "Settings",     "icon": "gear",          "module": None},
]

PAGE_MODULES = {p["name"]: p["module"] for p in PAGES}


def select_page(page):
    module_path = PAGE_MODULES.get(page)
    if module_path:
        page_module = importlib.import_module(module_path)
        page_module.render()
    else:
        st.write(f"Selection changed to {page}")


def on_change_menu_a(key):
    pass


SIDEBAR_STYLES = {
    "container":         {
                            "padding": "0!important",
                            "background-color": AppColours.SIDEBAR_BG,
                            "border-radius": "0!important",
                            "overflow": "hidden",
                        },
    "icon":              {"color": "#ffffff", "font-size": "18px"},
    "nav-link":          {"font-size": "18px", "text-align": "left", "margin": "0px", "color": "#ffffff", "--hover-color": f"{AppColours.SIDEBAR_HOVER}!important"},
    "nav-link-selected": {"background-color": "#26344d!important"},
    "menu-icon":         {"color": "#ffffff !important"},
    "menu-title":        {"color": "#ffffff !important", "font-size": "25px"},
}

with st.sidebar:
    st.session_state.selected_page = option_menu(
        "Inventory",
        [p["name"] for p in PAGES],
        icons=[p["icon"] for p in PAGES],
        menu_icon="cast",
        on_change=on_change_menu_a,
        key="menu_a",
        styles=SIDEBAR_STYLES,
    )

select_page(st.session_state.selected_page)