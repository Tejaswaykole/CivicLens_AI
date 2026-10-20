"""
CivicLens AI — Dataset Schema and Validation Module.

Defines controlled vocabularies, column constraints, and validation rules
for grievance complaint datasets to prevent label leakage and corruption.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Sequence, Set, Tuple

import pandas as pd

# Controlled Vocabularies
VALID_CATEGORIES: Set[str] = {
    "Sanitation",
    "Roads",
    "Electricity",
    "Water Supply",
    "Public Health",
}

VALID_PRIORITIES: Set[str] = {
    "Low",
    "Medium",
    "High",
}

VALID_SOURCE_TYPES: Set[str] = {
    "synthetic_template",
    "synthetic_template_v2",
    "synthetic_llm_augmented",
    "cincinnati_311_adapted",
    "citizen_field_annotated",
    "curated_benchmark",
}

VALID_REVIEW_STATUSES: Set[str] = {
    "pending_review",
    "officer_approved",
    "expert_validated",
    "rejected",
}

CATEGORY_DEPARTMENT_MAPPING: Dict[str, str] = {
    "Sanitation": "Department of Public Services",
    "Roads": "Department of Public Works",
    "Electricity": "Electricity Distribution Board",
    "Water Supply": "Municipal Water Works",
    "Public Health": "Department of Public Health",
}

REQUIRED_COLUMNS: Sequence[str] = (
    "complaint_id",
    "complaint_text",
    "category",
    "priority",
    "recommended_department",
    "annotation_rationale",
    "source_type",
    "review_status",
)

OPTIONAL_COLUMNS: Sequence[str] = (
    "template_id",
    "reviewed_category",
    "reviewed_priority",
    "review_notes",
    "is_safety_critical",
    "is_ambiguous",
    "reviewer_id",
)


@dataclass(frozen=True)
class ValidationError:
    row_index: int | None
    column: str
    error_message: str

    def __str__(self) -> str:
        row_str = f"Row {self.row_index}" if self.row_index is not None else "Dataset Level"
        return f"[{row_str}] Column '{self.column}': {self.error_message}"


def validate_complaint_record(record: Dict[str, Any], row_idx: int) -> List[ValidationError]:
    """Validate a single grievance record dictionary against schema rules."""
    errors: List[ValidationError] = []

    # 1. complaint_id
    cid = record.get("complaint_id")
    if not cid or not isinstance(cid, str) or not cid.strip():
        errors.append(ValidationError(row_idx, "complaint_id", "Missing or empty complaint_id"))

    # 2. complaint_text
    text = record.get("complaint_text")
    if not text or not isinstance(text, str) or len(text.strip()) < 10:
        errors.append(
            ValidationError(
                row_idx,
                "complaint_text",
                f"Complaint text must be a string with at least 10 characters (got: {text!r})",
            )
        )

    # 3. category
    cat = record.get("category")
    if cat not in VALID_CATEGORIES:
        errors.append(
            ValidationError(
                row_idx,
                "category",
                f"Invalid category '{cat}'. Must be one of: {sorted(VALID_CATEGORIES)}",
            )
        )

    # 4. priority
    prio = record.get("priority")
    if prio not in VALID_PRIORITIES:
        errors.append(
            ValidationError(
                row_idx,
                "priority",
                f"Invalid priority '{prio}'. Must be one of: {sorted(VALID_PRIORITIES)}",
            )
        )

    # 5. recommended_department
    dept = record.get("recommended_department")
    if not dept or not isinstance(dept, str) or not dept.strip():
        errors.append(ValidationError(row_idx, "recommended_department", "Missing department"))

    # 6. annotation_rationale
    rationale = record.get("annotation_rationale")
    if not rationale or not isinstance(rationale, str) or not rationale.strip():
        errors.append(ValidationError(row_idx, "annotation_rationale", "Missing annotation_rationale"))

    # 7. source_type
    src = record.get("source_type")
    if src not in VALID_SOURCE_TYPES:
        errors.append(
            ValidationError(
                row_idx,
                "source_type",
                f"Invalid source_type '{src}'. Must be one of: {sorted(VALID_SOURCE_TYPES)}",
            )
        )

    # 8. review_status
    status = record.get("review_status")
    if status not in VALID_REVIEW_STATUSES:
        errors.append(
            ValidationError(
                row_idx,
                "review_status",
                f"Invalid review_status '{status}'. Must be one of: {sorted(VALID_REVIEW_STATUSES)}",
            )
        )

    return errors


def validate_dataframe(df: pd.DataFrame) -> Tuple[bool, List[ValidationError]]:
    """Validate an entire pandas DataFrame against the CivicLens schema."""
    errors: List[ValidationError] = []

    # Column presence check
    for col in REQUIRED_COLUMNS:
        if col not in df.columns:
            errors.append(ValidationError(None, col, f"Missing required column in dataset schema"))

    if errors:
        return False, errors

    # Check for empty dataset
    if df.empty:
        errors.append(ValidationError(None, "dataset", "Dataset contains 0 rows"))
        return False, errors

    # Check for duplicate complaint_ids
    duplicate_ids = df[df["complaint_id"].duplicated(keep=False)]["complaint_id"].unique()
    if len(duplicate_ids) > 0:
        errors.append(
            ValidationError(
                None,
                "complaint_id",
                f"Found {len(duplicate_ids)} duplicate complaint_id values: {duplicate_ids[:5]}",
            )
        )

    # Check for exact duplicate complaint_texts
    duplicate_texts = df[df["complaint_text"].duplicated(keep=False)]["complaint_text"].unique()
    if len(duplicate_texts) > 0:
        errors.append(
            ValidationError(
                None,
                "complaint_text",
                f"Found {len(duplicate_texts)} duplicate complaint_text values",
            )
        )

    # Row-level validations
    for row_idx, row in df.iterrows():
        rec_errors = validate_complaint_record(row.to_dict(), int(row_idx))
        errors.extend(rec_errors)

    return len(errors) == 0, errors


def load_and_validate_dataset(filepath: Path | str) -> Tuple[pd.DataFrame, List[ValidationError]]:
    """Load a CSV file and return the DataFrame and validation errors list."""
    path = Path(filepath)
    if not path.exists():
        return pd.DataFrame(), [ValidationError(None, "file", f"File does not exist: {path}")]

    df = pd.read_csv(path)
    is_valid, errors = validate_dataframe(df)
    return df, errors
