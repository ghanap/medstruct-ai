from unittest.mock import patch
from utils.ocr import extract_text, preprocess_image


def test_preprocess_image(tmp_path):
    # Create a dummy image file
    from PIL import Image

    img_path = tmp_path / "test.png"
    img = Image.new("RGB", (100, 100), color="white")
    img.save(img_path)

    processed = preprocess_image(str(img_path))
    assert processed is not None
    assert processed.mode == "L"  # Should be grayscale


@patch("utils.ocr.pytesseract.image_to_string")
@patch("utils.ocr.pytesseract.image_to_data")
def test_extract_text_success(mock_data, mock_string, tmp_path):
    # Setup mocks
    mock_string.return_value = "Patient: John Doe\nRx: Paracetamol"
    mock_data.return_value = {"conf": ["90", "95", "-1", "85"]}

    # Dummy image
    from PIL import Image

    img_path = tmp_path / "test.png"
    img = Image.new("RGB", (10, 10))
    img.save(img_path)

    text, conf = extract_text(str(img_path))
    assert "John Doe" in text
    assert conf == 90.0  # Average of 90, 95, 85


def test_extract_text_missing_tesseract():
    # If tesseract is not installed or we give it a bad image, it should handle gracefully
    text, conf = extract_text("nonexistent_file.png")
    assert text == ""
    assert conf == 0.0
