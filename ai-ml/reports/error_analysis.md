# CivicLens AI — Phase 4: Detailed Error Analysis & Baseline Report

**Date**: 2026-10-20  
**Evaluated Model**: `TfidfVectorizer + LogisticRegression (Baseline)`  
**Test Set Records**: 38 complaints (Held-out template-grouped split)  

---

## 1. Baseline Comparisons (Model vs. Majority Class)

To verify whether the baseline model provides genuine statistical signal over simple heuristics, it was benchmarked against a **Majority-Class Baseline** (predicting `Water Supply` for all test cases) on the exact same held-out test split.

| Metric | Majority-Class Baseline | TF-IDF + Logistic Regression | Relative Delta |
| :--- | :---: | :---: | :---: |
| **Accuracy** | 13.16% | **23.68%** | +10.53% |
| **Macro Precision** | 0.0263 | **0.2738** | +0.2474 |
| **Macro Recall** | 0.2000 | **0.2579** | +0.0579 |
| **Macro F1-Score** | 0.0465 | **0.2450** | +0.1985 |

> [!NOTE]
> **Finding**: The TF-IDF model outperforms the majority baseline (Macro F1: 0.2450 vs. 0.0465, Accuracy: 23.68% vs 13.16%), > but its absolute accuracy on unseen templates reveals critical generalization bottlenecks caused by vocabulary sparsity.

---

## 2. Error Patterns & Root Causes

### A. The Public Health Recall Collapse (Recall = 0.0)
- Out of 11 held-out test complaints in **Public Health**, the model predicted **0 correctly**.
- **Misclassification destinations**: 6 instances predicted as `Sanitation`, 3 as `Roads`, 2 as `Water Supply`.
- **Root Cause**: Severe lexical overlap. Complaints describing food stalls, waste dumping in alleys, or open sewers contain terms (`waste`, `dumped`, `stall`, `water`) that have higher linear coefficients in other categories when training on a small template set.

### B. Confusion Matrix Diagnostic

| True \ Predicted | Electricity | Public Health | Roads | Sanitation | Water Supply |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Electricity** | 3 | 0 | 2 | 1 | 2 |
| **Public Health** | 0 | 0 | 3 | 6 | 2 |
| **Roads** | 0 | 4 | 1 | 2 | 0 |
| **Sanitation** | 0 | 2 | 1 | 4 | 0 |
| **Water Supply** | 1 | 1 | 2 | 0 | 1 |

### C. Common Confusion Pairs
1. **Public Health $\rightarrow$ Sanitation (6 errors)**: Biowaste, dead poultry, and street stall hygiene confusions.
2. **Roads $\rightarrow$ Public Health (4 errors)**: Missing manhole covers classified as Public Health due to sewer associations.
3. **Water Supply $\rightarrow$ Roads / Electricity (2 errors)**: Pipeline bursts flooding roads or electrical substations.

---

## 3. Instance-by-Instance Test Audit

