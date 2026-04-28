"""Unified Theme System for Cela's Streamlit Dashboards."""
import streamlit as st

COLORS = {
    "light": {
        "primary": "#1E3A5F", "secondary": "#4A6FA5", "accent": "#2EC4B6",
        "bg": "#FAFBFC", "surface": "#FFFFFF", "text": "#1A1A2E",
        "text_secondary": "#6B7280", "success": "#2ECC71", "warning": "#F39C12",
        "error": "#E74C3C", "border": "#E1E5EB", "metric_bg": "#F0F4F8",
        "sidebar_bg": "#FFFFFF", "card_bg": "#FFFFFF", "code_bg": "#F3F4F6",
    },
    "dark": {
        "primary": "#4A90D9", "secondary": "#6BA3D6", "accent": "#2EC4B6",
        "bg": "#0F1419", "surface": "#1A2332", "text": "#E8E8ED",
        "text_secondary": "#9CA3AF", "success": "#2ECC71", "warning": "#F39C12",
        "error": "#E74C3C", "border": "#2D3748", "metric_bg": "#1E293B",
        "sidebar_bg": "#141B27", "card_bg": "#1A2332", "code_bg": "#1E293B",
    },
}

def get_theme():
    if "cela_theme" not in st.session_state:
        st.session_state.cela_theme = "light"
    return st.session_state.cela_theme

def toggle_theme():
    t = get_theme()
    st.session_state.cela_theme = "dark" if t == "light" else "light"

def get_colors():
    return COLORS[get_theme()]

def _build_css(theme):
    c = COLORS[theme]
    return """<style>
[data-testid="stAppViewContainer"]{background-color:%(bg)s;color:%(text)s}
[data-testid="stSidebar"]{background-color:%(sidebar_bg)s}
[data-testid="stSidebarContent"]{color:%(text)s}
[data-testid="stMain"]{background-color:%(bg)s}
h1,h2,h3,h4,h5,h6{color:%(text)s!important}
p,span,div,label{color:%(text)s}
.stCaption{color:%(text_secondary)s!important}
[data-testid="stMetric"]{background-color:%(metric_bg)s;border:1px solid %(border)s;border-radius:12px;padding:16px}
[data-testid="stMetricLabel"]{color:%(text_secondary)s!important}
[data-testid="stMetricValue"]{color:%(text)s!important}
[data-testid="stDataFrame"]{border:1px solid %(border)s;border-radius:8px}
.stButton>button{border-radius:8px;font-weight:500;transition:all .2s ease}
.stButton>button:hover{transform:translateY(-1px);box-shadow:0 4px 12px rgba(0,0,0,.15)}
[data-testid="stBaseButton-primary"]{background-color:%(primary)s!important;border-color:%(primary)s!important}
.stTabs [data-baseweb="tab-list"]{gap:4px}
.stTabs [data-baseweb="tab"]{border-radius:8px 8px 0 0;font-weight:500}
.stTabs [data-baseweb="tab-active"]{background-color:%(surface)s;border-bottom:2px solid %(primary)s}
.streamlit-expanderHeader{font-weight:500;border-radius:8px}
hr,.stDivider{border-color:%(border)s!important}
[data-testid="stAlert"]{border-radius:8px}
::-webkit-scrollbar{width:8px}
::-webkit-scrollbar-track{background:%(bg)s}
::-webkit-scrollbar-thumb{background:%(border)s;border-radius:4px}
.ampel-gruen{background-color:%(success)s;color:#fff;padding:8px 16px;border-radius:8px;font-weight:700;display:inline-block}
.ampel-gelb{background-color:%(warning)s;color:#fff;padding:8px 16px;border-radius:8px;font-weight:700;display:inline-block}
.ampel-rot{background-color:%(error)s;color:#fff;padding:8px 16px;border-radius:8px;font-weight:700;display:inline-block}
.score-high{color:%(success)s;font-weight:700;font-size:1.5rem}
.score-mid{color:%(warning)s;font-weight:700;font-size:1.5rem}
.score-low{color:%(error)s;font-weight:700;font-size:1.5rem}
.priority-high{color:%(error)s;font-weight:700}
.priority-medium{color:%(warning)s;font-weight:700}
.priority-low{color:%(success)s;font-weight:700}
.metric-card{background-color:%(metric_bg)s;border:1px solid %(border)s;border-radius:12px;padding:20px;text-align:center}
.main-header{background:linear-gradient(135deg,%(primary)s,%(secondary)s);padding:24px 32px;border-radius:12px;margin-bottom:24px}
.main-header h1{color:#fff!important;margin:0}
.main-header p{color:rgba(255,255,255,.85)!important;margin:4px 0 0}
.sub-header{color:%(text_secondary)s;font-size:1.1rem;margin-bottom:16px}
</style>""" % c

def init_theme():
    st.markdown(_build_css(get_theme()), unsafe_allow_html=True)

def theme_toggle_sidebar():
    with st.sidebar:
        st.divider()
        c1, c2 = st.columns(2)
        with c1:
            if st.button("\u2600\ufe0f Light", use_container_width=True,
                         type="primary" if get_theme() == "light" else "secondary"):
                st.session_state.cela_theme = "light"
                st.rerun()
        with c2:
            if st.button("\ud83c\udf19 Dark", use_container_width=True,
                         type="primary" if get_theme() == "dark" else "secondary"):
                st.session_state.cela_theme = "dark"
                st.rerun()

def app_header(icon, title, subtitle=""):
    sub = "<p>%s</p>" % subtitle if subtitle else ""
    st.markdown('<div class="main-header"><h1>%s %s</h1>%s</div>' % (icon, title, sub), unsafe_allow_html=True)

def app_footer():
    c = get_colors()
    st.markdown('<div style="text-align:center;padding:24px 0 12px;color:%s;font-size:.85rem">Powered by Cela &mdash; AI Automation</div>' % c["text_secondary"], unsafe_allow_html=True)
