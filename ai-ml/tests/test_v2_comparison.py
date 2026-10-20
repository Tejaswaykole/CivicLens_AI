"""
Unit tests for CivicLens AI Phase 5: V2 Model Comparison, Fixed Group Splitting, and Inference Engine.
"""

from pathlib import Path
import pytest
import pandas as pd

from v2_model_comparison import (
    freeze_v2_group_split,
    build_model_a,
    build_model_b,
    evaluate_pipeline,
    explain_word_char_prediction,
    InferenceEngine,
    run_v2_comparison,
)


@pytest.fixture
def v2_dataset_path() -> Path:
    return Path(__file__).resolve().parent.parent / "data" / "processed" / "synthetic_complaints_v2.csv"


def test_freeze_v2_group_split_zero_overlap(v2_dataset_path: Path):
    df = pd.read_csv(v2_dataset_path)
    train_df, test_df = freeze_v2_group_split(
        df,
        group_col="template_id",
        target_col="category",
        n_test_templates_per_cat=4,
        random_state=42,
    )

    assert len(train_df) + len(test_df) == len(df)
    train_groups = set(train_df["template_id"])
    test_groups = set(test_df["template_id"])
    overlap = train_groups.intersection(test_groups)
    assert len(overlap) == 0, f"Found template overlap: {overlap}"

    # Verify identical split counts
    assert len(train_df) == 222
    assert len(test_df) == 78


def test_model_b_superior_to_model_a(v2_dataset_path: Path):
    df = pd.read_csv(v2_dataset_path)
    train_df, test_df = freeze_v2_group_split(df, random_state=42)

    pipe_a = build_model_a(random_state=42)
    pipe_b = build_model_b(random_state=42)

    res_a = evaluate_pipeline(pipe_a, train_df, test_df)
    res_b = evaluate_pipeline(pipe_b, train_df, test_df)

    assert res_b["accuracy"] > res_a["accuracy"]
    assert res_b["macro_avg"]["f1-score"] > res_a["macro_avg"]["f1-score"]


def test_inference_engine_contract(tmp_path: Path, v2_dataset_path: Path):
    df = pd.read_csv(v2_dataset_path)
    train_df, test_df = freeze_v2_group_split(df, random_state=42)

    pipe_b = build_model_b(random_state=42)
    pipe_b.fit(train_df["complaint_text"], train_df["category"])

    engine = InferenceEngine(model_pipeline=pipe_b)

    # Standard valid complaint
    res = engine.predict("Deep crater pothole on vehicular carriageway.")
    assert res.predicted_category in ["Roads", "Sanitation", "Electricity", "Water Supply", "Public Health"]
    assert res.recommended_department != ""
    assert isinstance(res.requires_human_review, bool)
    assert len(res.top_contributing_features) > 0

    # Safety-critical emergency case
    emergency_res = engine.predict("High voltage live electrical wire snapped and is sparking on street.")
    assert emergency_res.suggested_priority == "High"
    assert emergency_res.requires_human_review is True

    # Empty string handling
    empty_res = engine.predict("")
    assert empty_res.predicted_category == "Unknown"
    assert empty_res.requires_human_review is True
    assert empty_res.confidence is None

    # Unknown tokens handling
    oov_res = engine.predict("zzzz yyyy xxxx wwww")
    assert oov_res.predicted_category in ["Roads", "Sanitation", "Electricity", "Water Supply", "Public Health"]


def test_explain_word_char_prediction(v2_dataset_path: Path):
    df = pd.read_csv(v2_dataset_path)
    train_df, test_df = freeze_v2_group_split(df, random_state=42)

    pipe_b = build_model_b(random_state=42)
    pipe_b.fit(train_df["complaint_text"], train_df["category"])

    cat, conf, feats, stmt = explain_word_char_prediction(pipe_b, "Garbage accumulation on sidewalk")
    assert cat in ["Sanitation", "Roads", "Electricity", "Water Supply", "Public Health"]
    assert len(feats) > 0
    assert any("word:" in f["feature"] or "char:" in f["feature"] for f in feats)


def test_v2_comparison_execution(tmp_path: Path, v2_dataset_path: Path):
    models_dir = tmp_path / "models"
    reports_dir = tmp_path / "reports"

    results = run_v2_comparison(
        dataset_path=v2_dataset_path,
        models_dir=models_dir,
        reports_dir=reports_dir,
        random_state=42,
    )

    assert results["total_records"] == 300
    assert (models_dir / "category_classifier_v2_candidate.joblib").exists()
    assert (models_dir / "category_classifier_v2_metadata.json").exists()
    assert (reports_dir / "model_comparison_v2.md").exists()
