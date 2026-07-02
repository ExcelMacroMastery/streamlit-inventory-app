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

    # Already authenticated (e.g. via valid cookie) — just refresh state,
    # no need for the centered form.
    if st.session_state.get("authentication_status"):
        try:
            authenticator.login()
        except Exception as e:
            st.error(f"Login widget error: {type(e).__name__}: {e}")

        with st.sidebar:
            st.markdown(f"👤 **{st.session_state.get('name')}**")
            authenticator.logout(location="sidebar")
        return True

    # Not authenticated yet — render the form centered, and keep any
    # status message inside the same column so it lines up under the box.
    left, center, right = st.columns([1, 1, 1])
    with center:
        try:
            authenticator.login()
        except Exception as e:
            st.error(f"Login widget error: {type(e).__name__}: {e}")

        # Check status again now that login() has run
        if st.session_state.get("authentication_status") is False:
            st.error("Incorrect username or password.")
        elif not st.session_state.get("authentication_status"):
            st.info("Please enter your username and password.")

    return bool(st.session_state.get("authentication_status"))