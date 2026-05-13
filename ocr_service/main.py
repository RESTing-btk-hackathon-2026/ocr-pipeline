"""
OCR Service — 2 Aşamalı Doküman İşleme
  1. Doküman sınıflandırma (Gemini)
  2. Alan çıkarımı (Gemini)
"""

from pathlib import Path

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from config import EXTRACTION_MAP, ALLOWED_EXTENSIONS
import gemini_client

app = FastAPI(title="KOBİ AI — OCR Servisi")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Uzantı → MIME tipi
MIME_TYPES = {
    ".pdf": "application/pdf",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".webp": "image/webp",
    ".tiff": "image/tiff",
    ".bmp": "image/bmp",
}


def get_mime_type(filename):
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, f"Desteklenmeyen dosya türü: {ext}")
    return MIME_TYPES.get(ext, "application/octet-stream")


# ── Endpoint'ler ──────────────────────────────────────


@app.get("/health")
def health():
    return {"status": "ok", "document_types": len(EXTRACTION_MAP)}


@app.get("/document-types")
def document_types():
    """Desteklenen doküman türlerini listele."""
    result = []
    for key, val in EXTRACTION_MAP.items():
        result.append({"key": key, "label": val["label"]})
    return result


@app.post("/classify")
async def classify(file: UploadFile = File(...)):
    """Aşama 1: Dokümanı sınıflandır."""
    mime_type = get_mime_type(file.filename)
    file_bytes = await file.read()

    try:
        result = gemini_client.classify(file_bytes, mime_type)
        return {"success": True, "classification": result}
    except Exception as e:
        raise HTTPException(500, str(e))


@app.post("/extract")
async def extract(file: UploadFile = File(...)):
    """Tam pipeline: Sınıflandır → Alan çıkar."""
    mime_type = get_mime_type(file.filename)
    file_bytes = await file.read()

    try:
        result = gemini_client.process(file_bytes, mime_type)
        return {"success": True, **result}
    except Exception as e:
        raise HTTPException(500, str(e))


@app.post("/extract/{document_type}")
async def extract_with_type(document_type: str, file: UploadFile = File(...)):
    """Aşama 2: Türü bilinen dokümanın alanlarını çıkar."""
    if document_type not in EXTRACTION_MAP:
        raise HTTPException(400, f"Geçersiz doküman türü: {document_type}")

    mime_type = get_mime_type(file.filename)
    file_bytes = await file.read()

    try:
        result = gemini_client.extract(file_bytes, mime_type, document_type)
        return {"success": True, "extraction": result}
    except Exception as e:
        raise HTTPException(500, str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
