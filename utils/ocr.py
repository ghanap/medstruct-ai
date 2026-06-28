import streamlit as st
import logging
from PIL import Image

logger = logging.getLogger(__name__)

@st.cache_resource(show_spinner=False)
def load_trocr_model():
    """
    Load the TrOCR model and processor once and cache it in memory.
    Using trocr-small-handwritten to balance speed and accuracy.
    """
    logger.info("Loading TrOCR model into memory...")
    try:
        from transformers import TrOCRProcessor, VisionEncoderDecoderModel
        # Load the model (small version for speed)
        processor = TrOCRProcessor.from_pretrained("microsoft/trocr-small-handwritten")
        model = VisionEncoderDecoderModel.from_pretrained("microsoft/trocr-small-handwritten")
        logger.info("TrOCR model loaded successfully.")
        return processor, model
    except ImportError:
        logger.error("transformers or torch not installed. Run: pip install transformers torch torchvision")
        return None, None
    except Exception as e:
        logger.error(f"Failed to load TrOCR: {e}")
        return None, None

def extract_text(image_path_or_file):
    """
    Runs Microsoft TrOCR on the image and returns the raw text and confidence.
    """
    try:
        img = Image.open(image_path_or_file).convert("RGB")
    except Exception as e:
        logger.error(f"Error opening image: {e}")
        return "", 0.0

    processor, model = load_trocr_model()
    if processor is None or model is None:
        return "TROCR_NOT_FOUND_OR_FAILED", 0.0

    try:
        # Generate text from image
        pixel_values = processor(images=img, return_tensors="pt").pixel_values
        generated_ids = model.generate(pixel_values)
        generated_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
        
        # TrOCR doesn't provide a simple confidence score per word easily, 
        # so we assign a baseline confidence of 0.85 if it succeeds.
        confidence = 0.85 if generated_text else 0.0
        return generated_text.strip(), confidence
        
    except Exception as e:
        logger.error(f"TrOCR extraction failed: {e}")
        return f"TROCR_FAILED: {str(e)}", 0.0
