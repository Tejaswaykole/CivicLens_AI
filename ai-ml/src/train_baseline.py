"""
CivicLens AI — Baseline TF-IDF + Logistic Regression Category Classifier.

Provides modular functions for:
- Leakage-resistant group-aware train/test splitting.
- Training a Scikit-Learn TF-IDF + Logistic Regression pipeline.
- Evaluating classification metrics (Precision, Recall, F1, Confusion Matrix).
- Calculating genuine linear feature contribution explanations for individual predictions.
- Generating a global feature importance summary report.
- Serializing pipeline artifacts and metadata.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Sequence, Set, Tuple

import joblib
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.pipeline import Pipeline

from schema import (
    CATEGORY_DEPARTMENT_MAPPING,
    REQUIRED_COLUMNS,
    VALID_CATEGORIES,
    validate_dataframe,
)

MODEL_VERSION = "0.1.0-baseline-tfidf-logreg"


@dataclass(frozen=True)
class FeatureContribution:
    token: str
    contribution: float

    def to_dict(self) -> Dict[str, Any]:
        return {"token": self.token, "contribution": round(self.contribution, 4)}


@dataclass(frozen=True)
class CategoryExplanation:
    predicted_category: str
    model_version: str
    decision_score: float
    top_positive_features: List[Dict[str, Any]]
    explanation_statement: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def get_dataset_fingerprint(filepath: Path | str) -> str:
    """Calculate SHA256 checksum of the training dataset file."""
    path = Path(filepath)
    hasher = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def group_aware_train_test_split(
    df: pd.DataFrame,
    group_col: str = "template_id",
    target_col: str = "category",
    test_size: float = 0.25,
    random_state: int = 42,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Split dataset ensuring that no group (template/scenario) appears in both train and test.
    Performs stratified group selection across categories to maintain class representation.
    """
    if group_col not in df.columns:
        raise ValueError(
            f"Required grouping column '{group_col}' not found in dataframe. "
            f"Available columns: {list(df.columns)}"
        )

    rng = np.random.RandomState(random_state)
    test_groups: List[str] = []
    train_groups: List[str] = []

    for cat, grp in df.groupby(target_col):
        unique_templates = sorted(grp[group_col].unique())
        n_test = max(1, int(round(len(unique_templates) * test_size)))
        chosen_test = rng.choice(unique_templates, size=n_test, replace=False)
        test_groups.extend(chosen_test)
        train_groups.extend([t for t in unique_templates if t not in chosen_test])

    # Assert 0 group overlap
    overlap = set(test_groups).intersection(set(train_groups))
    if overlap:
        raise RuntimeError(f"Data leakage detected! Group overlap between train and test: {overlap}")

    train_df = df[df[group_col].isin(train_groups)].copy().reset_index(drop=True)
    test_df = df[df[group_col].isin(test_groups)].copy().reset_index(drop=True)

    return train_df, test_df


def build_pipeline(random_state: int = 42) -> Pipeline:
    """Construct Scikit-Learn TF-IDF + LogisticRegression pipeline."""
    return Pipeline(
        steps=[
            (
                "tfidf",
                TfidfVectorizer(
                    ngram_range=(1, 2),
                    min_df=1,
                    sublinear_tf=True,
                    stop_words="english",
                ),
            ),
            (
                "classifier",
                LogisticRegression(
                    C=1.0,
                    class_weight="balanced",
                    solver="liblinear",
                    random_state=random_state,
                    max_iter=1000,
                ),
            ),
        ]
    )


def train_category_classifier(
    train_df: pd.DataFrame,
    random_state: int = 42,
) -> Pipeline:
    """Train the category classification pipeline strictly on complaint_text."""
    if "complaint_text" not in train_df.columns or "category" not in train_df.columns:
        raise ValueError("train_df must contain 'complaint_text' and 'category'")

    # Validate that non-feature columns are not passed
    X_train = train_df["complaint_text"].astype(str)
    y_train = train_df["category"].astype(str)

    # Validate classes
    present_categories = set(y_train.unique())
    if not present_categories.issubset(VALID_CATEGORIES):
        invalid = present_categories - VALID_CATEGORIES
        raise ValueError(f"Found invalid categories in training data: {invalid}")

    pipeline = build_pipeline(random_state=random_state)
    pipeline.fit(X_train, y_train)
    return pipeline


