"""
CivicLens AI — Human Review Workflow Utility.

Allows a human triage officer or domain reviewer to inspect complaint records,
approve or modify categories/priorities, flag safety-critical and ambiguous cases,
and record review rationales without silently overwriting original labels or provenance.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd

from schema import (
    CATEGORY_DEPARTMENT_MAPPING,
    VALID_CATEGORIES,
    VALID_PRIORITIES,
    VALID_REVIEW_STATUSES,
    validate_dataframe,
)


def apply_human_review(
    df: pd.DataFrame,
    complaint_id: str,
    reviewer_id: str,
    reviewed_category: Optional[str] = None,
    reviewed_priority: Optional[str] = None,
    review_status: str = "officer_approved",
    review_notes: str = "",
    is_safety_critical: bool = False,
    is_ambiguous: bool = False,
) -> pd.DataFrame:
    """Apply a documented human review decision to a single complaint record."""
    if complaint_id not in df["complaint_id"].values:
        raise ValueError(f"Complaint ID '{complaint_id}' not found in dataset.")

    if reviewed_category and reviewed_category not in VALID_CATEGORIES:
        raise ValueError(f"Invalid reviewed_category '{reviewed_category}'. Must be in {VALID_CATEGORIES}")

    if reviewed_priority and reviewed_priority not in VALID_PRIORITIES:
        raise ValueError(f"Invalid reviewed_priority '{reviewed_priority}'. Must be in {VALID_PRIORITIES}")

    if review_status not in VALID_REVIEW_STATUSES:
        raise ValueError(f"Invalid review_status '{review_status}'. Must be in {VALID_REVIEW_STATUSES}")

    updated = df.copy()
    idx = updated[updated["complaint_id"] == complaint_id].index[0]

    # Initialize review columns if not present
    for col in [
        "reviewed_category",
        "reviewed_priority",
        "review_notes",
        "is_safety_critical",
        "is_ambiguous",
        "reviewer_id",
    ]:
        if col not in updated.columns:
            updated[col] = None

    # Apply changes while preserving original columns
    updated.at[idx, "reviewer_id"] = reviewer_id
    updated.at[idx, "review_status"] = review_status
    updated.at[idx, "reviewed_category"] = reviewed_category or updated.at[idx, "category"]
    updated.at[idx, "reviewed_priority"] = reviewed_priority or updated.at[idx, "priority"]
    updated.at[idx, "review_notes"] = review_notes
    updated.at[idx, "is_safety_critical"] = bool(is_safety_critical)
    updated.at[idx, "is_ambiguous"] = bool(is_ambiguous)

    return updated


def export_review_queue(
    df: pd.DataFrame,
    output_path: Path,
    filter_status: str = "pending_review",
) -> None:
    """Export unreviewed or pending records to an audit CSV file."""
    queue = df[df["review_status"] == filter_status].copy()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    queue.to_csv(output_path, index=False)
    print(f"Exported {len(queue)} pending review records to: {output_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Human Review Workflow Tool for CivicLens AI")
    parser.add_argument(
        "--dataset",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "data" / "processed" / "synthetic_complaints.csv",
        help="Path to complaints dataset",
    )
    parser.add_argument(
        "--export-queue",
        type=Path,
        default=None,
        help="Export pending review records to specified CSV path",
    )
    parser.add_argument("--review-id", type=str, default=None, help="Complaint ID to review")
    parser.add_argument("--reviewer", type=str, default="analyst_default", help="Reviewer identifier")
    parser.add_argument("--category", type=str, default=None, help="Reviewed category")
    parser.add_argument("--priority", type=str, default=None, help="Reviewed priority")
    parser.add_argument("--status", type=str, default="officer_approved", help="New review status")
    parser.add_argument("--notes", type=str, default="", help="Reviewer notes / rationale")
    parser.add_argument("--safety-critical", action="store_true", help="Flag as safety-critical")
    parser.add_argument("--ambiguous", action="store_true", help="Flag as ambiguous")
    parser.add_argument("--output", type=Path, default=None, help="Destination output path")

    args = parser.parse_args()
    df = pd.read_csv(args.dataset.resolve())

    if args.export_queue:
        export_review_queue(df, args.export_queue.resolve())
        return

    if args.review_id:
        out_path = args.output.resolve() if args.output else args.dataset.resolve()
        updated = apply_human_review(
            df=df,
            complaint_id=args.review_id,
            reviewer_id=args.reviewer,
            reviewed_category=args.category,
            reviewed_priority=args.priority,
            review_status=args.status,
            review_notes=args.notes,
            is_safety_critical=args.safety_critical,
            is_ambiguous=args.ambiguous,
        )
        is_valid, errors = validate_dataframe(updated)
        if not is_valid:
            print("[ERROR] Schema validation failed after review update:")
            for e in errors[:5]:
                print(f"  - {e}")
            raise SystemExit(1)
        updated.to_csv(out_path, index=False)
        print(f"Successfully recorded review for {args.review_id}. Saved to {out_path}")
    else:
        print("CivicLens Review Utility: Provide --review-id to record a review, or --export-queue to export audit CSV.")


if __name__ == "__main__":
    main()
