import streamlit as st
from utils.database import get_stats


def render():
    st.title("Dashboard")
    stats = get_stats()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Records",    stats["total"])
    c2.metric("Added Today",      stats["today"])
    c3.metric("Avg Confidence",   f"{stats['avg_confidence']:.1f}%")
    c4.metric("Unique Patients",  stats["unique_patients"])

    st.markdown("---")
    st.markdown("""
    <div style="text-align:center;padding:2rem;color:#334155">
        <div style="font-size:13px">🔒 All data is stored locally in <code>db/medstruct.db</code>. Nothing leaves this device.</div>
    </div>
    """, unsafe_allow_html=True)
