"""
CivicLens AI — AI Inference Service for Backend Integration.

Provides a cached, failure-resilient wrapper around the AI/ML InferenceEngine.
Handles:
- Safe model loading at startup or on first call.
- Category normalization from AI research taxonomy to backend COMPLAINT_CATEGORIES.
- Priority mapping from AI suggested levels to backend ComplaintPriority enum.
- Emergency term safeguards.
- Clean JSONB explanation formatting.
- Graceful degradation when the model artifact is missing or fails to load.
"""

from __future__ import annotations

import logging
from decimal import Decimal
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import joblib

from app.domain.enums import ComplaintPriority
from app.domain.workflow import COMPLAINT_CATEGORIES

logger = logging.getLogger("civiclens.ai_service")

# Project root resolution: backend/app/services/ai_inference.py -> 3 levels up is repo root
PROJECT_ROOT = Path(__file__).resolve().parents[3]
MODEL_ARTIFACT_PATH = PROJECT_ROOT / "ai-ml" / "models" / "category_classifier_v2_candidate.joblib"

MODEL_IDENTIFIER = "civiclens-category-word-char"
FALLBACK_MODEL_VERSION = "0.2.0-word-char-logreg"

# Explicit mapping from AI research taxonomy (5 categories) to backend COMPLAINT_CATEGORIES
AI_TO_BACKEND_CATEGORY_MAP: Dict[str, str] = {
    "Roads": "Road Infrastructure",
    "Water Supply": "Water & Sewage",
    "Sanitation": "Sanitation & Solid Waste",
    "Electricity": "Electrical Hazard",
    "Public Health": "Public Health",
}

AI_TO_BACKEND_PRIORITY_MAP: Dict[str, ComplaintPriority] = {
    "High": ComplaintPriority.high,
    "Medium": ComplaintPriority.medium,
    "Low": ComplaintPriority.low,
}


@lru_cache(maxsize=1)
def get_cached_pipeline(model_path: Path = MODEL_ARTIFACT_PATH) -> Optional[Any]:
    """
    Load and cache the scikit-learn pipeline artifact once.
    Fails safely if the artifact is missing or corrupted.
    """
    if not model_path.exists():
        logger.warning(
            "AI model artifact not found at %s. AI inference will operate in fallback mode.",
            model_path,
        )
        return None

    try:
        pipeline = joblib.load(model_path)
        logger.info("Successfully loaded AI/ML model pipeline from %s", model_path)
        return pipeline
    except Exception as exc:
        logger.error(
            "Failed to load AI model artifact from %s: %s. Continuing with manual triage fallback.",
            model_path,
            exc,
            exc_info=False,
        )
        return None


def run_complaint_inference(
    title: str,
    description: str,
    model_path: Path = MODEL_ARTIFACT_PATH,
) -> Optional[Dict[str, Any]]:
    """
    Execute AI inference on complaint text.
    Combines title and description per integration contract.
    Returns a dictionary structured for the ModelPrediction SQLAlchemy model,
    or None if the model is unavailable or inference fails.
    """
    raw_text = f"{title.strip()}. {description.strip()}"
    if len(raw_text.strip()) < 5:
        logger.debug("Complaint text too short for AI inference. Skipping.")
        return None

    pipeline = get_cached_pipeline(model_path)
    if pipeline is None:
        return None

    try:
        # Import InferenceEngine dynamically from ai-ml src if not on pythonpath
        try:
            from v2_model_comparison import InferenceEngine
        except ImportError:
            import sys
            ai_src = str(PROJECT_ROOT / "ai-ml" / "src")
            if ai_src not in sys.path:
                sys.path.insert(0, ai_src)
            from v2_model_comparison import InferenceEngine

        engine = InferenceEngine(pipeline)
        result = engine.predict(raw_text)

        # 1. Map predicted category to backend COMPLAINT_CATEGORIES
        backend_category = AI_TO_BACKEND_CATEGORY_MAP.get(result.predicted_category)
        if backend_category not in COMPLAINT_CATEGORIES:
            backend_category = None

        # 2. Map suggested priority to backend ComplaintPriority
        # Check emergency words directly for critical elevation
        lower_text = raw_text.lower()
        critical_indicators = ["snapped live wire", "sparking in water", "sinkhole", "toxic fumes", "poisonous"]
        if any(ind in lower_text for ind in critical_indicators):
            backend_priority = ComplaintPriority.critical
        else:
            backend_priority = AI_TO_BACKEND_PRIORITY_MAP.get(
                result.suggested_priority,
                ComplaintPriority.medium,
            )

        # 3. Format confidence (Decimal 5,4)
        confidence_dec = None
        if result.confidence is not None:
            clamped = max(0.0, min(1.0, float(result.confidence)))
            confidence_dec = Decimal(f"{clamped:.4f}")

        requires_review = bool(result.requires_human_review)

        # 4. Package explanation JSONB
        explanation_payload = {
            "statement": result.explanation_statement,
            "requires_human_review": requires_review,
            "raw_predicted_category": result.predicted_category,
            "recommended_department": result.recommended_department,
            "top_contributing_features": result.top_contributing_features,
            "limitations_notice": (
                "Feature contributions represent linear model weights from an experimental corpus. "
                "Probabilities are uncalibrated decision scores and do not establish real-world certainty."
            ),
        }

        return {
            "model_identifier": MODEL_IDENTIFIER,
            "model_version": result.model_version or FALLBACK_MODEL_VERSION,
            "predicted_category": backend_category,
            "suggested_priority": backend_priority,
            "confidence": confidence_dec,
            "explanation": explanation_payload,
        }

    except Exception as exc:
        logger.error(
            "Unexpected error during AI inference for complaint: %s. Falling back to manual triage.",
            exc,
            exc_info=False,
        )
        return None
