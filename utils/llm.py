import os
import json
import requests
import logging
import base64

logger = logging.getLogger(__name__)

OLLAMA_API_URL = "http://127.0.0.1:11434/api/generate"
DEFAULT_MODEL = os.getenv("OLLAMA_MODEL", "mistral")

TRIAGE_PROMPT = """
Look at the image provided.
Is this an X-Ray of a bone/joint, or a Medical Document (like a prescription)?
If it is an X-Ray, reply ONLY with the exact word: xray
If it is a Document with text, reply ONLY with the exact word: document
"""

XRAY_PROMPT = """
You are an expert radiologist. Analyze this medical image.
Carefully check if there are any breaks, fractures, or abnormalities in the bones.
Return a single JSON with these exact fields:
{
  "document_type": "xray_report",
  "summary": "A 2-3 sentence plain-English summary of what this X-ray shows and if any breaks/fractures are present.",
  "diagnosis": "Main diagnosis or finding (e.g. Ankle fracture, Normal foot) or null",
  "imaging_findings": "Detailed description of the bones and whether any breaks or fractures are visible."
}
IMPORTANT: Return ONLY the JSON. No markdown, no extra text.
"""

DOCUMENT_PROMPT = """
You are an expert medical analyst. Extract information from this document.
DO NOT GUESS OR HALLUCINATE. If you cannot read handwriting with 100% certainty, DO NOT guess medication names. Output null instead.
Return a single JSON with these fields:
{
  "document_type": "One of: prescription / lab_report / discharge_summary / blood_test / other",
  "summary": "A 2-3 sentence plain-English summary of what this document says.",
  "patient": {
    "name": "Patient Name or null",
    "age": "Age or null",
    "gender": "Gender or null"
  },
  "doctor": {
    "name": "Doctor Name or null",
    "qualification": "Qualifications or null",
    "hospital": "Hospital/Clinic or null"
  },
  "diagnosis": "Main diagnosis or null",
  "medications": [
    {
      "drug_name": "Drug name",
      "dosage": "e.g. 500mg",
      "frequency": "e.g. twice daily",
      "duration": "e.g. 5 days",
      "instructions": "e.g. after meals"
    }
  ],
  "lab_results": [
    {
      "test_name": "Test name",
      "value": "Result value",
      "unit": "Unit",
      "reference_range": "Normal range",
      "status": "Normal / High / Low"
    }
  ],
  "key_concerns": ["List any critical values or urgent findings"],
  "notes": "Any other important clinical notes or null"
}
IMPORTANT: Return ONLY the JSON. No markdown, no extra text. If a field doesn't apply, set it to null or [].

Raw OCR Text:
{ocr_text}
"""

def triage_image(image_file):
    """
    Passes ONLY the image to LLaVA to ask if it's an X-Ray or a Document.
    Returns 'xray' or 'document'.
    """
    image_bytes = image_file.getvalue() if hasattr(image_file, 'getvalue') else open(image_file, "rb").read()
    payload = {
        "model": "llava",
        "prompt": TRIAGE_PROMPT,
        "images": [base64.b64encode(image_bytes).decode("utf-8")],
        "stream": False,
    }
    logger.info("Running Triage Phase on image...")
    try:
        response = requests.post(OLLAMA_API_URL, json=payload, timeout=60)
        response.raise_for_status()
        res_text = response.json().get("response", "").strip().lower()
        if "xray" in res_text or "x-ray" in res_text or "bone" in res_text:
            return "xray"
        return "document"
    except Exception as e:
        logger.error(f"Triage failed: {e}")
        return "document" # fallback

def _run_llm_json(payload, model):
    try:
        response = requests.post(OLLAMA_API_URL, json=payload, timeout=120)
        response.raise_for_status()
        result = response.json()
        response_text = result.get("response", "")
        
        try:
            structured_data = json.loads(response_text)
            return structured_data, model
        except json.JSONDecodeError:
            if "```json" in response_text:
                cleaned = response_text.split("```json")[1].split("```")[0].strip()
                return json.loads(cleaned), model
            logger.error("Failed to parse LLM response as JSON")
            return {"error": "Ollama did not return valid JSON.", "raw_response": response_text}, model
            
    except requests.exceptions.ConnectionError:
        return {"error": f"❌ Cannot connect to Ollama at {OLLAMA_API_URL}."}, model
    except requests.exceptions.Timeout:
        return {"error": "⏱️ Ollama timed out. The model may still be loading — try again in a moment."}, model
    except requests.exceptions.RequestException as e:
        logger.error(f"Ollama API request failed: {e}")
        return {"error": f"Ollama error: {str(e)}"}, model

def extract_xray_data(image_file):
    image_bytes = image_file.getvalue() if hasattr(image_file, 'getvalue') else open(image_file, "rb").read()
    payload = {
        "model": "llava",
        "prompt": XRAY_PROMPT,
        "images": [base64.b64encode(image_bytes).decode("utf-8")],
        "stream": False,
        "format": "json"
    }
    logger.info("Running X-Ray Extraction Phase...")
    return _run_llm_json(payload, "llava")

def extract_document_data(ocr_text: str, image_file=None, model: str = DEFAULT_MODEL):
    if (not ocr_text or ocr_text.startswith("TESSERACT_NOT_FOUND_OR_FAILED") or ocr_text.startswith("TROCR_")) and not image_file:
        return {"error": "No text or image provided."}, model

    payload = {
        "model": model,
        "prompt": DOCUMENT_PROMPT.format(ocr_text=ocr_text.strip() or "[No readable text detected]"),
        "stream": False,
        "format": "json",
    }

    if image_file:
        try:
            image_bytes = image_file.getvalue() if hasattr(image_file, 'getvalue') else open(image_file, "rb").read()
            payload["images"] = [base64.b64encode(image_bytes).decode("utf-8")]
            model = "llava"
            payload["model"] = model
            logger.info("Image detected for Document. Using LLaVA.")
        except Exception as e:
            logger.error(f"Failed to encode image for Vision API: {e}")

    logger.info("Running Document Extraction Phase...")
    return _run_llm_json(payload, model)
