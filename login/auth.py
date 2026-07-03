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
    Returns True if the user is authenticated, False otherwise.
    Does NOT render the sidebar badge/logout — call render_account_sidebar()
    separately, after your nav menu, for that."""
    authenticator = load_authenticator()
    st.session_state["_authenticator"] = authenticator  # reuse, avoid reloading yaml twice

    # Already authenticated (e.g. via valid cookie) — just refresh state.
    if st.session_state.get("authentication_status"):
        try:
            authenticator.login()
        except Exception as e:
            st.error(f"Login widget error: {type(e).__name__}: {e}")
        return True

    # Not authenticated yet — render the form centered.
    left, center, right = st.columns([1, 1, 1])
    with center:
        try:
            authenticator.login()
        except Exception as e:
            st.error(f"Login widget error: {type(e).__name__}: {e}")

        if st.session_state.get("authentication_status") is False:
            st.error("Incorrect username or password.")
        elif not st.session_state.get("authentication_status"):
            st.info("Please enter your username and password.")

    return bool(st.session_state.get("authentication_status"))


def render_account_sidebar():
    """Call this inside `with st.sidebar:` — badge + logout, styled light
    to be visible against a dark sidebar background."""
    authenticator = st.session_state.get("_authenticator")
    if authenticator is None or not st.session_state.get("authentication_status"):
        return

    st.markdown(
        f"<p style='color:#ffffff; font-size:16px; margin-bottom:0.5rem;'>"
        f"👤 <b>{st.session_state.get('name')}</b></p>",
        unsafe_allow_html=True,
    )
    try:
        authenticator.logout(location="sidebar")
    except Exception as e:
        st.error(f"Logout widget error: {type(e).__name__}: {e}")
    