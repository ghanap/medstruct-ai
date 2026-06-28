import pytest
from unittest.mock import patch
from utils.pipeline import run_pipeline

@pytest.mark.integration
@patch('utils.pipeline.extract_text')
@patch('utils.pipeline.extract_structured_data')
@patch('utils.pipeline.save_prescription')
def test_run_pipeline_success(mock_save, mock_llm, mock_ocr):
    # Setup mocks
    mock_ocr.return_value = ("Sample OCR Text", 92.5)
    mock_llm.return_value = ({"patient": {"name": "Bob"}}, "mistral")
    mock_save.return_value = 42 # Database ID
    
    result = run_pipeline("dummy_image.png", save_to_db=True)
    
    assert result["ocr_text"] == "Sample OCR Text"
    assert result["ocr_confidence"] == 92.5
    assert result["llm_model"] == "mistral"
    assert result["extracted"]["patient"]["name"] == "Bob"
    assert result["rx_id"] == 42
    assert result["error"] is None

@patch('utils.pipeline.extract_text')
def test_run_pipeline_ocr_failure(mock_ocr):
    # Setup mock to simulate Tesseract not installed
    mock_ocr.return_value = ("TESSERACT_NOT_FOUND_OR_FAILED: error", 0.0)
    
    result = run_pipeline("dummy.png")
    
    assert result["error"] == "Tesseract OCR is not installed or failed to run."
    assert result["rx_id"] is None
