from utils.ocr import extract_text

def test_extract_text_missing_file():
    text, conf = extract_text("nonexistent_file.png")
    assert text == ""
    assert conf == 0.0
