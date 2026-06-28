import os
import json
import requests
import logging

logger = logging.getLogger(__name__)

OLLAMA_API_URL = "http://localhost:11434/api/generate"
DEFAULT_MODEL = os.getenv("OLLAMA_MODEL", "tinyllama:latest")

EXTRACTION_PROMPT = """
You are a medical data extraction assistant. I will provide you with raw OCR text from a medical document (like a prescription or lab report).
Your task is to extract the relevant information and return it as a STRICT JSON object.

The JSON should have the following structure:
{{
  "patient": {{
    "name": "Patient Name",
    "age": "Age if present",
    "gender": "Gender if present"
  }},
  "doctor": {{
    "name": "Doctor Name",
    "qualification": "Qualifications if present",
    "hospital": "Hospital or Clinic name if present"
  }},
  "diagnosis": "Main diagnosis or chief complaint",
  "medications": [
    {{
      "drug_name": "Name of the drug",
      "dosage": "e.g., 500mg",
      "frequency": "e.g., 1-0-1 or twice a day",
      "duration": "e.g., 5 days",
      "instructions": "e.g., after meals"
    }}
  ],
  "lab_results": [
    {{
      "test_name": "Name of the test",
      "value": "Result value",
      "unit": "Measurement unit",
      "reference_range": "Normal range"
    }}
  ],
  "notes": "Any other important clinical notes"
}}

If a field is not found in the text, omit it or set it to null. Do not include markdown formatting or any text outside of the JSON block.

Raw OCR Text:
{ocr_text}
"""

def extract_structured_data(ocr_text, model=DEFAULT_MODEL):
    """
    Sends the OCR text to Ollama and attempts to parse the returned JSON.
    """
    if not ocr_text or ocr_text.startswith("TESSERACT_NOT_FOUND_OR_FAILED"):
        return {"error": "OCR failed, cannot extract data."}, DEFAULT_MODEL

    prompt = EXTRACTION_PROMPT.format(ocr_text=ocr_text)
    
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "format": "json"  # Forces JSON output if supported by the model
    }
    
    try:
        response = requests.post(OLLAMA_API_URL, json=payload, timeout=60)
        response.raise_for_status()
        
        result = response.json()
        response_text = result.get("response", "")
        
        # Parse the JSON
        try:
            structured_data = json.loads(response_text)
            return structured_data, model
        except json.JSONDecodeError:
            # Fallback if it wrapped in markdown
            if "```json" in response_text:
                cleaned = response_text.split("```json")[1].split("```")[0].strip()
                return json.loads(cleaned), model
            
            logger.error("Failed to parse LLM response as JSON")
            return {"error": "LLM did not return valid JSON.", "raw_response": response_text}, model
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Ollama API request failed: {e}")
        return {"error": f"Failed to connect to Ollama. Is it running? ({str(e)})"}, model
