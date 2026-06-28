import json
import streamlit as st
from PIL import Image
from datetime import datetime
from utils.pipeline import run_pipeline


def render():
    st.title("Upload & Analyse")
    st.caption("📍 100% offline — prescriptions, lab reports, X-rays, scans — Ollama auto-detects everything.")

    tab1, tab2 = st.tabs(["📁 Upload File", "📷 Take Picture"])
    with tab1:
        uploaded_file = st.file_uploader(
            "Drop any medical document here",
            type=["jpg", "jpeg", "png", "bmp", "tiff", "pdf"],
            help="Prescriptions, lab reports, X-rays, discharge summaries, blood tests",
        )
    with tab2:
        camera_file = st.camera_input("Point at document and capture")

    uploaded = uploaded_file or camera_file

    if not uploaded:
        st.markdown("""
        <div style="margin-top:3rem;text-align:center;color:#334155">
            <div style="font-size:64px">🏥</div>
            <div style="font-size:18px;font-weight:600;color:#64748b;margin-top:12px">Upload any medical document to get started</div>
            <div style="font-size:13px;color:#475569;margin-top:6px">Prescriptions · Lab Reports · X-Rays · Scans · Blood Tests</div>
        </div>
        """, unsafe_allow_html=True)
        return

    col_img, col_result = st.columns([1, 1], gap="large")

    with col_img:
        st.subheader("Preview")
        if uploaded.type == "application/pdf":
            st.info("PDF uploaded — first page will be processed.")
        else:
            st.image(Image.open(uploaded), use_container_width=True)

    with col_result:
        st.subheader("AI Analysis")
        st.caption("Ollama auto-detects the document type — no selection needed!")

        # Auto-trigger analysis when a new file is uploaded
        if "last_uploaded_file" not in st.session_state or st.session_state.last_uploaded_file != uploaded.name:
            st.session_state.last_uploaded_file = uploaded.name
            st.session_state.analysis_result = None

        if st.session_state.analysis_result is None:
            bar = st.progress(0)
            status = st.empty()

            status.markdown("🔍 **Auto-analyzing document…**")
            bar.progress(30)
            st.session_state.analysis_result = run_pipeline(uploaded, doc_type="auto", save_to_db=True)
            bar.progress(100)
            status.empty()
            bar.empty()

        result = st.session_state.analysis_result

        if result:
            if result["error"]:
                st.error(f"❌ {result['error']}")
                return

            rx = result["extracted"]

            # Type badge
            doc_type = rx.get("document_type", "other").replace("_", " ").title()
            emoji = {"Prescription":"💊","Lab Report":"🧪","Discharge Summary":"🏥",
                     "Xray Report":"🩻","Scan Report":"📡","Blood Test":"🩸"}.get(doc_type, "📄")
            st.success(f"✅ Record **#{result['rx_id']}** saved · {emoji} **{doc_type}** detected")

            # Summary (THE MOST IMPORTANT THING)
            if rx.get("summary"):
                st.markdown("### 📝 Plain-English Summary")
                st.info(rx["summary"])

            # Key concerns
            for concern in (rx.get("key_concerns") or []):
                st.warning(f"⚠️ {concern}")

            # Imaging (X-ray/scan)
            if rx.get("imaging_findings"):
                st.markdown("### 🩻 Imaging Findings")
                st.markdown(f"""
                <div style="background:#0d1526;border:1px solid #1e3a5f;border-radius:12px;padding:16px;color:#94a3b8">
                {rx['imaging_findings']}
                </div>
                """, unsafe_allow_html=True)

            # Diagnosis
            if rx.get("diagnosis"):
                st.markdown(f"🔬 **Diagnosis:** {rx['diagnosis']}")

            # Patient / Doctor collapsible
            with st.expander("👤 Patient & Doctor Details"):
                p = rx.get("patient") or {}
                d = rx.get("doctor") or {}
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("**Patient**")
                    st.write(f"Name: {p.get('name') or '—'}")
                    st.write(f"Age: {p.get('age') or '—'}")
                    st.write(f"Gender: {p.get('gender') or '—'}")
                with c2:
                    st.markdown("**Doctor / Facility**")
                    st.write(f"Name: {d.get('name') or '—'}")
                    st.write(f"Qualification: {d.get('qualification') or '—'}")
                    st.write(f"Hospital: {d.get('hospital') or '—'}")

            # Meds
            meds = rx.get("medications") or []
            if meds:
                st.markdown("**💊 Medications**")
                st.dataframe(meds, use_container_width=True, hide_index=True)

            # Labs
            labs = rx.get("lab_results") or []
            if labs:
                st.markdown("**🧪 Lab Results**")
                st.dataframe(labs, use_container_width=True, hide_index=True)

            # Download + raw OCR
            st.download_button(
                "⬇ Download JSON",
                data=json.dumps(rx, indent=2),
                file_name=f"medstruct_{result['rx_id']}_{datetime.now():%Y%m%d}.json",
                mime="application/json",
                use_container_width=True,
            )
            with st.expander("Raw OCR text"):
                st.text_area("", result["ocr_text"], height=160, label_visibility="collapsed")
            st.caption(f"OCR confidence: **{result['ocr_confidence']:.1f}%**")
