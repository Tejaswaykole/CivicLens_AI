# CivicLens AI — Phase 3: Baseline Classifier & Honest Evaluation

**Date**: 2026-10-20  
**Model Version**: `0.1.0-baseline-tfidf-logreg`  
**Pipeline**: `TfidfVectorizer(ngram_range=(1,2), sublinear_tf=True)` + `LogisticRegression(class_weight='balanced')`  
**Split Strategy**: Leakage-Resistant Group-Aware Split on `template_id` (Random State: 42)  

> [!IMPORTANT]
> **Honest Evaluation Notice**:
> This evaluation was conducted on an experimental synthetic corpus (`ai-ml/data/processed/synthetic_complaints.csv`).
> Group-aware splitting was enforced so that **no template or complaint scenario appeared in both training and test sets**.
> High test performance on synthetic templates **does not constitute proof of real-world municipal performance, transferability, or fairness**.

---

## 1. Dataset & Split Methodology

- **Total Dataset Size**: 150 complaints
- **Training Set Size**: 112 complaints (74.7%)
- **Test Set Size**: 38 complaints (25.3%)
- **Group Column**: `template_id` (44 unique templates across 5 categories)
- **Group Overlap**: 0 overlapping template IDs between train and test.

### Category Distribution Across Splits

| Category | Train Records | Test Records | Total |
| :--- | :---: | :---: | :---: |
| **Electricity** | 22 | 8 | 30 |
| **Public Health** | 19 | 11 | 30 |
| **Roads** | 23 | 7 | 30 |
| **Sanitation** | 23 | 7 | 30 |
| **Water Supply** | 25 | 5 | 30 |

---

## 2. Test Performance Metrics

- **Accuracy**: **23.68%**
- **Macro Precision**: **0.2738**
- **Macro Recall**: **0.2579**
- **Macro F1-Score**: **0.2450**

### Per-Category Performance Breakdown

| Category | Precision | Recall | F1-Score | Support (Test Cases) |
| :--- | :---: | :---: | :---: | :---: |
| **Electricity** | 0.7500 | 0.3750 | 0.5000 | 8.0 |
| **Public Health** | 0.0000 | 0.0000 | 0.0000 | 11.0 |
| **Roads** | 0.1111 | 0.1429 | 0.1250 | 7.0 |
| **Sanitation** | 0.3077 | 0.5714 | 0.4000 | 7.0 |
| **Water Supply** | 0.2000 | 0.2000 | 0.2000 | 5.0 |

### Confusion Matrix

Rows represent Ground Truth, Columns represent Model Predictions:

| Ground Truth \ Prediction | Electricity | Public Health | Roads | Sanitation | Water Supply |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Electricity** | 3 | 0 | 2 | 1 | 2 |
| **Public Health** | 0 | 0 | 3 | 6 | 2 |
| **Roads** | 0 | 4 | 1 | 2 | 0 |
| **Sanitation** | 0 | 2 | 1 | 4 | 0 |
| **Water Supply** | 1 | 1 | 2 | 0 | 1 |

---

## 3. Global Explainability & Most Indicative Features

Top indicative positive terms extracted from linear model weights (`LogisticRegression.coef_`):

- **Electricity**: `power` (+0.58), `nights` (+0.46), `nights creating` (+0.46), `remained dark` (+0.46), `fears` (+0.46), `fears total` (+0.46)
- **Public Health**: `open` (+0.76), `basin faucet` (+0.58), `washer replacement` (+0.58), `basin` (+0.58), `needs washer` (+0.58), `needs` (+0.58)
- **Roads**: `broken` (+0.60), `deep` (+0.52), `missing` (+0.49), `completely` (+0.47), `lane` (+0.46), `slight surface` (+0.38)
- **Sanitation**: `garbage` (+0.71), `waste` (+0.45), `collection truck` (+0.42), `consecutive` (+0.42), `garbage collection` (+0.42), `consecutive rounds` (+0.42)
- **Water Supply**: `water` (+1.08), `drinking water` (+0.80), `drinking` (+0.80), `supply` (+0.62), `pipeline` (+0.61), `municipal` (+0.42)

---

## 4. Priority Evaluation Review & Operational Risks

- **Why Priority was NOT Trained as a Black-Box Classifier**:
  1. In the Cincinnati municipal dataset, 97% of records are labeled `STANDARD`, reflecting internal work dispatch scheduling rather than citizen urgency.
  2. In synthetic datasets, priority labels reflect heuristic rules encoded into templates.
  3. Training a classifier on synthetic priority creates a circular artifact that merely learns template markers.
- **Consequences of Misclassification**:
  - **False Low**: A high-risk emergency (e.g. live sparking cable, open sewage near a school) classified as Low priority causes lethal response delays.
  - **False High**: Systemic triage overload and resource misallocation, burying genuine life-threatening emergencies.
- **Recommendation**: Operational priority must be managed via an inspectable, rule-assisted triage heuristic with human officer sign-off.

---

## 5. Model Limitations & Non-Claims

1. **No Production Claims**: This baseline model is an architectural foundation, not a certified production decision engine.
2. **Domain Shifts**: Real-world citizen complaints will include spelling mistakes, informal slang, transliterated vernacular, and incomplete information that differ from synthetic templates.
3. **Human Authority**: The AI model serves solely as a suggestion engine for triage officers.