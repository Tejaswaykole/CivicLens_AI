"""
Tests for CivicLens AI dataset inspection script.
"""

from pathlib import Path
import pytest
import pandas as pd

from inspect_data import inspect_dataset, get_default_dataset_path


def test_default_dataset_path_resolution():
    default_path = get_default_dataset_path()
    assert default_path.name == "cincinnati_311_sample.csv"
    assert "data" in default_path.parts
    assert "raw" in default_path.parts


def test_missing_file_handling(tmp_path: Path):
    missing_file = tmp_path / "non_existent.csv"
    status = inspect_dataset(missing_file)
    assert status == 1


def test_inspection_on_sample_or_fixture(tmp_path: Path):
    fixture_csv = tmp_path / "fixture.csv"
    df = pd.DataFrame({
        "sr_type_desc": ["POTHOLE IN STREET", "STREET LIGHT OUT", "POTHOLE IN STREET"],
        "priority": ["STANDARD", "HAZARDOUS", "STANDARD"],
        "dept_name": ["TRANSPORTATION", "PUBLIC UTILITIES", "TRANSPORTATION"],
        "address": ["123 MAIN ST", "456 OAK AVE", "789 ELM ST"],
    })
    df.to_csv(fixture_csv, index=False)

    status = inspect_dataset(
        fixture_csv,
        category_col="sr_type_desc",
        priority_col="priority",
        dept_col="dept_name",
        sample_rows=2,
    )
    assert status == 0
