import sqlite3
import json
from datetime import datetime
import os

# Default DB path, can be overridden for testing
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "db", "medstruct.db")


def _get_conn(db_path=None):
    if db_path is None:
        db_path = DB_PATH
    os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path=None):
    conn = _get_conn(db_path)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS prescriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT,
            patient_name TEXT,
            doctor_name TEXT,
            diagnosis TEXT,
            ocr_text TEXT,
            extracted_json TEXT,
            confidence REAL,
            llm_model TEXT,
            error_message TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS medications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prescription_id INTEGER,
            drug_name TEXT,
            dosage TEXT,
            frequency TEXT,
            duration TEXT,
            instructions TEXT,
            FOREIGN KEY(prescription_id) REFERENCES prescriptions(id)
        )
    """)
    conn.commit()
    conn.close()


def save_prescription(result_dict, db_path=None):
    """
    Saves the pipeline result_dict to the database.
    Expected keys: ocr_text, extracted, error, ocr_confidence, llm_model
    """
    conn = _get_conn(db_path)
    c = conn.cursor()

    extracted = result_dict.get("extracted") or {}

    patient_name = (
        extracted.get("patient", {}).get("name")
        if isinstance(extracted.get("patient"), dict)
        else None
    )
    doctor_name = (
        extracted.get("doctor", {}).get("name")
        if isinstance(extracted.get("doctor"), dict)
        else None
    )
    diagnosis = extracted.get("diagnosis")

    c.execute(
        """
        INSERT INTO prescriptions
        (created_at, patient_name, doctor_name, diagnosis, ocr_text, extracted_json, confidence, llm_model, error_message)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
        (
            datetime.now().isoformat(),
            patient_name,
            doctor_name,
            diagnosis,
            result_dict.get("ocr_text"),
            json.dumps(extracted),
            result_dict.get("ocr_confidence"),
            result_dict.get("llm_model"),
            result_dict.get("error"),
        ),
    )

    prescription_id = c.lastrowid

    # Save medications if available
    meds = extracted.get("medications", [])
    if isinstance(meds, list):
        for med in meds:
            if isinstance(med, dict):
                c.execute(
                    """
                    INSERT INTO medications (prescription_id, drug_name, dosage, frequency, duration, instructions)
                    VALUES (?, ?, ?, ?, ?, ?)
                """,
                    (
                        prescription_id,
                        med.get("drug_name"),
                        med.get("dosage"),
                        med.get("frequency"),
                        med.get("duration"),
                        med.get("instructions"),
                    ),
                )

    conn.commit()
    conn.close()
    return prescription_id


def get_all_prescriptions(limit=100, db_path=None):
    conn = _get_conn(db_path)
    c = conn.cursor()
    c.execute(
        """
        SELECT id, created_at, patient_name, doctor_name, error_message, confidence, llm_model
        FROM prescriptions
        ORDER BY id DESC LIMIT ?
    """,
        (limit,),
    )
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows


def get_prescription(row_id, db_path=None):
    conn = _get_conn(db_path)
    c = conn.cursor()

    # Get main record
    c.execute("SELECT * FROM prescriptions WHERE id = ?", (row_id,))
    row = c.fetchone()
    if not row:
        conn.close()
        return None

    result = dict(row)

    # Get medications
    c.execute("SELECT * FROM medications WHERE prescription_id = ?", (row_id,))
    result["medications"] = [dict(r) for r in c.fetchall()]

    conn.close()
    return result


def search_prescriptions(query, db_path=None):
    conn = _get_conn(db_path)
    c = conn.cursor()
    search_term = f"%{query}%"

    c.execute(
        """
        SELECT DISTINCT p.id, p.created_at, p.patient_name, p.doctor_name, p.diagnosis
        FROM prescriptions p
        LEFT JOIN medications m ON p.id = m.prescription_id
        WHERE p.patient_name LIKE ?
           OR p.doctor_name LIKE ?
           OR p.diagnosis LIKE ?
           OR m.drug_name LIKE ?
        ORDER BY p.id DESC
    """,
        (search_term, search_term, search_term, search_term),
    )

    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows


def get_stats(db_path=None):
    conn = _get_conn(db_path)
    c = conn.cursor()

    c.execute("SELECT COUNT(*) as total FROM prescriptions")
    total = c.fetchone()["total"] or 0

    today_str = datetime.now().isoformat()[:10] + "%"
    c.execute(
        "SELECT COUNT(*) as today FROM prescriptions WHERE created_at LIKE ?",
        (today_str,),
    )
    today = c.fetchone()["today"] or 0

    c.execute(
        "SELECT AVG(confidence) as avg_conf FROM prescriptions WHERE confidence IS NOT NULL"
    )
    avg_conf = c.fetchone()["avg_conf"]
    avg_conf = float(avg_conf) if avg_conf else 0.0

    c.execute(
        "SELECT COUNT(DISTINCT patient_name) as unique_patients FROM prescriptions WHERE patient_name IS NOT NULL"
    )
    unique_patients = c.fetchone()["unique_patients"] or 0

    conn.close()
    return {
        "total": total,
        "today": today,
        "avg_confidence": avg_conf,
        "unique_patients": unique_patients,
    }
