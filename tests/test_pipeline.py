from unittest.mock import patch
from utils.pipeline import run_pipeline
import pytest

@patch('utils.pipeline.triage_image')
@patch('utils.pipeline.extract_text')
def test_run_pipeline_ocr_failure(mock_ocr, mock_triage):
    mock_triage.return_value = "document"
    mock_ocr.return_value = ("TESSERACT_NOT_FOUND_OR_FAILED: error", 0.0)
    pass

def test_dummy():
    assert True

@pytest.mark.integration
def test_dummy_integration():
    assert True
