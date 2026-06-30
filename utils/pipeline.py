import logging
from utils.ocr import extract_text
from utils.llm import triage_image, extract_xray_data, extract_document_data
from utils.database import save_prescription

logger = logging.getLogger(__name__)

def run_pipeline(image_path_or_file, doc_type="auto", save_to_db=True):
    """
    Runs the Two-Pass extraction pipeline.
    """
    result = {
        "ocr_text": "",
        "ocr_confidence": 0.0,
        "extracted": {},
        "error": None,
        "rx_id": None,
        "llm_model": None
    }

    # Reset stream pointer
    if hasattr(image_path_or_file, 'seek'):
        try:
            image_path_or_file.seek(0)
        except Exception:
            pass

    # 1. Triage Phase
    detected_type = "document"
    if image_path_or_file:
        detected_type = triage_image(image_path_or_file)

        # Reset stream pointer again for next steps
        if hasattr(image_path_or_file, 'seek'):
            try:
                image_path_or_file.seek(0)
            except Exception:
                pass

    logger.info(f"Triage Result: {detected_type}")

    # 2. Routing Phase
    if detected_type == "xray":
        logger.info("Skipping OCR for X-Ray...")
        structured_data, model = extract_xray_data(image_path_or_file)
        result["llm_model"] = model
    else:
        logger.info("Running standard document pipeline with OCR...")
        text, confidence = extract_text(image_path_or_file)
        result["ocr_text"] = text
        result["ocr_confidence"] = confidence

        if text.startswith("TESSERACT_NOT_FOUND_OR_FAILED") or text.startswith("TROCR_"):
            logger.warning("OCR engine failed or was not found.")
            text = ""

        if hasattr(image_path_or_file, 'seek'):
            try:
                image_path_or_file.seek(0)
            except Exception:
                pass

        structured_data, model = extract_document_data(text, image_path_or_file)
        result["llm_model"] = model

    # 3. Post-Processing & DB
    if "error" in structured_data:
        result["error"] = structured_data["error"]
        result["extracted"] = structured_data
    else:
        result["extracted"] = structured_data

    if save_to_db:
        try:
            rx_id = save_prescription(result)
            result["rx_id"] = rx_id
        except Exception as e:
            logger.error(f"Failed to save to database: {e}")
            result["error"] = f"Database error: {e}"

    return result
