import json
import streamlit as st
from utils.database import get_all_prescriptions, get_prescription


def render():
    st.title("Record History")
    rows = get_all_prescriptions(limit=100)

    if not rows:
        st.markdown(
            """
        <div style="text-align:center;margin-top:4rem;color:#475569">
            <div style="font-size:48px">📋</div>
            <div style="font-size:16px;margin-top:12px">No records yet — upload a document first.</div>
        </div>
        """,
            unsafe_allow_html=True,
        )
        return

    st.caption(f"{len(rows)} record(s) stored locally on this device")

    for row in rows:
        ts = row["created_at"][:16]
        pat = row["patient_name"] or "Unknown patient"
        doc_type = row.get("doc_type", "").title() or "Document"
        label = f"#{row['id']}  ·  {ts}  ·  {pat}  ·  {doc_type}"

        with st.expander(label):
            full = get_prescription(row["id"])
            extracted = json.loads(full.get("extracted_json") or "{}")

            summary = extracted.get("summary")
            if summary:
                st.info(summary)

            c1, c2 = st.columns([3, 1])
            with c1:
                if extracted.get("diagnosis"):
                    st.markdown(f"**Diagnosis:** {extracted['diagnosis']}")
                meds = full.get("medications", [])
                if meds:
                    st.markdown("**Medications**")
                    for m in meds:
                        st.write(
                            f"- **{m['drug_name']}** — {m.get('dosage','')} {m.get('frequency','')}"
                        )
                if extracted.get("imaging_findings"):
                    st.markdown(f"**Imaging:** {extracted['imaging_findings']}")
            with c2:
                st.download_button(
                    "⬇ JSON",
                    data=json.dumps(extracted, indent=2),
                    file_name=f"record_{row['id']}.json",
                    mime="application/json",
                    key=f"dl_{row['id']}",
                )
                st.caption(f"Confidence: {row.get('confidence', 0):.1f}%")
                st.caption(f"Model: {row.get('llm_model','—')}")
