# CivicLens AI — Phase 6.1: Backend and AI/ML Inference Contract Alignment

**Document Version**: `1.0.0`  
**Date**: 2026-10-20  
**Status**: Contract Alignment & Inspection (Pre-Integration)  
**Authors**: Senior AI/ML Engineer & Backend Engineer  

---

## 1. Executive Summary & Purpose

This document establishes the official integration boundary and contract specification between:
1. **The Backend Track**: FastAPI REST API, PostgreSQL database (SQLAlchemy models), and Human-in-the-Loop (HITL) audit systems.
2. **The AI/ML Track**: Standalone, sub-millisecond grievance classification, priority triage suggestion, and linear feature explainability pipeline (`InferenceEngine`).

> [!IMPORTANT]
> **Strict Operational Boundary**:
> - The AI/ML module produces **suggestions and explainable evidence**, never authoritative administrative actions.
> - The AI/ML module is completely decoupled from database connections, PostgreSQL sessions, and FastAPI HTTP lifecycles.
> - Human grievance officers retain final authority; human-confirmed categories and priorities **must never be overwritten** by model predictions.

---

## 2. Actual Backend Implementation Inventory

An inspection of the real merged backend codebase reveals the following schema, domain models, and API endpoints:

### A. Primary Endpoints & Flow
- **Complaint Registration**:
  - `POST /api/v1/complaints` (implemented in [`backend/app/api/routes/complaints.py`](file:///t:/My%20Projects/CivicLens_AI%20Project/backend/app/api/routes/complaints.py))
  - Invokes `complaint_service.create_complaint(db, payload)`.
  - Currently receives `ComplaintCreate` and creates a `Complaint` record with initial status `ComplaintStatus.submitted`.
  - **Current AI Status**: *No model prediction is currently invoked during complaint creation.*
- **Human Priority Review & HITL Overrides**:
  - `POST /api/v1/reviews/{complaint_id}` (implemented in [`backend/app/api/routes/reviews.py`](file:///t:/My%20Projects/CivicLens_AI%20Project/backend/app/api/routes/reviews.py))
  - Uses `create_review()` in [`backend/app/services/reviews.py`](file:///t:/My%20Projects/CivicLens_AI%20Project/backend/app/services/reviews.py).
  - Queries `latest_prediction(db, complaint.id)`. If a stored prediction exists:
    - If officer confirms a different priority than `stored_priority`, requires a **`justification` string of at least 10 characters**.
    - Records an audit log with action `AuditAction.HITL_OVERRIDE` (or `AuditAction.CONCURRENCE` if matching).

### B. Backend Domain Enums & Controlled Vocabularies
Located in [`backend/app/domain/enums.py`](file:///t:/My%20Projects/CivicLens_AI%20Project/backend/app/domain/enums.py) and [`backend/app/domain/workflow.py`](file:///t:/My%20Projects/CivicLens_AI%20Project/backend/app/domain/workflow.py):

| Entity | Backend Definition | Values |
| :--- | :--- | :--- |
| **Category** | `COMPLAINT_CATEGORIES` (tuple) | `"Road Infrastructure"`, `"Water & Sewage"`, `"Electrical Hazard"`, `"Sanitation & Solid Waste"`, `"Street Lighting"` |
| **Priority** | `ComplaintPriority` (StrEnum) | `"critical"`, `"high"`, `"medium"`, `"low"` |
| **Status** | `ComplaintStatus` (StrEnum) | `"submitted"`, `"in_review"`, `"triaged"`, `"assigned"`, `"in_progress"`, `"resolved"`, `"rejected"` |
| **Suggestion Origin** | `SuggestionOrigin` (StrEnum) | `"stored_prediction"`, `"client_supplied"`, `"none"` |
| **Audit Action** | `AuditAction` (StrEnum) | `"COMPLAINT_CREATED"`, `"STATUS_CHANGE"`, `"ASSIGNMENT_CREATED"`, `"CONCURRENCE"`, `"HITL_OVERRIDE"`, `"HUMAN_REVIEW"` |

### C. Persistent Storage: `model_predictions` Table
Defined in [`backend/app/models/model_prediction.py`](file:///t:/My%20Projects/CivicLens_AI%20Project/backend/app/models/model_prediction.py):
```sql
CREATE TABLE model_predictions (
    id UUID PRIMARY KEY,
    complaint_id UUID NOT NULL REFERENCES complaints(id) ONDELETE RESTRICT,
    model_identifier VARCHAR(200) NOT NULL,
    model_version VARCHAR(50) NOT NULL,
    predicted_category VARCHAR(80) NULL,
    suggested_priority complaint_priority NULL,
    confidence NUMERIC(5, 4) NULL CHECK (confidence IS NULL OR (confidence >= 0 AND confidence <= 1)),
    explanation JSONB NULL,
    predicted_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

---

## 3. Actual AI/ML Implementation Inventory

Located in [`ai-ml/src/v2_model_comparison.py`](file:///t:/My%20Projects/CivicLens_AI%20Project/ai-ml/src/v2_model_comparison.py):
- **Candidate Model**: `Model B (Word + Character n-grams TF-IDF + LogisticRegression)`.
- **Model Identifier**: `"civiclens-category-word-char"`
- **Model Version**: `"0.2.0-word-char-logreg"`
- **Artifact Path**: `ai-ml/models/category_classifier_v2_candidate.joblib`
- **Inference Latency**: $\approx 0.42\text{ ms}$ on standard CPU.
- **Output Data Structure (`InferenceResult`)**:
  - `predicted_category`: string (`"Sanitation"`, `"Roads"`, `"Electricity"`, `"Water Supply"`, `"Public Health"`)
  - `suggested_priority`: string (`"High"`, `"Medium"`)
  - `recommended_department`: string (e.g. `"Department of Public Works"`)
  - `model_version`: string (`"0.2.0-word-char-logreg"`)
  - `requires_human_review`: boolean
  - `confidence`: float ($0.0000$ to $1.0000$)
  - `top_contributing_features`: list of dicts (token and signed float contribution)
  - `explanation_statement`: human-readable explanation

---

## 4. Field-by-Field Mapping & Adaptation Table

To bridge the AI/ML inference engine with the Backend database schema, the following transformation rules must be applied:

| AI/ML `InferenceResult` Field | Backend `ModelPrediction` / Response Field | Type Conversion & Normalization Rule |
| :--- | :--- | :--- |
| `model_version` | `model_version` (`varchar(50)`) | Direct 1:1 mapping (e.g. `"0.2.0-word-char-logreg"`). |
| *N/A (Module Constant)* | `model_identifier` (`varchar(200)`) | Injected as `"civiclens-category-word-char"`. |
| `predicted_category` | `predicted_category` (`varchar(80)`) | **Taxonomy Mapping Required** (see Section 5 below). |
| `suggested_priority` | `suggested_priority` (`ComplaintPriority` enum) | Lowercased & mapped: `"High"` $\rightarrow$ `ComplaintPriority.high`, `"Medium"` $\rightarrow$ `ComplaintPriority.medium`. |
| `confidence` | `confidence` (`Numeric(5, 4)`) | Converted to `Decimal` rounded to 4 decimal places, or `None`. |
| `top_contributing_features` + `explanation_statement` | `explanation` (`JSONB`) | Packaged as a clean dictionary: `{"statement": ..., "features": [...]}`. |
| `recommended_department` | *Complaint Assignment Recommendation* | Used by triage service to pre-select department if unassigned. |
| `requires_human_review` | `Complaint.status` / Notification Flag | If `True`, forces complaint status into `ComplaintStatus.in_review` and triggers triage notification. |

---

## 5. Critical Taxonomy & Enum Mismatches (Action Required)

### A. Category Discrepancy
The backend strictly validates against `COMPLAINT_CATEGORIES` (from the citizen UI), whereas the AI/ML model was trained on 5 municipal research categories:

| AI/ML Category Label | Backend Citizen Category (`COMPLAINT_CATEGORIES`) | Notes & Mapping Rule |
| :--- | :--- | :--- |
| **`Roads`** | `"Road Infrastructure"` | Map `Roads` $\rightarrow$ `"Road Infrastructure"` |
| **`Water Supply`** | `"Water & Sewage"` | Map `Water Supply` $\rightarrow$ `"Water & Sewage"` |
| **`Electricity`** | `"Electrical Hazard"` or `"Street Lighting"` | If subwords indicate lighting/lamps $\rightarrow$ `"Street Lighting"`; otherwise $\rightarrow$ `"Electrical Hazard"`. |
| **`Sanitation`** | `"Sanitation & Solid Waste"` | Map `Sanitation` $\rightarrow$ `"Sanitation & Solid Waste"` |
| **`Public Health`** | **Missing in Backend!** | **Mismatch**: Backend currently has no `"Public Health"` category! (Routes currently to `"Sanitation & Solid Waste"` or `"Water & Sewage"`). |

### B. Priority Scale Discrepancy
- **Backend**: 4 levels (`"low"`, `"medium"`, `"high"`, `"critical"`).
- **AI/ML**: 3 levels (`"Low"`, `"Medium"`, `"High"`).
  - Note: In AI/ML, emergency indicators trigger `"High"`.
  - Mapping rule: AI/ML `"High"` maps to Backend `ComplaintPriority.high` (or `critical` if specific fatal keywords are detected).

---

## 6. Error Handling, Edge Cases & Safety Protocols

1. **Short or Empty Complaints**:
   - If `complaint_text` has fewer than 10 characters, `InferenceEngine.predict()` returns `predicted_category="Unknown"`, `confidence=None`, and `requires_human_review=True`.
   - Backend gracefully accepts `predicted_category=None` and flags the case for manual intake.
2. **Model Load Failure**:
   - If the `.joblib` model artifact cannot be found or loaded at FastAPI startup:
     - The application **must not crash**.
     - A structured warning is logged.
     - The service operates in fallback mode (`ModelPrediction` record omitted; complaint defaults to manual triage).
3. **Probability Calibration Notice**:
   - Probabilities from `LogisticRegression.predict_proba` are **uncalibrated Platt scaling scores**. They represent relative linear decision margin, **not empirical probability of correctness**.
   - Low confidence scores must **never** be used to suppress an emergency alert.
4. **Emergency Keyword Safeguard**:
   - Words such as `sparking`, `live wire`, `sinkhole`, `fecal`, `dengue` automatically trigger `requires_human_review=True` and escalate suggested priority, regardless of classifier confidence.

---

## 7. Audit Logging and HITL Governance

Every time a human officer interacts with a complaint:
1. **Officer Agreement (`AuditAction.CONCURRENCE`)**:
   - If officer confirms `suggested_priority`, audit log captures concurrence without mandatory justification.
2. **Officer Override (`AuditAction.HITL_OVERRIDE`)**:
   - If officer overrides `suggested_priority`, `justification` ($\ge 10$ characters) is mandatory.
   - The stored prediction in `model_predictions` is **never updated or overwritten**; it remains immutable for audit history.
3. **Privacy**:
   - Audit event metadata must never log sensitive citizen identity details or raw private complaint descriptions.

---

## 8. Unresolved Decisions Requiring Backend Teammate Agreement

1. **Category Alignment**:
   - *Option 1*: Update backend `COMPLAINT_CATEGORIES` to include `"Public Health"`.
   - *Option 2*: Use an explicit mapping layer inside the AI adapter service translating AI predictions into the 5 frontend/backend categories.
2. **Invocation Lifecycle**:
   - Should AI inference be called:
     - **Synchronously** within `create_complaint` (latency is $< 1\text{ ms}$, so negligible impact on response time)?
     - Or **Asynchronously** via a background task/worker?
     - *Recommendation*: Given sub-millisecond execution, calling inference synchronously inside `create_complaint` ensures the officer dashboard immediately sees the triage suggestion upon creation.
3. **Confidence Storage**:
   - Should confidence be stored as `Decimal(0.xxxx)` or omitted when decision margin is ambiguous?
