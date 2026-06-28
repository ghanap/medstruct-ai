import logging
from utils.ocr import extract_text
from utils.llm import extract_structured_data
from utils.database import save_prescription

logger = logging.getLogger(__name__)

def run_pipeline(image_path_or_file, doc_type="Prescription", save_to_db=True):
    """
    Runs the full extraction pipeline: Image -> OCR -> LLM -> DB.
    """
    result = {
        "ocr_text": "",
        "ocr_confidence": 0.0,
        "extracted": {},
        "error": None,
        "rx_id": None,
        "llm_model": None
    }
    
    # 1. OCR
    text, confidence = extract_text(image_path_or_file)
    result["ocr_text"] = text
    result["ocr_confidence"] = confidence
    
    if text.startswith("TESSERACT_NOT_FOUND_OR_FAILED"):
        logger.warning("Tesseract failed. Continuing with Vision AI if possible.")
        text = ""
        
    # 2. LLM Extraction
    structured_data, model = extract_structured_data(text, image_path_or_file)
    result["llm_model"] = model
    
    if "error" in structured_data:
        result["error"] = structured_data["error"]
        result["extracted"] = structured_data
        # Still save it if we want to log the error
    else:
        result["extracted"] = structured_data
        
    # 3. Database
    if save_to_db:
        try:
            rx_id = save_prescription(result)
            result["rx_id"] = rx_id
        except Exception as e:
            logger.error(f"Failed to save to database: {e}")
            result["error"] = f"Database error: {e}"
            
    return result
