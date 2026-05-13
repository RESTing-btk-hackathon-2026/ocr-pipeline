"""
OCR Service Config — .env'den ayarları okur.
"""

import json
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

# Dosya kısıtları
MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "20"))
ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg", ".webp", ".tiff", ".bmp"}

# Extraction map
MAP_PATH = Path(__file__).parent / ".." / "ocr_extraction_map.json"
with open(MAP_PATH.resolve(), "r", encoding="utf-8") as f:
    EXTRACTION_MAP = json.load(f)["ocr_extraction_map"]