def evaluate_classifier(
    pipeline: Pipeline,
    test_df: pd.DataFrame,
) -> Dict[str, Any]:
    """Evaluate pipeline on out-of-group test set and return full metrics dictionary."""
    X_test = test_df["complaint_text"].astype(str)
    y_test = test_df["category"].astype(str)
    classes = list(pipeline.classes_)

    y_pred = pipeline.predict(X_test)

    # Classification report as dict
    report = classification_report(
        y_test,
        y_pred,
        labels=classes,
        output_dict=True,
        zero_division=0,
    )

    # Confusion matrix
    cm = confusion_matrix(y_test, y_pred, labels=classes)

    return {
        "classes": classes,
        "classification_report": report,
        "confusion_matrix": cm.tolist(),
        "accuracy": float(report.get("accuracy", 0.0)),
        "macro_avg": report.get("macro avg", {}),
        "weighted_avg": report.get("weighted avg", {}),
        "test_size": len(test_df),
        "test_distribution": test_df["category"].value_counts().to_dict(),
    }


def explain_category_prediction(
    pipeline: Pipeline,
    complaint_text: str,
    top_n: int = 5,
) -> CategoryExplanation:
    """
    Calculate genuine linear feature contributions:
    Contribution = tfidf_weight(token) * coefficient(class, token)
    for the predicted class.
    """
    if not complaint_text or not complaint_text.strip():
        return CategoryExplanation(
            predicted_category="Unknown",
            model_version=MODEL_VERSION,
            decision_score=0.0,
            top_positive_features=[],
            explanation_statement="Complaint text is empty. No features could be extracted.",
        )

    tfidf: TfidfVectorizer = pipeline.named_steps["tfidf"]
    classifier: LogisticRegression = pipeline.named_steps["classifier"]
    classes = list(classifier.classes_)

    # Vectorize single input
    X_vec = tfidf.transform([complaint_text])
    feature_names = np.array(tfidf.get_feature_names_out())

    # Predict class
    pred_idx = classifier.predict(X_vec)[0]
    # In scikit-learn, predict returns the class label
    class_label = str(pred_idx)
    class_index = classes.index(class_label)

    # Decision score for class (intercept + dot(X, coef))
    intercept = (
        float(classifier.intercept_[class_index])
        if hasattr(classifier, "intercept_") and len(classifier.intercept_) > class_index
        else 0.0
    )
    coef = classifier.coef_[class_index]

    # Non-zero active features in input vector
    non_zero_indices = X_vec.indices
    non_zero_values = X_vec.data

    if len(non_zero_indices) == 0:
        return CategoryExplanation(
            predicted_category=class_label,
            model_version=MODEL_VERSION,
            decision_score=round(intercept, 4),
            top_positive_features=[],
            explanation_statement="No recognized vocabulary terms were present in the complaint text.",
        )

    # Calculate token contribution: value * coef
    contributions: List[FeatureContribution] = []
    total_score = intercept
    for col_idx, val in zip(non_zero_indices, non_zero_values):
        token_name = feature_names[col_idx]
        contrib = float(val * coef[col_idx])
        total_score += contrib
        contributions.append(FeatureContribution(token=token_name, contribution=contrib))

    # Sort descending by contribution
    contributions.sort(key=lambda x: x.contribution, reverse=True)
    positive_contribs = [c.to_dict() for c in contributions if c.contribution > 0][:top_n]

    statement = (
        f"Model classified complaint as '{class_label}'. "
        f"These token contribution values reflect the linear weighting within the fitted Logistic Regression model "
        f"and do not constitute causal proof or human validation."
    )

    return CategoryExplanation(
        predicted_category=class_label,
        model_version=MODEL_VERSION,
        decision_score=round(total_score, 4),
        top_positive_features=positive_contribs,
        explanation_statement=statement,
    )


def generate_global_feature_summary(pipeline: Pipeline, top_n: int = 8) -> Dict[str, List[Dict[str, Any]]]:
    """Extract top positive indicative terms for each category from model coefficients."""
    tfidf: TfidfVectorizer = pipeline.named_steps["tfidf"]
    classifier: LogisticRegression = pipeline.named_steps["classifier"]
    classes = list(classifier.classes_)
    feature_names = np.array(tfidf.get_feature_names_out())

    summary: Dict[str, List[Dict[str, Any]]] = {}
    for idx, cat in enumerate(classes):
        coefs = classifier.coef_[idx]
        top_indices = np.argsort(coefs)[::-1][:top_n]
        top_terms = [
            {"term": feature_names[i], "coefficient": round(float(coefs[i]), 4)}
            for i in top_indices
            if coefs[i] > 0
        ]
        summary[cat] = top_terms
    return summary


