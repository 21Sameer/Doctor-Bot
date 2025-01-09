import pytesseract
from PIL import Image

def extract_text_from_image(image_path: str) -> str:
    """Extracts text from an image using Tesseract OCR."""
    try:
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img)
        return text.strip()
    except Exception as e:
        print(f"Error processing image: {e}")
        return ""
