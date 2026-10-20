"""
Unit tests for CivicLens AI Phase 4: Error analysis, human review workflow, and expanded corpus V2.
"""

from pathlib import Path
import pytest
import pandas as pd

from error_analysis import run_error_analysis, diagnose_prediction
from human_review import apply_human_review, export_review_queue
from generate_expanded_corpus import generate_expanded_corpus
from schema import load_and_validate_dataset, validate_dataframe


def test_diagnose_prediction_logic():
    # Correct case
    correct_note = diagnose_prediction("Roads", "Roads", "pothole on road", [{"token": "pothole", "contribution": 0.2}])
    assert "Correctly classified" in correct_note

    # Public Health confused as Sanitation
    ph_san_note = diagnose_prediction(
        "Public Health",
        "Sanitation",
        "Hospital waste dumped in public alley",
        [{"token": "waste", "contribution": 0.3}],
    )
    assert "Sanitation" in ph_san_note
    assert "Analyst Note" in ph_san_note

    # Zero features case
    zero_note = diagnose_prediction("Water Supply", "Roads", "unknown text", [])
    assert "Zero vocabulary overlap" in zero_note


def test_human_review_workflow(tmp_path: Path):
    df = pd.DataFrame([{
        "complaint_id": "TEST-SAN-001",
        "complaint_text": "Dry leaf litter piled on sidewalk corner.",
        "category": "Sanitation",
        "priority": "Low",
        "recommended_department": "Department of Public Services",
        "annotation_rationale": "Dry litter",
        "source_type": "synthetic_template",
        "review_status": "pending_review",
    }])

    # Apply review approval with safety flag
    reviewed_df = apply_human_review(
        df=df,
        complaint_id="TEST-SAN-001",
        reviewer_id="officer_sharma",
        reviewed_category="Sanitation",
        reviewed_priority="Low",
        review_status="officer_approved",
        review_notes="Verified as routine dry leaf litter.",
        is_safety_critical=False,
        is_ambiguous=False,
    )

    assert reviewed_df.loc[0, "reviewer_id"] == "officer_sharma"
    assert reviewed_df.loc[0, "review_status"] == "officer_approved"
    assert reviewed_df.loc[0, "reviewed_category"] == "Sanitation"
    assert reviewed_df.loc[0, "review_notes"] == "Verified as routine dry leaf litter."
    assert reviewed_df.loc[0, "is_safety_critical"] is False

    # Original columns must be preserved
    assert reviewed_df.loc[0, "category"] == "Sanitation"
    assert reviewed_df.loc[0, "priority"] == "Low"

    # Export queue check
    queue_path = tmp_path / "queue.csv"
    export_review_queue(df, queue_path, filter_status="pending_review")
    assert queue_path.exists()
    q_df = pd.read_csv(queue_path)
    assert len(q_df) == 1


def test_human_review_invalid_inputs(tmp_path: Path):
    df = pd.DataFrame([{
        "complaint_id": "TEST-ROA-002",
        "complaint_text": "Pothole crater on street.",
        "category": "Roads",
        "priority": "High",
        "recommended_department": "Public Works",
        "annotation_rationale": "Road defect",
        "source_type": "synthetic_template",
        "review_status": "pending_review",
    }])

    # Invalid ID
    with pytest.raises(ValueError, match="not found"):
        apply_human_review(df, complaint_id="NON_EXISTENT", reviewer_id="officer")

    # Invalid category
    with pytest.raises(ValueError, match="Invalid reviewed_category"):
        apply_human_review(df, complaint_id="TEST-ROA-002", reviewer_id="officer", reviewed_category="BadCategory")

    # Invalid priority
    with pytest.raises(ValueError, match="Invalid reviewed_priority"):
        apply_human_review(df, complaint_id="TEST-ROA-002", reviewer_id="officer", reviewed_priority="CRITICAL")


def test_expanded_corpus_v2_generation_and_validation():
    df_v2 = generate_expanded_corpus(seed=42, samples_per_category=5)
    assert len(df_v2) == 25
    assert set(df_v2["category"].unique()) == {"Sanitation", "Roads", "Electricity", "Water Supply", "Public Health"}
    assert "is_safety_critical" in df_v2.columns
    assert "is_ambiguous" in df_v2.columns

    is_valid, errors = validate_dataframe(df_v2)
    assert is_valid, f"Validation errors: {errors}"


def test_error_analysis_execution(tmp_path: Path):
    dataset_path = Path(__file__).resolve().parent.parent / "data" / "processed" / "synthetic_complaints.csv"
    model_path = Path(__file__).resolve().parent.parent / "models" / "category_classifier_baseline.joblib"

    results = run_error_analysis(
        dataset_path=dataset_path,
        model_path=model_path,
        output_dir=tmp_path,
        random_state=42,
    )

    assert results["total_test_records"] == 38
    assert "model_performance" in results
    assert "majority_baseline_performance" in results
    assert len(results["instance_records"]) == 38
    assert (tmp_path / "error_analysis.md").exists()
    assert (tmp_path / "error_analysis_data.json").exists()
