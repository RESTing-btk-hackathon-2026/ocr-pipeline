"""
Pydantic Schemas
~~~~~~~~~~~~~~~~
API request/response modelleri.
"""

from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field


# ── Classification (Aşama 1) ────────────────────────────────

class ClassificationResult(BaseModel):
    """Doküman sınıflandırma sonucu."""
    document_type: str = Field(..., description="Extraction map'teki kategori anahtarı")
    document_label: str = Field(..., description="İnsan-okunabilir etiket")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Güven skoru")
    reasoning: str = Field("", description="Sınıflandırma gerekçesi")


# ── Extraction (Aşama 2) ────────────────────────────────────

class ExtractionResult(BaseModel):
    """Alan çıkarım sonucu."""
    document_type: str
    document_label: str
    hedef_tablolar: list[str] = Field(default_factory=list)
    extracted_data: dict[str, Any] = Field(default_factory=dict)


# ── Full Pipeline ────────────────────────────────────────────

class OCRPipelineResponse(BaseModel):
    """2 aşamalı pipeline'ın tam yanıtı."""
    success: bool = True
    classification: ClassificationResult
    extraction: ExtractionResult
    processing_time_seconds: float = Field(0.0, description="Toplam işlem süresi")


class OCRErrorResponse(BaseModel):
    """Hata yanıtı."""
    success: bool = False
    error: str
    detail: Optional[str] = None


# ── Sadece Sınıflandırma endpoint'i için ─────────────────────

class ClassifyOnlyResponse(BaseModel):
    """Sadece sınıflandırma sonucu."""
    success: bool = True
    classification: ClassificationResult
    available_fields: dict[str, Any] = Field(
        default_factory=dict,
        description="Bu doküman türü için çıkarılabilecek alanlar"
    )
