import pytesseract
from PIL import Image, ImageEnhance
import logging
import sys
import os

# Configure Tesseract path for Windows local environments
if sys.platform == "win32":
    tess_path = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    if os.path.exists(tess_path):
        pytesseract.pytesseract.tesseract_cmd = tess_path

logger = logging.getLogger(__name__)

def preprocess_image(image_path_or_file):
    """
    Basic preprocessing: grayscale, contrast enhancement.
    """
    try:
        img = Image.open(image_path_or_file)
        # Convert to grayscale
        img = img.convert('L')
        # Enhance contrast
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.5)
        return img
    except Exception as e:
        logger.error(f"Error preprocessing image: {e}")
        return None

def extract_text(image_path_or_file):
    """
    Runs Tesseract OCR on the image and returns the raw text and confidence.
    """
    img = preprocess_image(image_path_or_file)
    if img is None:
        return "", 0.0

    try:
        # Get raw text
        text = pytesseract.image_to_string(img)
        
        # Get confidence (average of all recognized words)
        data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
        confidences = [int(c) for c in data['conf'] if int(c) != -1]
        
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        
        return text.strip(), round(avg_confidence, 2)
    except Exception as e:
        logger.error(f"Tesseract OCR failed: {e}")
        # Return fallback text for testing if tesseract isn't installed
        return "TESSERACT_NOT_FOUND_OR_FAILED: " + str(e), 0.0
