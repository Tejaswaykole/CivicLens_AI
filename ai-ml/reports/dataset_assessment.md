# CivicLens AI — Dataset Assessment Report

**Date**: 2026-10-20  
**Dataset Evaluated**: Cincinnati 311 (Non-Emergency) Service Requests  
**Source**: City of Cincinnati Open Data Portal (Socrata API: `gcej-gmiw`)  
**Sample File**: `ai-ml/data/raw/cincinnati_311_sample.csv` (1,000 records, 67 columns)  

---

## 1. Executive Summary & Verdict

| Dimension | Finding | Assessment |
| :--- | :--- | :--- |
| **Overall Recommendation** | **Supplement / Synthetic Expansion** | **Conditional**: Useful for taxonomy & structural simulation, but **unsuitable as a standalone training source** for free-text NLP or reliable priority modeling. |
| **Text Classification** | **Deficient** | No citizen-submitted narrative descriptions exist in the open portal export. Only pre-defined catalog service codes (`SR_TYPE_DESC`) exist. |
| **Priority Classification** | **Critically Imbalanced & Procedural** | 96.9% of records are labeled `STANDARD`, 2.9% `HAZARDOUS`, and 0.2% `PRIORITY`. Reflects municipal internal SLA dispatch rather than citizen urgency. |
| **Department Routing** | **Strong & Feasible** | `DEPT_NAME` maps cleanly from service request categories and offers realistic municipal departments (Public Services, Buildings, Health, Transportation). |

---

## 2. Dataset Schema & Structure Analysis

- **Total records inspected**: 1,000 active service request records fetched via the official Socrata API.
- **Total columns**: 67 fields (full municipal schema contains 70 fields).
- **Exact duplicate rows**: 0.

### Key Candidate Fields
1. **`SR_TYPE_DESC` (Service Request Description / Category)**:
   - 117 distinct classes in 1,000 rows.
   - Top classes: `METAL FURNITURE, SPEC COLLECTN` (32.1%), `TRASH, BULK ITEM PICK-UP` (23.4%), `TRASH, MISSED COLLECTION` (2.7%), `BUILDING, RESIDENTIAL` (2.4%).
   - *Observation*: These strings are municipal catalog labels assigned during triage/entry, not citizen grievance narratives.
2. **`PRIORITY` (Urgency level)**:
   - Only 3 unique labels: `STANDARD` (969 rows / 96.9%), `HAZARDOUS` (29 rows / 2.9%), `PRIORITY` (2 rows / 0.2%).
   - Missing: 0 rows.
   - *Observation*: Extreme class imbalance; training a general classifier on this target will collapse to predicting `STANDARD` without severe artificial reweighting.
3. **`DEPT_NAME` (Department / Agency)**:
   - 12 unique departments: `PUBLIC SERVICES` (79.2%), `CINC BUILDING DEPT` (6.7%), `DEPT OF TRANS AND ENG` (3.9%), `CINC HEALTH DEPT` (3.8%), `CITY MANAGER'S OFFICE` (2.3%), `EMERGENCY COMMUNICATIONS` (1.2%), etc.
   - Missing: 0 rows.
   - *Observation*: Excellent candidate for department routing rules and hierarchical classification baselines.

---

## 3. Critical Limitations for CivicLens AI

### A. Absence of Free-Text Grievance Narratives
CivicLens AI's core mission is **Explainable Public Grievance Intelligence**, where citizens describe a real-world problem (e.g., *"There is a deep pothole near the school crossing causing severe traffic hazards"*).
- The Cincinnati 311 dataset provides structured catalog selections (e.g., `POTHOLE, REPAIR`).
- Training an NLP classifier solely on the category title itself produces circular trivial identity matching (predicting the label from its own name).

### B. SLA / Municipal Procedure vs. Real Urgency
The `PRIORITY` field reflects Cincinnati's internal dispatch scheduling (e.g., bulk trash collections scheduled as `STANDARD`). It does **not** reflect citizen urgency or grievance severity under Indian public administration standards (e.g., CPGRAMS guidelines where human safety, public health, and basic amenities dictate priority).

### C. Legal & Privacy Considerations
- **License**: Public Domain (City of Cincinnati).
- **Privacy**: The public export scrubs citizen identities (names, phone numbers). Addresses and coordinates are preserved.

---

## 4. Recommended AI/ML Strategy

1. **Category Classification**:
   - Utilize standard public administration complaint categories (e.g., Sanitation, Roads & Traffic, Water Supply, Electricity, Public Health).
   - Augment municipal category titles with synthetic/curated natural language citizen complaint narratives reflecting realistic variability, slang, and phrasing.
2. **Priority Prediction**:
   - Do **not** train a black-box model on Cincinnati's `PRIORITY` column.
   - Implement an **Explainable Rule-Based Urgency Engine** based on grievance indicators (e.g., hazards, safety risks, elderly/hospital impact) coupled with human-in-the-loop review.
3. **Department Recommendation**:
   - Use a clear category-to-department routing matrix (e.g., Sanitation $\rightarrow$ Public Health & Sanitation Dept; Potholes $\rightarrow$ Public Works / Engineering).
