"""
MedStruct AI — Streamlit Interface
Run: streamlit run app.py
"""

import json
import streamlit as st
from PIL import Image
from datetime import datetime

from utils.pipeline import run_pipeline
from utils.database import (
    get_all_prescriptions,
    get_prescription,
    search_prescriptions,
    get_stats,
    init_db,
)

# Initialize database tables if they don't exist
init_db()

# ── Page config ────────────────────────────────────────────────────
st.set_page_config(
    page_title="MedStruct AI",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────────────
st.markdown(
    """
<style>
    .metric-card {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 16px 20px;
        text-align: center;
    }
    .metric-card .value { font-size: 2rem; font-weight: 700; color: #1e40af; }
    .metric-card .label { font-size: 0.8rem; color: #64748b; text-transform: uppercase; }
    .offline-badge {
        background: #dcfce7; color: #166534;
        border: 1px solid #bbf7d0;
        border-radius: 20px; padding: 4px 12px;
        font-size: 12px; font-weight: 600;
        display: inline-block;
    }
    .stAlert { border-radius: 8px !important; }
</style>
""",
    unsafe_allow_html=True,
)

# ── Sidebar ────────────────────────────────────────────────────────
with st.sidebar:
    st.image("assets/logo.png", use_column_width=True) if False else None
    st.markdown("## 🏥 MedStruct AI")
    st.markdown(
        '<span class="offline-badge">🔒 100% Offline</span>', unsafe_allow_html=True
    )
    st.divider()
    page = st.radio(
        "Navigate",
        [
            "📤 Upload & Extract",
            "📋 Record History",
            "🔍 Search Records",
            "📊 Dashboard",
        ],
        label_visibility="collapsed",
    )
    st.divider()
    stats = get_stats()
    st.caption(f"**{stats['total']}** records stored")
    st.caption(f"**{stats['today']}** added today")

# ═══════════════════════════════════════════════════════════════════
# PAGE: Upload & Extract
# ═══════════════════════════════════════════════════════════════════
if page == "📤 Upload & Extract":
    st.title("Upload Medical Document")
    st.caption(
        "Prescriptions, lab reports, discharge summaries — processed entirely on your device."
    )

    tab1, tab2 = st.tabs(["📁 Upload File", "📷 Take Picture"])

    with tab1:
        uploaded_file = st.file_uploader(
            "Drop a file here or click to browse",
            type=["jpg", "jpeg", "png", "bmp", "tiff", "pdf"],
            help="Max 20 MB · Supported: JPG, PNG, BMP, TIFF, PDF",
        )

    with tab2:
        camera_file = st.camera_input("Take a picture of the document")

    uploaded = uploaded_file or camera_file

    if uploaded:
        col_img, col_result = st.columns([1, 1], gap="large")

        with col_img:
            st.subheader("Document preview")
            if uploaded.type == "application/pdf":
                st.info("PDF uploaded — first page will be processed.")
            else:
                st.image(Image.open(uploaded), use_column_width=True)

        with col_result:
            st.subheader("Extraction")
            doc_type = st.selectbox(
                "Document type",
                ["Prescription", "Lab Report", "Discharge Summary", "Other"],
            )

            run_btn = st.button(
                "⚡ Extract & Structure", type="primary", use_container_width=True
            )

            if run_btn:
                progress = st.progress(0, text="Starting OCR…")
                with st.spinner(""):
                    progress.progress(20, text="Running Tesseract OCR…")
                    result = run_pipeline(uploaded, doc_type=doc_type, save_to_db=True)
                    progress.progress(100, text="Done!")

                progress.empty()

                if result["error"]:
                    st.error(f"❌ {result['error']}")
                else:
                    st.success(f"✅ Saved as record **#{result['rx_id']}**")

                    rx = result["extracted"]

                    # Patient card
                    with st.container(border=True):
                        p = rx.get("patient", {})
                        st.markdown("**👤 Patient**")
                        c1, c2, c3 = st.columns(3)
                        c1.metric("Name", p.get("name") or "—")
                        c2.metric("Age", p.get("age") or "—")
                        c3.metric("Gender", p.get("gender") or "—")

                    # Doctor card
                    with st.container(border=True):
                        d = rx.get("doctor", {})
                        st.markdown("**🩺 Doctor / Facility**")
                        c1, c2 = st.columns(2)
                        c1.write(
                            f"**{d.get('name','—')}**  ·  {d.get('qualification','')}"
                        )
                        c2.write(d.get("hospital", "—"))

                    # Diagnosis
                    if rx.get("diagnosis"):
                        st.info(f"🔬 **Diagnosis:** {rx['diagnosis']}")

                    # Medications table
                    meds = rx.get("medications", [])
                    if meds:
                        st.markdown("**💊 Medications**")
                        st.dataframe(
                            meds,
                            column_config={
                                "drug_name": st.column_config.TextColumn("Drug"),
                                "dosage": st.column_config.TextColumn("Dosage"),
                                "frequency": st.column_config.TextColumn("Frequency"),
                                "duration": st.column_config.TextColumn("Duration"),
                                "instructions": st.column_config.TextColumn(
                                    "Instructions"
                                ),
                            },
                            use_container_width=True,
                            hide_index=True,
                        )

                    # Lab results
                    labs = rx.get("lab_results", [])
                    if labs:
                        st.markdown("**🧪 Lab Results**")
                        st.dataframe(labs, use_container_width=True, hide_index=True)

                    # Download JSON
                    st.download_button(
                        "⬇ Download structured JSON",
                        data=json.dumps(rx, indent=2),
                        file_name=f"medstruct_{result['rx_id']}_{datetime.now():%Y%m%d}.json",
                        mime="application/json",
                        use_container_width=True,
                    )

                    # OCR raw
                    with st.expander("Raw OCR text"):
                        st.text_area(
                            "",
                            result["ocr_text"],
                            height=160,
                            label_visibility="collapsed",
                        )

                    st.caption(f"OCR confidence: **{result['ocr_confidence']:.1f}%**")


# ═══════════════════════════════════════════════════════════════════
# PAGE: Record History
# ═══════════════════════════════════════════════════════════════════
elif page == "📋 Record History":
    st.title("Record History")
    rows = get_all_prescriptions(limit=100)

    if not rows:
        st.info("No records yet — upload a document to get started.")
    else:
        st.caption(f"{len(rows)} record(s) stored locally")

        for row in rows:
            ts = row["created_at"][:16]
            pat = row["patient_name"] or "Unknown patient"
            doc = row["doctor_name"] or "Unknown doctor"
            col_label = f"#{row['id']}  ·  {ts}  ·  {pat}  ·  {doc}"

            with st.expander(col_label):
                full = get_prescription(row["id"])
                c1, c2 = st.columns([3, 2])

                with c1:
                    extracted = json.loads(full["extracted_json"] or "{}")
                    meds = full.get("medications", [])
                    if meds:
                        st.markdown("**Medications**")
                        for m in meds:
                            st.write(
                                f"- **{m['drug_name']}** — {m['dosage']} {m['frequency']}"
                            )
                    if extracted.get("diagnosis"):
                        st.markdown(f"**Diagnosis:** {extracted['diagnosis']}")
                    if extracted.get("notes"):
                        st.markdown(f"**Notes:** {extracted['notes']}")

                with c2:
                    st.download_button(
                        "⬇ JSON",
                        data=json.dumps(extracted, indent=2),
                        file_name=f"record_{row['id']}.json",
                        mime="application/json",
                        key=f"dl_{row['id']}",
                    )
                    if row.get("error_message"):
                        st.warning(f"Error: {row['error_message']}")
                    st.caption(f"Confidence: {row.get('confidence', 0):.1f}%")
                    st.caption(f"Model: {row.get('llm_model','—')}")


# ═══════════════════════════════════════════════════════════════════
# PAGE: Search
# ═══════════════════════════════════════════════════════════════════
elif page == "🔍 Search Records":
    st.title("Search Records")
    query = st.text_input(
        "Search by patient name, doctor, diagnosis, or drug",
        placeholder="e.g. Paracetamol",
    )

    if query:
        rows = search_prescriptions(query)
        st.caption(f'{len(rows)} result(s) for "{query}"')
        for row in rows:
            st.markdown(
                f"**#{row['id']}** — {row['patient_name'] or '—'}  ·  "
                f"{row['doctor_name'] or '—'}  ·  {row['diagnosis'] or '—'}  "
                f"<span style='color:#94a3b8;font-size:12px'>{row['created_at'][:10]}</span>",
                unsafe_allow_html=True,
            )
    else:
        st.info("Type to search — all queries run locally.")


# ═══════════════════════════════════════════════════════════════════
# PAGE: Dashboard
# ═══════════════════════════════════════════════════════════════════
elif page == "📊 Dashboard":
    st.title("Dashboard")
    stats = get_stats()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total records", stats["total"])
    c2.metric("Added today", stats["today"])
    c3.metric("Avg confidence", f"{stats['avg_confidence']:.1f}%")
    c4.metric("Unique patients", stats["unique_patients"])

    st.divider()
    st.caption("All data is stored locally. Nothing leaves this device.")
