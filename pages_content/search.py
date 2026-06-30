import streamlit as st
from utils.database import search_prescriptions


def render():
    st.title("Search Records")
    query = st.text_input(
        "Search",
        placeholder="Patient name, doctor, diagnosis, drug name…",
        label_visibility="collapsed",
    )

    if not query:
        st.markdown(
            """
        <div style="text-align:center;margin-top:4rem;color:#475569">
            <div style="font-size:48px">🔍</div>
            <div style="font-size:16px;margin-top:12px">All searches run locally — nothing leaves your device.</div>
        </div>
        """,
            unsafe_allow_html=True,
        )
        return

    rows = search_prescriptions(query)
    st.caption(f'{len(rows)} result(s) for "{query}"')

    if not rows:
        st.info("No matching records found.")
        return

    for row in rows:
        st.markdown(
            f"**#{row['id']}** — {row['patient_name'] or '—'}  ·  "
            f"{row['doctor_name'] or '—'}  ·  {row['diagnosis'] or '—'}  "
            f"<span style='color:#475569;font-size:12px'>{row['created_at'][:10]}</span>",
            unsafe_allow_html=True,
        )
