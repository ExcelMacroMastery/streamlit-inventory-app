import yaml
import streamlit as st
import streamlit_authenticator as stauth
from yaml.loader import SafeLoader
from pathlib import Path

def load_authenticator() -> stauth.Authenticate:
    login_dir = Path(__file__).resolve().parent
    with open(login_dir / "config.yaml") as f:
        config = yaml.load(f, Loader=SafeLoader)

    return stauth.Authenticate(
        config["credentials"],
        config["cookie"]["name"],
        config["cookie"]["key"],
        config["cookie"]["expiry_days"],
    )


def require_login() -> bool:
    """Call at the top of main_window.py before rendering anything.
    Returns True if the user is authenticated, False otherwise."""
    authenticator = load_authenticator()

    authenticator.login()  # no arguments needed in newer version

    if st.session_state.get("authentication_status"):
        with st.sidebar:
            st.markdown(f"👤 **{st.session_state.get('name')}**")
            authenticator.logout(location="sidebar")
        return True

    elif st.session_state.get("authentication_status") is False:
        st.error("Incorrect username or password.")
        return False

    else:
        st.info("Please enter your username and password.")
        return False
