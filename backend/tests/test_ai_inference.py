"""
Unit tests for backend AI/ML inference service integration.
Verifies:
- Inference result structure and mapping to backend enums.
- Category normalization from research categories to COMPLAINT_CATEGORIES.
- Priority mapping and critical emergency elevation.
- Safe handling of missing/corrupt model artifact.
- Safe handling of empty or sub-minimum text.
- Fallback behavior without throwing unhandled exceptions.
- ModelPrediction model compatibility.
"""

import uuid
from decimal import Decimal
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from app.domain.enums import ComplaintPriority
from app.domain.workflow import COMPLAINT_CATEGORIES
from app.models.model_prediction import ModelPrediction
from app.services.ai_inference import (
    AI_TO_BACKEND_CATEGORY_MAP,
    AI_TO_BACKEND_PRIORITY_MAP,
    MODEL_IDENTIFIER,
    get_cached_pipeline,
    run_complaint_inference,
)


def test_ai_category_mappings_valid():
    """Verify all mapped backend categories are within COMPLAINT_CATEGORIES."""
    for ai_cat, backend_cat in AI_TO_BACKEND_CATEGORY_MAP.items():
        assert backend_cat in COMPLAINT_CATEGORIES, f"Mapped category '{backend_cat}' is not in COMPLAINT_CATEGORIES"


def test_run_complaint_inference_success():
    """Verify normal inference execution on valid complaint text."""
    title = "Broken street water pipe"
    desc = "Clean water is gushing out on the road from a fractured underground pipeline."

    res = run_complaint_inference(title, desc)
    assert res is not None
    assert res["model_identifier"] == MODEL_IDENTIFIER
    assert isinstance(res["model_version"], str)
    assert res["predicted_category"] in COMPLAINT_CATEGORIES
    assert isinstance(res["suggested_priority"], ComplaintPriority)
    assert res["confidence"] is None or isinstance(res["confidence"], Decimal)
    assert "explanation" in res
    assert "statement" in res["explanation"]
    assert "top_contributing_features" in res["explanation"]


def test_emergency_term_detection_elevates_to_critical():
    """Verify life-safety emergency keywords elevate suggested_priority to critical."""
    title = "High voltage wire snapped"
    desc = "Live snapped live wire sparking in water right near bus stop."

    res = run_complaint_inference(title, desc)
    assert res is not None
    assert res["suggested_priority"] == ComplaintPriority.critical
    assert res["explanation"]["requires_human_review"] is True


def test_short_or_empty_text_returns_none():
    """Verify sub-5-character complaints return None cleanly without failing."""
    assert run_complaint_inference("", "") is None
    assert run_complaint_inference("a", "b") is None


def test_missing_model_artifact_falls_back_safely(tmp_path: Path):
    """Verify non-existent artifact path returns None and logs warning without crash."""
    non_existent = tmp_path / "does_not_exist.joblib"
    res = run_complaint_inference("Some title", "Some description with sufficient characters", model_path=non_existent)
    assert res is None


def test_model_prediction_orm_instantiation():
    """Verify ModelPrediction SQLAlchemy row can be constructed from inference output."""
    res = run_complaint_inference("Street lamp dark", "Streetlight not turning on at night causing blackout.")
    assert res is not None

    complaint_id = uuid.uuid4()
    prediction = ModelPrediction(
        complaint_id=complaint_id,
        model_identifier=res["model_identifier"],
        model_version=res["model_version"],
        predicted_category=res["predicted_category"],
        suggested_priority=res["suggested_priority"],
        confidence=res["confidence"],
        explanation=res["explanation"],
    )

    assert prediction.complaint_id == complaint_id
    assert prediction.model_identifier == MODEL_IDENTIFIER
    assert prediction.predicted_category in COMPLAINT_CATEGORIES
    assert isinstance(prediction.suggested_priority, ComplaintPriority)


def test_public_health_direct_mapping_and_explanation():
    """Verify Public Health predictions map directly to Public Health without proxying."""
    with patch("app.services.ai_inference.get_cached_pipeline") as mock_pipeline:
        mock_engine = MagicMock()
        mock_result = MagicMock()
        mock_result.predicted_category = "Public Health"
        mock_result.suggested_priority = "Medium"
        mock_result.confidence = 0.85
        mock_result.requires_human_review = False
        mock_result.explanation_statement = "Model detected stagnant water vector hazard."
        mock_result.recommended_department = "Public Health & Vector Control"
        mock_result.top_contributing_features = [("stagnant", 1.2), ("mosquitoes", 1.0)]
        mock_result.model_version = "0.2.0-test"
        mock_engine.return_value.predict.return_value = mock_result

        with patch("v2_model_comparison.InferenceEngine", mock_engine):
            res = run_complaint_inference(
                "Stagnant water breeding mosquitoes",
                "Large puddle of dirty stagnant water breeding mosquitoes near public park.",
            )

    assert res is not None
    assert res["predicted_category"] == "Public Health"
    assert res["predicted_category"] in COMPLAINT_CATEGORIES
    assert "public_health_proxy_notice" not in res["explanation"]


def test_inference_exception_returns_none_and_logs(caplog):
    """Verify unexpected inference engine exceptions return None without raising."""
    with patch("app.services.ai_inference.get_cached_pipeline") as mock_pipeline:
        mock_engine = MagicMock()
        mock_engine.return_value.predict.side_effect = RuntimeError("Simulated runtime inference failure")

        with patch("v2_model_comparison.InferenceEngine", mock_engine):
            res = run_complaint_inference("Valid title", "Valid description that meets minimum length threshold.")

    assert res is None

