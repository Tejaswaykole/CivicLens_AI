"""
Unit tests for CivicLens AI Phase 3: Baseline Classifier, Group Splitting, and Explainability.
"""

import json
from pathlib import Path
import pytest
import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline

from train_baseline import (
    MODEL_VERSION,
    build_pipeline,
    group_aware_train_test_split,
    train_category_classifier,
    evaluate_classifier,
    explain_category_prediction,
    generate_global_feature_summary,
    run_training_and_evaluation,
)


@pytest.fixture
def mini_corpus() -> pd.DataFrame:
    """Deterministic synthetic fixture with explicit template groups."""
    data = []
    categories = ["Sanitation", "Roads", "Electricity", "Water Supply", "Public Health"]
    for cat in categories:
        for t_idx in range(1, 5):  # 4 templates per category
            tid = f"{cat[:3].upper()}_T{t_idx:02d}"
            for rep in range(3):  # 3 variations per template
                data.append({
                    "complaint_id": f"TEST-{cat[:3].upper()}-{t_idx}-{rep}",
                    "complaint_text": f"Grievance regarding {cat.lower()} issue at location variation {rep} with template keyword {tid}.",
                    "category": cat,
                    "priority": "Medium",
                    "recommended_department": "Test Department",
                    "annotation_rationale": "Test rationale",
                    "source_type": "synthetic_template",
                    "review_status": "pending_review",
                    "template_id": tid,
                })
    return pd.DataFrame(data)


def test_group_aware_train_test_split(mini_corpus: pd.DataFrame):
    train_df, test_df = group_aware_train_test_split(
        mini_corpus,
        group_col="template_id",
        target_col="category",
        test_size=0.25,
        random_state=42,
    )
    # Check that neither is empty
    assert len(train_df) > 0
    assert len(test_df) > 0
    assert len(train_df) + len(test_df) == len(mini_corpus)

    # Check zero overlap
    train_groups = set(train_df["template_id"])
    test_groups = set(test_df["template_id"])
    overlap = train_groups.intersection(test_groups)
    assert len(overlap) == 0, f"Found group overlap: {overlap}"

    # Check all 5 categories exist in both splits
    assert set(train_df["category"].unique()) == set(mini_corpus["category"].unique())
    assert set(test_df["category"].unique()) == set(mini_corpus["category"].unique())


def test_missing_group_column_raises_error(mini_corpus: pd.DataFrame):
    df_no_group = mini_corpus.drop(columns=["template_id"])
    with pytest.raises(ValueError, match="Required grouping column 'template_id' not found"):
        group_aware_train_test_split(df_no_group, group_col="template_id")


def test_train_pipeline_input_validation(mini_corpus: pd.DataFrame):
    # Reject when category is missing
    df_no_cat = mini_corpus.drop(columns=["category"])
    with pytest.raises(ValueError, match="train_df must contain"):
        train_category_classifier(df_no_cat)

    # Reject invalid categories
    df_invalid_cat = mini_corpus.copy()
    df_invalid_cat.loc[0, "category"] = "AlienInvasion"
    with pytest.raises(ValueError, match="Found invalid categories in training data"):
        train_category_classifier(df_invalid_cat)


def test_train_pipeline_reproducibility(mini_corpus: pd.DataFrame):
    pipe1 = train_category_classifier(mini_corpus, random_state=42)
    pipe2 = train_category_classifier(mini_corpus, random_state=42)

    coef1 = pipe1.named_steps["classifier"].coef_
    coef2 = pipe2.named_steps["classifier"].coef_
    np.testing.assert_allclose(coef1, coef2)


def test_evaluate_classifier_structure(mini_corpus: pd.DataFrame):
    train_df, test_df = group_aware_train_test_split(mini_corpus, random_state=42)
    pipeline = train_category_classifier(train_df, random_state=42)
    eval_res = evaluate_classifier(pipeline, test_df)

    assert "accuracy" in eval_res
    assert "macro_avg" in eval_res
    assert "confusion_matrix" in eval_res
    assert len(eval_res["confusion_matrix"]) == len(pipeline.classes_)
    assert isinstance(eval_res["accuracy"], float)


def test_explain_category_prediction_values(mini_corpus: pd.DataFrame):
    pipeline = train_category_classifier(mini_corpus, random_state=42)
    sample_text = "Grievance regarding sanitation issue at location"
    explanation = explain_category_prediction(pipeline, sample_text, top_n=3)

    assert explanation.model_version == MODEL_VERSION
    assert explanation.predicted_category in pipeline.classes_
    assert isinstance(explanation.decision_score, float)
    assert len(explanation.top_positive_features) <= 3

    # Verify calculation: check that token contribution = tfidf * coef
    tfidf = pipeline.named_steps["tfidf"]
    clf = pipeline.named_steps["classifier"]
    class_idx = list(clf.classes_).index(explanation.predicted_category)

    vec = tfidf.transform([sample_text])
    feature_names = np.array(tfidf.get_feature_names_out())

    for item in explanation.top_positive_features:
        token = item["token"]
        token_col = list(feature_names).index(token)
        expected_contrib = float(vec[0, token_col] * clf.coef_[class_idx, token_col])
        assert abs(item["contribution"] - round(expected_contrib, 4)) < 1e-3


def test_explain_empty_and_unknown_text(mini_corpus: pd.DataFrame):
    pipeline = train_category_classifier(mini_corpus, random_state=42)

    # Empty string
    empty_exp = explain_category_prediction(pipeline, "")
    assert empty_exp.predicted_category == "Unknown"
    assert "empty" in empty_exp.explanation_statement

    # Out of vocabulary string
    oov_exp = explain_category_prediction(pipeline, "zyxw vuts rqpo")
    assert oov_exp.predicted_category in pipeline.classes_
    assert len(oov_exp.top_positive_features) == 0


def test_global_feature_summary(mini_corpus: pd.DataFrame):
    pipeline = train_category_classifier(mini_corpus, random_state=42)
    summary = generate_global_feature_summary(pipeline, top_n=5)
    assert set(summary.keys()) == set(pipeline.classes_)
    for cat, terms in summary.items():
        assert len(terms) <= 5
        if terms:
            assert "term" in terms[0]
            assert "coefficient" in terms[0]


def test_metadata_consistency_on_disk(tmp_path: Path, mini_corpus: pd.DataFrame):
    dataset_file = tmp_path / "test_corpus.csv"
    mini_corpus.to_csv(dataset_file, index=False)

    models_dir = tmp_path / "models"
    reports_dir = tmp_path / "reports"

    pipeline, metadata = run_training_and_evaluation(
        dataset_path=dataset_file,
        models_dir=models_dir,
        reports_dir=reports_dir,
        random_state=42,
    )

    metadata_file = models_dir / "category_classifier_metadata.json"
    assert metadata_file.exists()
    report_file = reports_dir / "baseline_evaluation.md"
    assert report_file.exists()

    with open(metadata_file) as f:
        loaded = json.load(f)

    assert loaded["model_version"] == MODEL_VERSION
    assert loaded["total_records"] == len(mini_corpus)
    assert loaded["split_method"] == "group_aware_template_stratified"
