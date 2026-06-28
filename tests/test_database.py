import pytest
import os
from utils.database import (
    init_db,
    save_prescription,
    get_all_prescriptions,
    get_prescription,
    search_prescriptions,
    get_stats
)

TEST_DB = ":memory:"

@pytest.fixture(autouse=True)
def setup_database():
    # Initialize the schema in memory for each test
    init_db(TEST_DB)
    yield
    # No teardown needed for :memory: as it is cleared automatically,
    # but if we used a file we'd delete it here.

def test_save_and_get_prescription():
    result_dict = {
        "ocr_text": "Sample text",
        "ocr_confidence": 95.5,
        "llm_model": "test-model",
        "error": None,
        "extracted": {
            "patient": {"name": "John Doe", "age": "45"},
            "doctor": {"name": "Dr. Smith"},
            "diagnosis": "Common Cold",
            "medications": [
                {
                    "drug_name": "Paracetamol",
                    "dosage": "500mg",
                    "frequency": "1-1-1"
                }
            ]
        }
    }
    
    rx_id = save_prescription(result_dict, db_path=TEST_DB)
    assert rx_id == 1
    
    record = get_prescription(rx_id, db_path=TEST_DB)
    assert record is not None
    assert record["patient_name"] == "John Doe"
    assert record["doctor_name"] == "Dr. Smith"
    assert record["diagnosis"] == "Common Cold"
    
    meds = record["medications"]
    assert len(meds) == 1
    assert meds[0]["drug_name"] == "Paracetamol"

def test_get_all_prescriptions():
    for i in range(3):
        save_prescription({"extracted": {"patient": {"name": f"Patient {i}"}}}, db_path=TEST_DB)
        
    rows = get_all_prescriptions(limit=2, db_path=TEST_DB)
    assert len(rows) == 2
    # Should be descending order by ID
    assert rows[0]["patient_name"] == "Patient 2"
    assert rows[1]["patient_name"] == "Patient 1"

def test_search_prescriptions():
    save_prescription({"extracted": {"patient": {"name": "Alice"}}}, db_path=TEST_DB)
    save_prescription({"extracted": {"diagnosis": "Fever"}}, db_path=TEST_DB)
    save_prescription({"extracted": {"medications": [{"drug_name": "Ibuprofen"}]}}, db_path=TEST_DB)
    
    res1 = search_prescriptions("Alice", db_path=TEST_DB)
    assert len(res1) == 1
    
    res2 = search_prescriptions("Fever", db_path=TEST_DB)
    assert len(res2) == 1
    
    res3 = search_prescriptions("Ibuprofen", db_path=TEST_DB)
    assert len(res3) == 1

def test_get_stats():
    save_prescription({"ocr_confidence": 90.0, "extracted": {"patient": {"name": "Alice"}}}, db_path=TEST_DB)
    save_prescription({"ocr_confidence": 100.0, "extracted": {"patient": {"name": "Bob"}}}, db_path=TEST_DB)
    
    stats = get_stats(db_path=TEST_DB)
    assert stats["total"] == 2
    assert stats["today"] == 2
    assert stats["avg_confidence"] == 95.0
    assert stats["unique_patients"] == 2