| ID | True Category | Predicted | Outcome | Top Features Extracted | Analyst Interpretation |
| :--- | :--- | :--- | :---: | :--- | :--- |
| `SYN-ELE-01079` | **Electricity** | Sanitation | ❌ FAIL | `3rd`, `3rd cross` | Analyst Note: False attribution. Model misclassified Electricity $\rightarrow$ Sanitation based on incidental vocabulary: '3rd', '3rd cross'. |
| `SYN-PUB-01142` | **Public Health** | Sanitation | ❌ FAIL | `dumped`, `stench` | Analyst Note: Cross-domain lexical overlap. Words like 'waste' or 'dumped' heavily weight towards Sanitation in training data, overwhelming Public Health pathogen context. |
| `SYN-ROA-01037` | **Roads** | Sanitation | ❌ FAIL | `3rd`, `3rd cross` | Analyst Note: False attribution. Model misclassified Roads $\rightarrow$ Sanitation based on incidental vocabulary: '3rd', '3rd cross'. |
| `SYN-WAT-01105` | **Water Supply** | Electricity | ❌ FAIL | `bose`, `bose park` | Analyst Note: False attribution. Model misclassified Water Supply $\rightarrow$ Electricity based on incidental vocabulary: 'bose', 'bose park'. |
| `SYN-SAN-01030` | **Sanitation** | Sanitation | ✅ PASS | `openly`, `waste` | Correctly classified. Model leveraged genuine domain tokens: 'openly', 'waste'. |
| `SYN-PUB-01132` | **Public Health** | Sanitation | ❌ FAIL | `dumped`, `stench` | Analyst Note: Cross-domain lexical overlap. Words like 'waste' or 'dumped' heavily weight towards Sanitation in training data, overwhelming Public Health pathogen context. |
| `SYN-ROA-01046` | **Roads** | Sanitation | ❌ FAIL | `near`, `marg` | Analyst Note: False attribution. Model misclassified Roads $\rightarrow$ Sanitation based on incidental vocabulary: 'near', 'marg'. |
| `SYN-SAN-01016` | **Sanitation** | Public Health | ❌ FAIL | `hospital`, `city` | Analyst Note: False attribution. Model misclassified Sanitation $\rightarrow$ Public Health based on incidental vocabulary: 'hospital', 'city'. |
| `SYN-PUB-01147` | **Public Health** | Water Supply | ❌ FAIL | `water`, `main market` | Analyst Note: False attribution. Model misclassified Public Health $\rightarrow$ Water Supply based on incidental vocabulary: 'water', 'main market'. |
| `SYN-PUB-01143` | **Public Health** | Sanitation | ❌ FAIL | `community`, `near` | Analyst Note: Taxonomy ambiguity between environmental public health vectors and solid waste collection. |
| `SYN-ELE-01086` | **Electricity** | Electricity | ✅ PASS | `pole`, `lamp` | Correctly classified. Model leveraged genuine domain tokens: 'pole', 'lamp'. |
| `SYN-ELE-01087` | **Electricity** | Electricity | ✅ PASS | `pole`, `lamp` | Correctly classified. Model leveraged genuine domain tokens: 'pole', 'lamp'. |
| `SYN-SAN-01017` | **Sanitation** | Sanitation | ✅ PASS | `garbage`, `plastic` | Correctly classified. Model leveraged genuine domain tokens: 'garbage', 'plastic'. |
| `SYN-ELE-01082` | **Electricity** | Water Supply | ❌ FAIL | `leaking`, `main market` | Analyst Note: False attribution. Model misclassified Electricity $\rightarrow$ Water Supply based on incidental vocabulary: 'leaking', 'main market'. |
| `SYN-WAT-01110` | **Water Supply** | Public Health | ❌ FAIL | `hospital`, `city` | Analyst Note: Compound symptom confusion. Pipeline burst flooded a road or mixed with sewage, leading the model to misattribute the primary root cause. |
| `SYN-PUB-01123` | **Public Health** | Roads | ❌ FAIL | `severe`, `lane` | Analyst Note: False attribution. Model misclassified Public Health $\rightarrow$ Roads based on incidental vocabulary: 'severe', 'lane'. |
| `SYN-SAN-01029` | **Sanitation** | Public Health | ❌ FAIL | `estate`, `estate phase` | Analyst Note: False attribution. Model misclassified Sanitation $\rightarrow$ Public Health based on incidental vocabulary: 'estate', 'estate phase'. |
| `SYN-WAT-01096` | **Water Supply** | Roads | ❌ FAIL | `meter`, `bus terminal` | Analyst Note: Compound symptom confusion. Pipeline burst flooded a road or mixed with sewage, leading the model to misattribute the primary root cause. |
| `SYN-WAT-01098` | **Water Supply** | Water Supply | ✅ PASS | `water`, `supply` | Correctly classified. Model leveraged genuine domain tokens: 'water', 'supply'. |
| `SYN-ROA-01054` | **Roads** | Roads | ✅ PASS | `deep`, `gandhi` | Correctly classified. Model leveraged genuine domain tokens: 'deep', 'gandhi'. |
| `SYN-ELE-01071` | **Electricity** | Water Supply | ❌ FAIL | `leaking`, `12 leaking` | Analyst Note: False attribution. Model misclassified Electricity $\rightarrow$ Water Supply based on incidental vocabulary: 'leaking', '12 leaking'. |
| `SYN-ELE-01084` | **Electricity** | Roads | ❌ FAIL | `adarsh`, `adarsh colony` | Analyst Note: False attribution. Model misclassified Electricity $\rightarrow$ Roads based on incidental vocabulary: 'adarsh', 'adarsh colony'. |
| `SYN-PUB-01136` | **Public Health** | Sanitation | ❌ FAIL | `dumped`, `stench` | Analyst Note: Cross-domain lexical overlap. Words like 'waste' or 'dumped' heavily weight towards Sanitation in training data, overwhelming Public Health pathogen context. |
| `SYN-SAN-01018` | **Sanitation** | Sanitation | ✅ PASS | `openly`, `waste` | Correctly classified. Model leveraged genuine domain tokens: 'openly', 'waste'. |
| `SYN-ROA-01039` | **Roads** | Public Health | ❌ FAIL | `hospital`, `city` | Analyst Note: False attribution. Model misclassified Roads $\rightarrow$ Public Health based on incidental vocabulary: 'hospital', 'city'. |
| `SYN-PUB-01127` | **Public Health** | Roads | ❌ FAIL | `lane`, `crossing` | Analyst Note: False attribution. Model misclassified Public Health $\rightarrow$ Roads based on incidental vocabulary: 'lane', 'crossing'. |
| `SYN-ROA-01047` | **Roads** | Public Health | ❌ FAIL | `estate`, `estate phase` | Analyst Note: False attribution. Model misclassified Roads $\rightarrow$ Public Health based on incidental vocabulary: 'estate', 'estate phase'. |
| `SYN-PUB-01140` | **Public Health** | Roads | ❌ FAIL | `severe`, `dead` | Analyst Note: False attribution. Model misclassified Public Health $\rightarrow$ Roads based on incidental vocabulary: 'severe', 'dead'. |
| `SYN-PUB-01125` | **Public Health** | Sanitation | ❌ FAIL | `community`, `3rd` | Analyst Note: Taxonomy ambiguity between environmental public health vectors and solid waste collection. |
| `SYN-ROA-01058` | **Roads** | Public Health | ❌ FAIL | `hospital`, `city` | Analyst Note: False attribution. Model misclassified Roads $\rightarrow$ Public Health based on incidental vocabulary: 'hospital', 'city'. |
| `SYN-PUB-01130` | **Public Health** | Sanitation | ❌ FAIL | `dumped`, `stench` | Analyst Note: Cross-domain lexical overlap. Words like 'waste' or 'dumped' heavily weight towards Sanitation in training data, overwhelming Public Health pathogen context. |
| `SYN-ROA-01038` | **Roads** | Public Health | ❌ FAIL | `estate`, `estate phase` | Analyst Note: False attribution. Model misclassified Roads $\rightarrow$ Public Health based on incidental vocabulary: 'estate', 'estate phase'. |
| `SYN-PUB-01141` | **Public Health** | Water Supply | ❌ FAIL | `water`, `public` | Analyst Note: False attribution. Model misclassified Public Health $\rightarrow$ Water Supply based on incidental vocabulary: 'water', 'public'. |
| `SYN-WAT-01100` | **Water Supply** | Roads | ❌ FAIL | `meter`, `adarsh` | Analyst Note: Compound symptom confusion. Pipeline burst flooded a road or mixed with sewage, leading the model to misattribute the primary root cause. |
| `SYN-ELE-01088` | **Electricity** | Roads | ❌ FAIL | `lane`, `crossing` | Analyst Note: False attribution. Model misclassified Electricity $\rightarrow$ Roads based on incidental vocabulary: 'lane', 'crossing'. |
| `SYN-SAN-01021` | **Sanitation** | Sanitation | ✅ PASS | `openly`, `waste` | Correctly classified. Model leveraged genuine domain tokens: 'openly', 'waste'. |
| `SYN-ELE-01072` | **Electricity** | Electricity | ✅ PASS | `pole`, `lamp` | Correctly classified. Model leveraged genuine domain tokens: 'pole', 'lamp'. |
| `SYN-SAN-01015` | **Sanitation** | Roads | ❌ FAIL | `lane`, `crossing` | Analyst Note: False attribution. Model misclassified Sanitation $\rightarrow$ Roads based on incidental vocabulary: 'lane', 'crossing'. |

---

## 4. Key Recommendations for Dataset Expansion

1. **Break Single-Keyword Dependency**: Add multi-sentence phrasing where the category is established by semantic intent rather than a single cue word.
2. **Disambiguate Public Health vs Sanitation**: Add specific clinical/vector narratives (mosquito larvae, epidemic fever, dengue risk, biohazard contamination).
3. **Add Colloquial & Informal Variations**: Include complaints with minor typos, informal speech, and multi-issue reporting.
4. **Preserve Human-in-the-Loop Review**: Maintain strict reviewer status and audit trails on all newly curated complaints.