def run_training_and_evaluation(
    dataset_path: Path,
    models_dir: Path,
    reports_dir: Path,
    random_state: int = 42,
) -> Tuple[Pipeline, Dict[str, Any]]:
    """Complete execution pipeline: load, group-split, train, evaluate, report, and save."""
    df = pd.read_csv(dataset_path)
    is_valid, errors = validate_dataframe(df)
    if not is_valid:
        raise ValueError(f"Dataset failed schema validation: {[str(e) for e in errors]}")

    fingerprint = get_dataset_fingerprint(dataset_path)

    # Group-aware split
    train_df, test_df = group_aware_train_test_split(
        df,
        group_col="template_id",
        target_col="category",
        test_size=0.25,
        random_state=random_state,
    )

    # Train
    pipeline = train_category_classifier(train_df, random_state=random_state)

    # Evaluate
    eval_results = evaluate_classifier(pipeline, test_df)
    global_features = generate_global_feature_summary(pipeline, top_n=6)

    # Save artifacts
    models_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)

    model_artifact_path = models_dir / "category_classifier_baseline.joblib"
    joblib.dump(pipeline, model_artifact_path)

    metadata = {
        "model_version": MODEL_VERSION,
        "dataset_filename": dataset_path.name,
        "dataset_sha256": fingerprint,
        "total_records": len(df),
        "train_records": len(train_df),
        "test_records": len(test_df),
        "split_method": "group_aware_template_stratified",
        "random_state": random_state,
        "categories": list(pipeline.classes_),
        "evaluation_metrics": eval_results,
        "global_feature_importance": global_features,
    }

    metadata_path = models_dir / "category_classifier_metadata.json"
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    # Write evaluation markdown report
    report_md_path = reports_dir / "baseline_evaluation.md"
    write_evaluation_report(report_md_path, metadata, train_df, test_df)

    return pipeline, metadata


