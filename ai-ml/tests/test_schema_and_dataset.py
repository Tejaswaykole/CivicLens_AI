"""
Unit tests for CivicLens AI dataset schema, validation, and synthetic generation.
"""

from pathlib import Path
import pytest
import pandas as pd

from schema import (
    REQUIRED_COLUMNS,
    VALID_CATEGORIES,
    VALID_PRIORITIES,
    validate_complaint_record,
    validate_dataframe,
    load_and_validate_dataset,
)
from generate_synthetic_data import generate_synthetic_corpus


def test_schema_required_columns():
    assert "complaint_id" in REQUIRED_COLUMNS
    assert "complaint_text" in REQUIRED_COLUMNS
    assert "category" in REQUIRED_COLUMNS
    assert "priority" in REQUIRED_COLUMNS
    assert "recommended_department" in REQUIRED_COLUMNS
    assert "annotation_rationale" in REQUIRED_COLUMNS
    assert "source_type" in REQUIRED_COLUMNS
    assert "review_status" in REQUIRED_COLUMNS


def test_record_validation_success():
    valid_record = {
        "complaint_id": "SYN-ROA-00001",
        "complaint_text": "Massive pothole on Main Road causing accidents.",
        "category": "Roads",
        "priority": "High",
        "recommended_department": "Department of Public Works",
        "annotation_rationale": "High-risk roadway defect",
        "source_type": "synthetic_template",
        "review_status": "pending_review",
    }
    errors = validate_complaint_record(valid_record, row_idx=0)
    assert len(errors) == 0


def test_record_validation_invalid_category():
    invalid_record = {
        "complaint_id": "SYN-ROA-00002",
        "complaint_text": "Broken lamp post on the sidewalk.",
        "category": "Telecommunications",  # Not in VALID_CATEGORIES
        "priority": "Low",
        "recommended_department": "Public Works",
        "annotation_rationale": "Aesthetic defect",
        "source_type": "synthetic_template",
        "review_status": "pending_review",
    }
    errors = validate_complaint_record(invalid_record, row_idx=1)
    assert any(e.column == "category" for e in errors)


def test_record_validation_invalid_priority():
    invalid_record = {
        "complaint_id": "SYN-ROA-00003",
        "complaint_text": "Live wire sparking in public waterlogged street.",
        "category": "Electricity",
        "priority": "CRITICAL",  # Must be Low, Medium, or High
        "recommended_department": "Electricity Board",
        "annotation_rationale": "Severe safety risk",
        "source_type": "synthetic_template",
        "review_status": "pending_review",
    }
    errors = validate_complaint_record(invalid_record, row_idx=2)
    assert any(e.column == "priority" for e in errors)


def test_dataframe_validation_empty_text():
    df = pd.DataFrame([{
        "complaint_id": "SYN-SAN-00004",
        "complaint_text": "   ",  # Empty/whitespace
        "category": "Sanitation",
        "priority": "Medium",
        "recommended_department": "Public Services",
        "annotation_rationale": "Uncollected trash",
        "source_type": "synthetic_template",
        "review_status": "pending_review",
    }])
    is_valid, errors = validate_dataframe(df)
    assert not is_valid
    assert any(e.column == "complaint_text" for e in errors)


def test_dataframe_validation_duplicate_ids():
    df = pd.DataFrame([
        {
            "complaint_id": "SYN-WAT-00005",
            "complaint_text": "Water pipeline burst causing street flooding.",
            "category": "Water Supply",
            "priority": "High",
            "recommended_department": "Water Works",
            "annotation_rationale": "Pipe burst",
            "source_type": "synthetic_template",
            "review_status": "pending_review",
        },
        {
            "complaint_id": "SYN-WAT-00005",  # Duplicate ID
            "complaint_text": "Low water pressure on 2nd floor taps.",
            "category": "Water Supply",
            "priority": "Medium",
            "recommended_department": "Water Works",
            "annotation_rationale": "Low pressure",
            "source_type": "synthetic_template",
            "review_status": "pending_review",
        },
    ])
    is_valid, errors = validate_dataframe(df)
    assert not is_valid
    assert any("duplicate complaint_id" in str(e) for e in errors)


def test_synthetic_corpus_generation_reproducibility():
    df1 = generate_synthetic_corpus(seed=42, samples_per_category=5)
    df2 = generate_synthetic_corpus(seed=42, samples_per_category=5)
    pd.testing.assert_frame_equal(df1, df2)

    is_valid, errors = validate_dataframe(df1)
    assert is_valid
    assert len(df1) == 25
    assert set(df1["category"].unique()) == VALID_CATEGORIES
    assert set(df1["priority"].unique()).issubset(VALID_PRIORITIES)


def test_processed_synthetic_dataset_on_disk():
    dataset_path = Path(__file__).resolve().parent.parent / "data" / "processed" / "synthetic_complaints.csv"
    assert dataset_path.exists(), f"Expected synthetic dataset at {dataset_path}"
    df, errors = load_and_validate_dataset(dataset_path)
    assert len(errors) == 0
    assert len(df) == 150
