"""
CivicLens AI — Dataset Inspection Utility
Robustly loads and analyzes municipal grievance/service request tabular datasets.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Sequence

import pandas as pd


def get_default_dataset_path() -> Path:
    """Resolve default raw dataset relative to this script file location."""
    # script located at: ai-ml/src/inspect_data.py -> repo root is 2 levels up
    script_dir = Path(__file__).resolve().parent
    return script_dir.parent / "data" / "raw" / "cincinnati_311_sample.csv"


def inspect_dataset(
    filepath: Path,
    category_col: str | None = None,
    priority_col: str | None = None,
    dept_col: str | None = None,
    text_col: str | None = None,
    sample_rows: int = 5,
) -> int:
    """Inspect CSV dataset and print comprehensive schema and distributions."""
    print("=" * 80)
    print(" CIVICLENS AI — DATASET INSPECTION")
    print("=" * 80)
    print(f"Target File: {filepath}")

    if not filepath.exists():
        print(f"\n[ERROR] File does not exist at specified path: {filepath}", file=sys.stderr)
        return 1

    try:
        df = pd.read_csv(filepath, low_memory=False)
    except Exception as exc:
        print(f"\n[ERROR] Failed to read CSV file: {exc}", file=sys.stderr)
        return 2

    n_rows, n_cols = df.shape
    print(f"\n1. Dimensions:")
    print(f"   - Total records (rows): {n_rows:,}")
    print(f"   - Total fields (columns): {n_cols}")

    print(f"\n2. Columns & Data Types:")
    for idx, (col, dtype) in enumerate(df.dtypes.items(), start=1):
        null_count = df[col].isna().sum()
        null_pct = (null_count / n_rows) * 100 if n_rows > 0 else 0.0
        print(f"   {idx:2d}. {col:<32} {str(dtype):<10} (Missing: {null_count:>5} | {null_pct:>5.1f}%)")

    # Duplicate records detection
    exact_duplicates = df.duplicated().sum()
    print(f"\n3. Duplicate Records:")
    print(f"   - Exact duplicate rows across all columns: {exact_duplicates:,}")

    # Discover candidate columns if not specified
    lower_map = {col.lower(): col for col in df.columns}

    def find_column(preferred: str | None, candidates: Sequence[str]) -> str | None:
        if preferred and preferred in df.columns:
            return preferred
        if preferred and preferred.lower() in lower_map:
            return lower_map[preferred.lower()]
        for candidate in candidates:
            if candidate.lower() in lower_map:
                return lower_map[candidate.lower()]
        return None

    cat_candidate = find_column(category_col, ["sr_type_desc", "group_title", "category", "service_type"])
    prio_candidate = find_column(priority_col, ["priority", "severity", "urgency", "priority_level"])
    dept_candidate = find_column(dept_col, ["dept_name", "department", "agency", "dept_code"])
    txt_candidate = find_column(text_col, ["description", "complaint_text", "notes", "sr_type_desc", "group_desc"])

    print("\n4. Identified Semantic Fields:")
    print(f"   - Category Column   : {cat_candidate or '[Not Found]'}")
    print(f"   - Priority Column   : {prio_candidate or '[Not Found]'}")
    print(f"   - Department Column : {dept_candidate or '[Not Found]'}")
    print(f"   - Text/Desc Column  : {txt_candidate or '[Not Found]'}")

    # Inspect class distributions
    def print_distribution(col_name: str | None, label: str, top_n: int = 10) -> None:
        if not col_name:
            return
        print(f"\n5. {label} Distribution ({col_name}):")
        counts = df[col_name].value_counts(dropna=False)
        total = len(df[col_name])
        for val, count in counts.head(top_n).items():
            val_str = "<MISSING/NAN>" if pd.isna(val) else str(val)
            pct = (count / total) * 100 if total > 0 else 0.0
            print(f"   - {val_str:<35} : {count:>5} ({pct:>5.1f}%)")
        if len(counts) > top_n:
            print(f"   ... and {len(counts) - top_n} more distinct classes (Total unique: {len(counts)})")

    print_distribution(cat_candidate, "Category / Service Type")
    print_distribution(prio_candidate, "Priority / Urgency")
    print_distribution(dept_candidate, "Department / Agency")

    # Sample non-sensitive preview
    print(f"\n6. Non-Sensitive Preview (First {min(sample_rows, n_rows)} rows):")
    preview_cols = [c for c in [cat_candidate, prio_candidate, dept_candidate, txt_candidate] if c]
    if not preview_cols:
        preview_cols = list(df.columns[:5])
    print(df[preview_cols].head(sample_rows).to_string(index=False))

    print("\n" + "=" * 80)
    print(" INSPECTION COMPLETE")
    print("=" * 80)
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Inspect and profile grievance datasets for CivicLens AI",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--file",
        "-f",
        type=Path,
        default=get_default_dataset_path(),
        help="Path to CSV dataset to inspect",
    )
    parser.add_argument("--category", "-c", type=str, default=None, help="Explicit category column name")
    parser.add_argument("--priority", "-p", type=str, default=None, help="Explicit priority column name")
    parser.add_argument("--department", "-d", type=str, default=None, help="Explicit department column name")
    parser.add_argument("--text", "-t", type=str, default=None, help="Explicit text/narrative column name")
    parser.add_argument("--rows", "-r", type=int, default=5, help="Number of preview sample rows to display")

    args = parser.parse_args()
    resolved_path = args.file.resolve()
    sys.exit(
        inspect_dataset(
            filepath=resolved_path,
            category_col=args.category,
            priority_col=args.priority,
            dept_col=args.department,
            text_col=args.text,
            sample_rows=args.rows,
        )
    )


if __name__ == "__main__":
    main()