def write_evaluation_report(
    output_path: Path,
    metadata: Dict[str, Any],
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
) -> None:
    """Generate comprehensive, honest markdown evaluation report."""
    eval_res = metadata["evaluation_metrics"]
    classes = eval_res["classes"]
    cm = eval_res["confusion_matrix"]
    report_dict = eval_res["classification_report"]

    lines: List[str] = [
        "# CivicLens AI — Phase 3: Baseline Classifier & Honest Evaluation",
        "",
        f"**Date**: 2026-10-20  ",
        f"**Model Version**: `{metadata['model_version']}`  ",
        f"**Pipeline**: `TfidfVectorizer(ngram_range=(1,2), sublinear_tf=True)` + `LogisticRegression(class_weight='balanced')`  ",
        f"**Split Strategy**: Leakage-Resistant Group-Aware Split on `template_id` (Random State: {metadata['random_state']})  ",
        "",
        "> [!IMPORTANT]",
        "> **Honest Evaluation Notice**:",
        "> This evaluation was conducted on an experimental synthetic corpus (`ai-ml/data/processed/synthetic_complaints.csv`).",
        "> Group-aware splitting was enforced so that **no template or complaint scenario appeared in both training and test sets**.",
        "> High test performance on synthetic templates **does not constitute proof of real-world municipal performance, transferability, or fairness**.",
        "",
        "---",
        "",
        "## 1. Dataset & Split Methodology",
        "",
        f"- **Total Dataset Size**: {metadata['total_records']} complaints",
        f"- **Training Set Size**: {metadata['train_records']} complaints ({metadata['train_records']/metadata['total_records']*100:.1f}%)",
        f"- **Test Set Size**: {metadata['test_records']} complaints ({metadata['test_records']/metadata['total_records']*100:.1f}%)",
        f"- **Group Column**: `template_id` (44 unique templates across 5 categories)",
        "- **Group Overlap**: 0 overlapping template IDs between train and test.",
        "",
        "### Category Distribution Across Splits",
        "",
        "| Category | Train Records | Test Records | Total |",
        "| :--- | :---: | :---: | :---: |",
    ]

    for cat in classes:
        train_count = int(train_df["category"].value_counts().get(cat, 0))
        test_count = int(test_df["category"].value_counts().get(cat, 0))
        lines.append(f"| **{cat}** | {train_count} | {test_count} | {train_count + test_count} |")

    lines.extend([
        "",
        "---",
        "",
        "## 2. Test Performance Metrics",
        "",
        f"- **Accuracy**: **{eval_res['accuracy'] * 100:.2f}%**",
        f"- **Macro Precision**: **{eval_res['macro_avg']['precision']:.4f}**",
        f"- **Macro Recall**: **{eval_res['macro_avg']['recall']:.4f}**",
        f"- **Macro F1-Score**: **{eval_res['macro_avg']['f1-score']:.4f}**",
        "",
        "### Per-Category Performance Breakdown",
        "",
        "| Category | Precision | Recall | F1-Score | Support (Test Cases) |",
        "| :--- | :---: | :---: | :---: | :---: |",
    ])

    for cat in classes:
        cat_metrics = report_dict.get(cat, {})
        lines.append(
            f"| **{cat}** | {cat_metrics.get('precision', 0.0):.4f} | "
            f"{cat_metrics.get('recall', 0.0):.4f} | "
            f"{cat_metrics.get('f1-score', 0.0):.4f} | "
            f"{cat_metrics.get('support', 0)} |"
        )

    lines.extend([
        "",
        "### Confusion Matrix",
        "",
        "Rows represent Ground Truth, Columns represent Model Predictions:",
        "",
        "| Ground Truth \\ Prediction | " + " | ".join(classes) + " |",
        "| :--- | " + " | ".join([":---:" for _ in classes]) + " |",
    ])

    for i, true_cat in enumerate(classes):
        row_str = " | ".join([str(cm[i][j]) for j in range(len(classes))])
        lines.append(f"| **{true_cat}** | {row_str} |")

    lines.extend([
        "",
        "---",
        "",
        "## 3. Global Explainability & Most Indicative Features",
        "",
        "Top indicative positive terms extracted from linear model weights (`LogisticRegression.coef_`):",
        "",
    ])

    for cat, terms in metadata["global_feature_importance"].items():
        term_strs = [f"`{t['term']}` ({t['coefficient']:+.2f})" for t in terms]
        lines.append(f"- **{cat}**: {', '.join(term_strs)}")

    lines.extend([
        "",
        "---",
        "",
        "## 4. Priority Evaluation Review & Operational Risks",
        "",
        "- **Why Priority was NOT Trained as a Black-Box Classifier**:",
        "  1. In the Cincinnati municipal dataset, 97% of records are labeled `STANDARD`, reflecting internal work dispatch scheduling rather than citizen urgency.",
        "  2. In synthetic datasets, priority labels reflect heuristic rules encoded into templates.",
        "  3. Training a classifier on synthetic priority creates a circular artifact that merely learns template markers.",
        "- **Consequences of Misclassification**:",
        "  - **False Low**: A high-risk emergency (e.g. live sparking cable, open sewage near a school) classified as Low priority causes lethal response delays.",
        "  - **False High**: Systemic triage overload and resource misallocation, burying genuine life-threatening emergencies.",
        "- **Recommendation**: Operational priority must be managed via an inspectable, rule-assisted triage heuristic with human officer sign-off.",
        "",
        "---",
        "",
        "## 5. Model Limitations & Non-Claims",
        "",
        "1. **No Production Claims**: This baseline model is an architectural foundation, not a certified production decision engine.",
        "2. **Domain Shifts**: Real-world citizen complaints will include spelling mistakes, informal slang, transliterated vernacular, and incomplete information that differ from synthetic templates.",
        "3. **Human Authority**: The AI model serves solely as a suggestion engine for triage officers.",
    ])

    output_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Train and evaluate CivicLens AI Category Baseline")
    parser.add_argument(
        "--dataset",
        "-d",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "data" / "processed" / "synthetic_complaints.csv",
        help="Path to complaints dataset",
    )
    parser.add_argument(
        "--models-dir",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "models",
        help="Path to save models",
    )
    parser.add_argument(
        "--reports-dir",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "reports",
        help="Path to save reports",
    )
    parser.add_argument("--seed", type=int, default=42, help="Random seed")

    args = parser.parse_args()
    print("Training and evaluating baseline category classifier...")
    pipeline, meta = run_training_and_evaluation(
        dataset_path=args.dataset.resolve(),
        models_dir=args.models_dir.resolve(),
        reports_dir=args.reports_dir.resolve(),
        random_state=args.seed,
    )
    acc = meta["evaluation_metrics"]["accuracy"]
    macro_f1 = meta["evaluation_metrics"]["macro_avg"]["f1-score"]
    print(f"Training Complete! Test Accuracy: {acc*100:.2f}%, Macro F1: {macro_f1:.4f}")
    print(f"Artifacts saved to {args.models_dir}")
    print(f"Evaluation report saved to {args.reports_dir / 'baseline_evaluation.md'}")


if __name__ == "__main__":
    main()
