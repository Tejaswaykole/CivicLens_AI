# CivicLens AI — AI/ML Track

Explainable Public Grievance Intelligence module for **CivicLens AI** (AI Innovation Hackathon 2026).

---

## 1. Project Purpose & Architecture Boundary

The AI/ML component provides:
1. **Category Classification**: Classifying incoming citizen grievances into standard public-service categories.
2. **Priority Assessment**: Suggesting triage priority levels with clear, inspectable criteria.
3. **Department Routing**: Recommending the responsible municipal department/agency.
4. **Explainability**: Generating genuine feature-contribution explanations for decisions.
5. **Human Review & Audit**: Enabling human officers to review, correct, and validate grievance suggestions without losing original provenance.
6. **Inference Contract**: Standalone Python class `InferenceEngine` ready for backend integration without direct database or API coupling.

### Standalone Python Inference Contract
```python
from v2_model_comparison import InferenceEngine

# Load candidate model
engine = InferenceEngine.load("ai-ml/models/category_classifier_v2_candidate.joblib")

# Run prediction
res = engine.predict("Cluster of three deep potholes causing vehicle axle damage.")
print(res.predicted_category)       # e.g., 'Roads'
print(res.suggested_priority)       # e.g., 'Medium'
print(res.recommended_department)   # e.g., 'Department of Public Works'
print(res.requires_human_review)    # e.g., False
print(res.top_contributing_features)# e.g., [{'feature': 'word:potholes', 'contribution': 0.18}]
```

---

## 2. Directory Structure

```text
ai-ml/
├── .venv/               # Isolated Python 3.12 virtual environment (Git-ignored)
├── data/
│   ├── raw/             # Unmodified external dataset samples & provenance
│   │   ├── cincinnati_311_sample.csv
│   │   └── PROVENANCE.md
│   └── processed/       # Curated and experimental datasets
│       ├── synthetic_complaints.csv     # V1 benchmark corpus (150 records, 45 templates)
│       └── synthetic_complaints_v2.csv  # V2 expanded corpus (300 records, 75 templates)
├── docs/
│   └── taxonomy_and_annotation.md       # Category definitions, inclusion/exclusion, priority criteria
├── notebooks/           # Exploratory data analysis and experimental notebooks
├── src/
│   ├── inspect_data.py            # Robust dataset profiling and schema inspection utility
│   ├── schema.py                  # Controlled vocabularies and validation rules
│   ├── generate_synthetic_data.py # Reproducible synthetic grievance corpus generator (V1)
│   ├── generate_expanded_corpus.py# Expanded V2 generator with diverse styles and clinical vocabulary
│   ├── train_baseline.py          # TF-IDF + Logistic Regression category classifier (V1)
│   ├── error_analysis.py          # Instance-level test error diagnosis and majority benchmark comparison
│   ├── human_review.py            # Human officer review workflow & audit queue exporter
│   └── v2_model_comparison.py     # Controlled V2 model comparison, subword pipeline, and InferenceEngine
├── models/              # Serialized model pipelines and metadata (Git-ignored)
│   ├── category_classifier_baseline.joblib
│   ├── category_classifier_metadata.json
│   ├── category_classifier_v2_candidate.joblib
│   └── category_classifier_v2_metadata.json
├── reports/             # Dataset assessments, evaluation metrics, and audit logs
│   ├── dataset_assessment.md
│   ├── baseline_evaluation.md
│   ├── error_analysis.md          # Comprehensive instance-by-instance test audit (V1)
│   ├── error_analysis_data.json
│   ├── human_review_queue.csv
│   └── model_comparison_v2.md     # Controlled comparison report on V2 corpus
├── tests/               # Unit and regression test suite (pytest)
│   ├── test_inspect_data.py
│   ├── test_schema_and_dataset.py
│   ├── test_train_baseline.py
│   ├── test_error_analysis_and_review.py
│   └── test_v2_comparison.py
├── requirements.txt     # Minimal, reproducible dependencies
└── README.md
```

---

## 3. Environment Setup & Dependency Installation

The environment utilizes a local Python 3.12 virtual environment managed via `uv`:

```powershell
# From the repository root:
uv venv --python 3.12 ai-ml/.venv

# Activate in PowerShell:
.\ai-ml\.venv\Scripts\Activate.ps1

# Install reproducible dependencies:
uv pip install --python ai-ml/.venv/Scripts/python.exe -r ai-ml/requirements.txt
```

### Verified Dependency Stack:
- `python`: 3.12.14
- `pandas`: 2.3.3
- `numpy`: 2.1.3
- `scikit-learn`: 1.5.2
- `matplotlib`: 3.9.4
- `joblib`: 1.4.2
- `pytest`: 8.4.2
- `jupyter`: 1.1.1

---

## 4. Phase 5 Controlled Model Comparison (V2 Corpus)

To run the controlled comparison on the held-out V2 test partition:
```powershell
& ai-ml\.venv\Scripts\python.exe ai-ml\src\v2_model_comparison.py
```

### Results Summary (Identical V2 Held-Out Split, Zero Group Overlap):
- **Split Protocol**: 222 Train (55 templates) | 78 Test (20 templates).
- **Comparison Table**:
  | Architecture | Accuracy | Macro F1 | Public Health F1 | Latency |
  | :--- | :---: | :---: | :---: | :---: |
  | **Majority-Class Baseline** | 25.64% | 0.0816 | 0.0000 | < 0.01 ms |
  | **Model A: Word TF-IDF + LogReg** | 56.41% | 0.5507 | 0.7222 | 0.35 ms |
  | **Model B: Word + Char TF-IDF + LogReg** | **66.67%** | **0.6639** | **0.8108** | **0.42 ms** |

> [!NOTE]
> **Key Finding**: Adding character-level n-grams (`char_wb`, range 3-5) improved generalization across out-of-template complaints (+10.26% accuracy, +0.1132 macro F1) and resolved the earlier Public Health recall bottleneck (F1 increased from 0.00 to 0.8108) while maintaining sub-millisecond CPU inference.

---

## 5. Running Full Test Suite
```powershell
& ai-ml\.venv\Scripts\python.exe -m pytest ai-ml\tests
```
All **30 unit tests** pass in ~2.1s across schema validation, group-aware splitting, training reproducibility, mathematical feature contribution checks, review workflows, error analysis, and candidate inference contracts.

---

## 6. Critical Disclaimers & Operational Limitations

> [!WARNING]
> **Strict Operational Limitations & Non-Claims**:
> 1. **Synthetic Experimental Corpus**: V2 results reflect out-of-template generalization on an experimental synthetic corpus and **do not establish real-world municipal performance, fairness, or robustness against noisy citizen inputs**.
> 2. **Category vs. Priority**: Category classification and priority prediction are distinct tasks. Priority has intentionally **not** been modeled as a black-box classifier to prevent dangerous false-low emergency triage decisions.
> 3. **Human Authority**: The AI system acts solely as a triage recommendation engine. Municipal human grievance officers retain final authority on all category routing and emergency escalations.
> 4. **Privacy**: No citizen personally identifiable information (PII) is processed or committed.
