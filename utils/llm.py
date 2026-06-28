import os
import json
import requests
import logging

logger = logging.getLogger(__name__)

OLLAMA_API_URL = "http://localhost:11434/api/generate"
DEFAULT_MODEL = os.getenv("OLLAMA_MODEL", "mistral")

AUTO_DETECT_PROMPT = """
You are an expert medical document analyst. I will give you raw OCR text from a medical document (could be a prescription, lab report, discharge summary, X-ray report, blood test, scan report, etc).

Step 1 — Auto-detect the document type from the text.
Step 2 — Extract ALL relevant information for that document type.
Step 3 — Return a single JSON with these fields:

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


def extract_structured_data(ocr_text: str, model: str = DEFAULT_MODEL):
    """
    Sends OCR text to Ollama. Auto-detects document type and returns rich structured data.
    """
    if not ocr_text or ocr_text.startswith("TESSERACT_NOT_FOUND_OR_FAILED"):
        return {"error": "OCR failed or Tesseract not found."}, model

    # If OCR returned very little text (e.g. X-ray image), still try with what we have
    prompt = AUTO_DETECT_PROMPT.format(ocr_text=ocr_text.strip() or "[No text detected — this may be an imaging scan]")

    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "format": "json",
    }

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
        return {"error": "❌ Cannot connect to Ollama. Make sure Ollama is running (`ollama serve`) and a model is pulled (`ollama pull mistral`)."}, model
    except requests.exceptions.Timeout:
        return {"error": "⏱️ Ollama timed out. The model may still be loading — try again in a moment."}, model
    except requests.exceptions.RequestException as e:
        logger.error(f"Ollama API request failed: {e}")
        return {"error": f"Ollama error: {str(e)}"}, model
