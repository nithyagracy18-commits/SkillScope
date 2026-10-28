"""Configuration for the resume text extraction prototype."""
from pathlib import Path

# If Tesseract is installed but not on PATH, uncomment and edit this:
# TESSERACT_CMD = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
TESSERACT_CMD = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# PDF pages with fewer characters than this threshold are treated as likely scanned.
PDF_TEXT_MIN_CHARS = 30

# Resolution used to render scanned PDF pages before OCR.
PDF_RENDER_DPI = 250

SUPPORTED_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp", ".webp"}
