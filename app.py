"""
MedStruct AI — Main entry point
"""

import streamlit as st
from utils.database import init_db, get_stats

# ── Page config ────────────────────────────────────────────────────
st.set_page_config(
    page_title="MedStruct AI",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize DB on every load
init_db()

# ── Custom CSS ─────────────────────────────────────────────────────
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

html, body, p, label, .stMarkdown {
    font-family: 'Inter', sans-serif !important;
}

/* ── BACKGROUNDS ── */
.stApp { background: #f7f9fc !important; }
.main .block-container {
    padding-top: 2rem !important;
    max-width: 1100px !important;
    background: #f7f9fc !important;
}

/* ── SIDEBAR ── */
section[data-testid="stSidebar"] > div:first-child {
    background: #ffffff !important;
    border-right: 1.5px solid #e4eaf2 !important;
    padding: 1.5rem 0.75rem !important;
}

/* ── BRAND ── */
.brand-name {
    font-size: 19px; font-weight: 800;
    color: #0a1628; letter-spacing: -0.5px;
}
.brand-sub {
    font-size: 10px; color: #8fa3b1;
    text-transform: uppercase; letter-spacing: 1.5px;
}
.offline-pill {
    display: inline-flex; align-items: center; gap: 5px;
    background: #e8fdf5; color: #059669;
    border: 1px solid #a7f3d0;
    border-radius: 999px; padding: 3px 10px;
    font-size: 11px; font-weight: 600;
    margin: 10px 0 18px;
}

/* ── NAV SECTION HEADER ── */
.nav-section {
    font-size: 10px; font-weight: 700; color: #b0bec5;
    text-transform: uppercase; letter-spacing: 1.5px;
    margin: 14px 0 6px 4px;
}

/* ── SIDEBAR NAV BUTTONS ── */
section[data-testid="stSidebar"] .stButton > button {
    background: transparent !important;
    color: #546e7a !important;
    border: none !important;
    border-radius: 8px !important;
    text-align: left !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    padding: 10px 12px !important;
    margin: 2px 0 !important;
    width: 100% !important;
    transition: all 0.15s ease !important;
    box-shadow: none !important;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    background: #f0f4ff !important;
    color: #0a5a9c !important;
    transform: none !important;
}

/* ── STAT CHIPS ── */
.stat-chip {
    display: flex; justify-content: space-between; align-items: center;
    background: #f0f4f8; border: 1px solid #dce6f0; border-radius: 8px;
    padding: 8px 12px; margin: 4px 0; font-size: 13px; color: #607d8b;
}
.stat-chip .val { color: #0077b6; font-weight: 700; font-size: 15px; }

/* ── HEADINGS ── */
h1 {
    color: #0a1628 !important; font-weight: 800 !important;
    font-size: 1.9rem !important; letter-spacing: -0.5px !important;
    -webkit-text-fill-color: #0a1628 !important;
    background: none !important;
}
h2, h3 { color: #1a2e44 !important; font-weight: 700 !important; }
p, span, div { color: #374151; }

/* ── PRIMARY BUTTONS ── */
button[kind="primary"] {
    background: linear-gradient(135deg, #0077b6 0%, #00b4a0 100%) !important;
    color: white !important; border: none !important;
    border-radius: 8px !important; font-weight: 600 !important;
    font-size: 14px !important;
    box-shadow: 0 2px 12px rgba(0,119,182,0.25) !important;
    transition: all 0.2s !important;
}
button[kind="primary"]:hover {
    box-shadow: 0 4px 18px rgba(0,119,182,0.4) !important;
    transform: translateY(-1px) !important;
}
.stDownloadButton > button {
    background: linear-gradient(135deg, #0077b6 0%, #00b4a0 100%) !important;
    color: white !important; border: none !important; border-radius: 8px !important;
    font-weight: 600 !important;
    box-shadow: 0 2px 12px rgba(0,119,182,0.2) !important;
}

/* ── FILE UPLOADER ── */
div[data-testid="stFileUploader"] {
    background: #ffffff !important;
    border: 2px dashed #cdd8e3 !important;
    border-radius: 12px !important;
    transition: all 0.2s !important;
}
div[data-testid="stFileUploader"]:hover {
    border-color: #0077b6 !important;
    background: #f0f7ff !important;
}
div[data-testid="stFileUploader"] label,
div[data-testid="stFileUploader"] small {
    color: #546e7a !important;
}

/* ── TABS ── */
div[data-baseweb="tab-list"] {
    background: #f0f4f8 !important; border-radius: 8px !important;
    padding: 3px !important; border: none !important;
}
button[data-baseweb="tab"] {
    background: transparent !important; color: #607d8b !important;
    font-weight: 500 !important; border-radius: 6px !important;
    border: none !important;
}
button[data-baseweb="tab"][aria-selected="true"] {
    background: #ffffff !important; color: #0077b6 !important;
    font-weight: 600 !important; border-bottom: none !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.1) !important;
}

/* ── TEXT INPUTS ── */
.stTextInput input, .stTextArea textarea {
    background: #ffffff !important; border: 1.5px solid #dce6f0 !important;
    color: #1a2e44 !important; border-radius: 8px !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: #0077b6 !important;
    box-shadow: 0 0 0 3px rgba(0,119,182,0.1) !important;
}

/* ── DATAFRAME ── */
div[data-testid="stDataFrame"] {
    border: 1.5px solid #dce6f0 !important;
    border-radius: 10px !important; overflow: hidden !important;
    background: #ffffff !important;
}

/* ── METRICS ── */
div[data-testid="metric-container"] {
    background: #ffffff; border: 1.5px solid #e4eaf2;
    border-radius: 12px; padding: 1rem;
    box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}
div[data-testid="metric-container"] label { color: #607d8b !important; font-size: 12px !important; font-weight: 600 !important; text-transform: uppercase; letter-spacing: 0.5px; }
div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
hr { border-color: #1e2d4a !important; }
</style>
""",
    unsafe_allow_html=True,
)

# ── Sidebar nav ────────────────────────────────────────────────────
PAGES = {
    "upload": ("📤", "Upload & Analyse"),
    "history": ("📋", "Record History"),
    "search": ("🔍", "Search Records"),
    "dashboard": ("📊", "Dashboard"),
}

if "page" not in st.session_state:
    st.session_state.page = "upload"

with st.sidebar:
    st.markdown(
        '<div class="brand"><span style="font-size:28px">🏥</span><div><div class="brand-name">MedStruct AI</div><div class="brand-sub">Offline Medical OCR</div></div></div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="offline-pill"><span>●</span> 100% Offline</div>',
        unsafe_allow_html=True,
    )

    st.markdown('<div class="nav-section">Navigation</div>', unsafe_allow_html=True)
    for key, (icon, label) in PAGES.items():
        is_active = st.session_state.page == key
        marker = "→ " if is_active else "   "
        if st.button(
            f"{icon}  {marker}{label}", key=f"nav_{key}", use_container_width=True
        ):
            st.session_state.page = key
            st.rerun()

    st.markdown("---")
    stats = get_stats()
    st.markdown(
        f'<div class="stat-chip">Records stored<span class="val">{stats["total"]}</span></div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div class="stat-chip">Added today<span class="val">{stats["today"]}</span></div>',
        unsafe_allow_html=True,
    )

# ── Route to page ──────────────────────────────────────────────────
page = st.session_state.page

if page == "upload":
    from pages_content.upload import render
elif page == "history":
    from pages_content.history import render
elif page == "search":
    from pages_content.search import render
elif page == "dashboard":
    from pages_content.dashboard import render

render()
