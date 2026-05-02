"""Generisches Streamlit Theme — DSGVO-konform, self-hosted."""
import streamlit as st

def init_theme():
    """Dark Sidebar Theme."""
    st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #151e2e; }
    [data-testid="stSidebar"] * { color: #c8d6e5 !important; }
    </style>
    """, unsafe_allow_html=True)

def theme_toggle_sidebar():
    """Sidebar-Toggle (no-op, sidebar always visible)."""
    pass

def app_footer():
    """DSGVO Footer."""
    st.markdown("---")
    st.caption("🔒 100% DSGVO-konform | Self-Hosted | Ollama")
