import os
import json
import requests
import logging
import base64

logger = logging.getLogger(__name__)

OLLAMA_API_URL = "http://127.0.0.1:11434/api/generate"
DEFAULT_MODEL = os.getenv("OLLAMA_MODEL", "mistral")

AUTO_DETECT_PROMPT = """
You are an expert medical analyst. I will provide raw OCR text AND/OR a medical image (such as an X-Ray, MRI, or scan).

CRITICAL INSTRUCTION 1: Look at the IMAGE FIRST to determine the document type. If you see bones, joints, or organs, it is an `xray_report` or `scan_report`. Do NOT classify an X-Ray as a prescription just because the OCR text is messy.
CRITICAL INSTRUCTION 2: If the image is a medical scan/X-ray, IGNORE the OCR text entirely if it seems nonsensical, as OCR models hallucinate on bones. Describe the bones and fractures directly in `imaging_findings`.
CRITICAL INSTRUCTION 3: DO NOT GUESS OR HALLUCINATE. If the document is a prescription with cursive handwriting that you cannot read with certainty, DO NOT guess medication names. Output null instead.
Step 1 — Auto-detect the document type (e.g. Xray Report, Prescription).
Step 2 — Extract ALL relevant information (if it's an X-Ray, describe the bones, joints, and any visible fractures or abnormalities in `imaging_findings`).
Step 3 — Return a single JSON with these fields (use null for fields you cannot find):

{{
  "document_type": "One of: prescription / lab_report / discharge_summary / xray_report / scan_report / blood_test / other",
  "summary": "A 2-3 sentence plain-English summary of what this document says and what it means for the patient.",
  "patient": {{
    "name": "Patient Name or null",
    "age": "Age or null",
    "gender": "Gender or null"
  }},
  "doctor": {{
    "name": "Doctor Name or null",
    "qualification": "Qualifications or null",
    "hospital": "Hospital/Clinic or null"
  }},
  "diagnosis": "Main diagnosis, finding, or chief complaint — or null",
  "medications": [
    {{
      "drug_name": "Drug name",
      "dosage": "e.g. 500mg",
      "frequency": "e.g. twice daily",
      "duration": "e.g. 5 days",
      "instructions": "e.g. after meals"
    }}
  ],
  "lab_results": [
    {{
      "test_name": "Test name",
      "value": "Result value",
      "unit": "Unit",
      "reference_range": "Normal range",
      "status": "Normal / High / Low"
    }}
  ],
  "imaging_findings": "For X-rays/scans: describe what is visible and any abnormalities found, or null",
  "key_concerns": ["List any critical values, urgent findings, or things the patient should act on"],
  "notes": "Any other important clinical notes or null"
}}

IMPORTANT: Return ONLY the JSON. No markdown, no extra text. If a field doesn't apply, set it to null or [].

Raw OCR Text:
{ocr_text}
"""


def extract_structured_data(ocr_text: str, image_file=None, model: str = DEFAULT_MODEL):
    """
    Sends OCR text (and optional image) to Ollama.
    """
    if (not ocr_text or ocr_text.startswith("TESSERACT_NOT_FOUND_OR_FAILED")) and not image_file:
        return {"error": "No text or image provided."}, model

    payload = {
        "model": model,
        "prompt": AUTO_DETECT_PROMPT.format(ocr_text=ocr_text.strip() or "[No text detected]"),
        "stream": False,
        "format": "json",
    }

    if image_file:
        try:
            image_bytes = image_file.getvalue() if hasattr(image_file, 'getvalue') else open(image_file, "rb").read()
            payload["images"] = [base64.b64encode(image_bytes).decode("utf-8")]
            model = "llama3.2-vision"
            payload["model"] = model
            logger.info("Image detected. Switching Ollama model to Llama 3.2 Vision for analysis.")
        except Exception as e:
            logger.error(f"Failed to encode image for Vision API: {e}")

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
        return {"error": f"❌ Cannot connect to Ollama at {OLLAMA_API_URL}. If you are on Streamlit Cloud, it cannot access your computer's local Ollama. Please use the local app (http://localhost:8501)."}, model
    except requests.exceptions.Timeout:
        return {"error": "⏱️ Ollama timed out. The model may still be loading — try again in a moment."}, model
    except requests.exceptions.RequestException as e:
        logger.error(f"Ollama API request failed: {e}")
        return {"error": f"Ollama error: {str(e)}"}, model
