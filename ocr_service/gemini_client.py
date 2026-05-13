"""
Gemini ile 2 aşamalı OCR — Sınıflandır → Çıkar
"""

import json
import time

from google import genai
from google.genai import types

from config import GEMINI_API_KEY, GEMINI_MODEL, EXTRACTION_MAP
from prompts import CLASSIFICATION_SYSTEM_PROMPT, EXTRACTION_SYSTEM_PROMPT

# Gemini client
client = genai.Client(api_key=GEMINI_API_KEY)
MODEL = GEMINI_MODEL


def _call_gemini(file_bytes, mime_type, system_prompt, user_text, max_tokens=4096):
    """Gemini'ye dosya + metin gönder, JSON yanıt al."""
    response = client.models.generate_content(
        model=MODEL,
        contents=[
            types.Content(
                role="user",
                parts=[
                    types.Part.from_bytes(data=file_bytes, mime_type=mime_type),
                    types.Part.from_text(text=user_text),
                ],
            )
        ],
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=0.1,
            max_output_tokens=max_tokens,
            response_mime_type="application/json",
        ),
    )
    return json.loads(response.text)


def classify(file_bytes, mime_type):
    """Aşama 1: Dokümanı sınıflandır."""
    # Kategori listesini oluştur
    categories = ""
    for key, val in EXTRACTION_MAP.items():
        categories += f'  - "{key}" → {val["label"]}\n'

    prompt = CLASSIFICATION_SYSTEM_PROMPT.format(category_list=categories)
    return _call_gemini(file_bytes, mime_type, prompt, "Bu dokümanı sınıflandır.", 500)


def extract(file_bytes, mime_type, document_type):
    """Aşama 2: Sınıflandırılmış dokümandan alanları çıkar."""
    doc = EXTRACTION_MAP.get(document_type)
    if not doc:
        raise ValueError(f"Bilinmeyen doküman türü: {document_type}")

    prompt = EXTRACTION_SYSTEM_PROMPT.format(
        document_label=doc["label"],
        document_type=document_type,
        fields_schema=json.dumps(doc["fields"], ensure_ascii=False, indent=2),
        hedef_tablolar=json.dumps(doc.get("hedef_tablolar", []), ensure_ascii=False),
    )
    return _call_gemini(file_bytes, mime_type, prompt, "Bu dokümandan tüm alanları çıkar.")


def process(file_bytes, mime_type):
    """Tam pipeline: Sınıflandır → Çıkar."""
    start = time.time()

    # Aşama 1 — Sınıflandır
    classification = classify(file_bytes, mime_type)
    doc_type = classification.get("document_type", "bilinmeyen")

    # Bilinmeyen tür kontrolü
    if doc_type not in EXTRACTION_MAP:
        return {
            "classification": classification,
            "extraction": None,
            "processing_time_seconds": round(time.time() - start, 2),
        }

    # Aşama 2 — Alan çıkar
    extraction = extract(file_bytes, mime_type, doc_type)

    return {
        "classification": classification,
        "extraction": extraction,
        "processing_time_seconds": round(time.time() - start, 2),
    }
