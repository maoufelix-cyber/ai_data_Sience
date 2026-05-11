"""Lightweight session auth (Streamlit secrets)."""

from __future__ import annotations

import streamlit as st


def auth_enabled() -> bool:
    try:
        return bool(st.secrets.get("AUTH_ENABLED", False))
    except Exception:
        return False


def login_form() -> bool:
    """Return True if authenticated."""
    if not auth_enabled():
        st.session_state["_ci_role"] = st.session_state.get("_ci_role") or "admin"
        return True

    if st.session_state.get("_ci_authed"):
        return True

    st.markdown("### Masuk — Churn Intelligence")
    u = st.text_input("Username", key="ci_user")
    p = st.text_input("Password", type="password", key="ci_pass")
    if st.button("Login", type="primary"):
        block = st.secrets.get("users", {})
        users = dict(block) if block is not None else {}
        row = None
        if u in users:
            raw = users[u]
            row = dict(raw) if hasattr(raw, "keys") else raw
        if row and row.get("password") == p:
            st.session_state["_ci_authed"] = True
            st.session_state["_ci_role"] = row.get("role", "analyst")
            st.rerun()
        else:
            st.error("Kredensial tidak valid.")
    return bool(st.session_state.get("_ci_authed"))


def logout_button() -> None:
    if st.sidebar.button("Keluar"):
        st.session_state.pop("_ci_authed", None)
        st.session_state.pop("_ci_role", None)
        st.rerun()


def current_role() -> str:
    return str(st.session_state.get("_ci_role", "analyst"))


def require_admin() -> bool:
    return current_role() == "admin"
