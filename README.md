<div align="center">

# CivicLens AI
### Explainable Public Grievance Intelligence

**Making Civic Decisions More Transparent. Making Grievance Resolution More Accountable.**

An intelligent civic grievance management platform that combines complaint management, explainable machine learning, departmental coordination, and human oversight to support more transparent public services.

<br/>

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)
![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=for-the-badge&logo=typescript&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)
![Scikit-learn](https://img.shields.io/badge/Scikit--learn-F7931E?style=for-the-badge&logo=scikitlearn&logoColor=white)

**CivicTech · Governance · Explainable AI · Human-in-the-Loop Systems**

</div>

---

## 🌐 Overview

CivicLens AI is an AI-enabled public grievance management platform designed to improve how civic complaints are classified, prioritized, assigned, monitored, and resolved.

Public authorities handle complaints involving road damage, sanitation, electricity, water supply, public health, and other essential civic services. Managing these complaints efficiently requires timely prioritization, appropriate departmental routing, transparent decision-making, and accountable resolution workflows.

CivicLens AI brings these processes together through a role-based web application and an explainable AI/ML decision-support component.

The platform combines structured complaint management, secure backend services, text classification, feature-contribution explanations, and human-review workflows.

### Our Mission

To make public grievance management more intelligent, transparent, explainable, and accountable.

---

## 🎯 Problem Statement

Traditional grievance management processes can face several challenges:

- **Inefficient prioritization:** Urgent complaints may be difficult to identify among large volumes of submissions.
- **Incorrect departmental routing:** Complaints may reach the wrong department, delaying resolution.
- **Limited explainability:** Officers may lack clear explanations for automated classification and prioritization recommendations.
- **Fragmented coordination:** Citizens and departments may have limited visibility into complaint progress.
- **Accountability gaps:** Tracking assignments, decisions, and resolution history can be difficult.
- **Insufficient human oversight:** Automated predictions require a structured process for review and correction.

### Our Objective

Develop an explainable grievance intelligence platform that supports complaint classification, priority assessment, department recommendation, transparent tracking, and human-reviewed decisions.

---

## 💡 Our Solution

CivicLens AI follows a five-stage grievance workflow:

<div align="center">

| 01 | 02 | 03 | 04 | 05 |
|:---:|:---:|:---:|:---:|:---:|
| **Understand** | **Prioritize** | **Assign** | **Resolve** | **Verify** |
| Capture complaints | Assess urgency | Recommend a department | Track progress | Review outcomes |

</div>

1. **Understand:** Collect and organize incoming civic complaints.
2. **Prioritize:** Generate priority suggestions to help officers assess urgency.
3. **Assign:** Recommend the responsible department and support assignment workflows.
4. **Resolve:** Track complaint status and actions throughout the lifecycle.
5. **Verify:** Support human review, preserve decision history, and improve accountability.

The AI/ML component provides recommendations and supporting explanations. Authorized human officers retain responsibility for final administrative decisions.

---

## ✨ Key Features

### 📝 1. Public Grievance Management

- Structured complaint submission and tracking.
- Complaint categorization and filtering.
- Complaint lifecycle and status management.
- Departmental assignment workflows.
- Complaint history and audit logging.

### 🧠 2. AI-Powered Complaint Classification

The AI/ML component includes a text-classification pipeline built with Scikit-learn.

It uses TF-IDF text representations and Logistic Regression to classify civic complaints into public-service categories.

The model comparison evaluates:

- A majority-class baseline.
- Word-level TF-IDF with Logistic Regression.
- Combined word-level and character-level TF-IDF with Logistic Regression.

Character n-grams help capture variations in wording, morphological patterns, and text that differs from the training examples.

### ⚡ 3. Priority Assessment

The inference interface produces suggested priority levels based on the complaint and the configured inference logic.

Priority suggestions are intended to assist triage. They are not substitutes for emergency procedures or the judgment of authorized public officials.

### 🏢 4. Department Recommendation

The inference component maps predicted complaint categories to corresponding departments using a controlled category-to-department mapping.

This helps support consistent routing while allowing officers to review and correct recommendations.

### 🔎 5. Explainable AI

CivicLens AI provides feature-contribution explanations for classification predictions.

The linear classification model allows the system to inspect which word and character features contribute positively or negatively to a predicted category.

The inference response can include:

- Predicted complaint category.
- Suggested priority.
- Recommended department.
- Model version.
- Confidence information when available.
- Contributing text features.
- An explanation statement.
- Whether human review is required.

This design makes model outputs easier to inspect rather than treating them as unexplained predictions.

### 🧑‍⚖️ 6. Human-in-the-Loop Review

Human review is an important part of the system's design.

- Officers can review model-generated recommendations.
- Human decisions remain authoritative.
- Overrides can require a justification.
- Review outcomes can be recorded for auditability.
- Original predictions and their provenance can be retained.

The AI/ML inference component is designed to remain independent of database connections and FastAPI request handling.

### 👥 7. Role-Based Access Control

CivicLens AI supports four primary user roles.

| Role | Responsibilities |
|---|---|
| **Citizen** | Submit grievances and track personal complaints. |
| **Grievance Officer** | Review, triage, and coordinate complaints. |
| **Department Officer** | Process complaints within the authorized departmental scope. |
| **System Administrator** | Manage users, roles, and system-level operations. |

The backend enforces role-specific permissions for protected operations.

### 🔐 8. Authentication and Security

The backend implementation includes:

- Argon2id password hashing.
- JWT-based authentication.
- Role-based authorization.
- Login and registration rate limiting.
- Email-verification workflow.
- Complaint access restrictions.
- Audit logging.
- Environment-based secret management.

Actual email delivery requires a configured email provider.

---

## 📊 AI/ML Model Evaluation

CivicLens AI includes a controlled comparison of text-classification approaches using an experimental synthetic grievance dataset.

The expanded V2 dataset contains **300 synthetic complaint records across 75 templates**.

The evaluation uses a group-aware split based on complaint templates to prevent the same template from appearing in both the training and test partitions.

### Experimental Results

| Model | Accuracy | Macro F1 | Public Health F1 |
|---|---:|---:|---:|
| Majority-Class Baseline | 25.64% | 0.0816 | 0.0000 |
| Word TF-IDF + Logistic Regression | 56.41% | 0.5507 | 0.7222 |
| **Word + Character TF-IDF + Logistic Regression** | **66.67%** | **0.6639** | **0.8108** |

**Evaluation setup:** 222 training records and 78 held-out test records, with zero overlap between complaint templates in the two partitions.

### Key Findings

- Combined word and character features achieved the strongest overall results in this experiment.
- Accuracy increased by approximately 10.26 percentage points over the word-only model.
- Macro F1 increased from 0.5507 to 0.6639.
- Public Health F1 increased from 0.7222 to 0.8108.
- The combined model demonstrated sub-millisecond CPU inference in the documented benchmark.

### Why Character-Level Features Help

Character n-grams capture partial words and morphological patterns, allowing the model to recognize useful text signals when complaint wording varies.

Combining word-level and character-level features can therefore improve generalization across complaint templates not seen during training.

### Evaluation Limitations

These metrics come from an experimental synthetic dataset. They do not establish real-world municipal performance, fairness, or robustness.

Further evaluation using representative real-world complaints is necessary before operational use.

The project distinguishes complaint category classification from authoritative emergency-priority decisions. Human officers retain final responsibility for prioritization and escalation.

---

## 🏗️ System Architecture

CivicLens AI separates the frontend, backend, data layer, and AI/ML inference component.

```text
                  CITIZENS & OFFICIALS
                           |
                           v
                +----------------------+
                |       FRONTEND       |
                | React + TypeScript   |
                |        + Vite        |
                +----------+-----------+
                           |
                        REST API
                           |
                           v
                +----------------------+
                |    FASTAPI BACKEND   |
                |                      |
                | Authentication       |
                | Authorization        |
                | Complaint Services   |
                | Department Services |
                | Reviews & Audit Logs|
                +----------+-----------+
                           |
                           v
                +----------------------+
                |      POSTGRESQL      |
                | SQLAlchemy + Alembic |
                +----------------------+

                +----------------------+
                |    AI/ML INFERENCE   |
                |                      |
                | Text Classification  |
                | Priority Suggestions |
                | Department Mapping   |
                | Feature Explanations |
                | Human Review Signals |
                +----------------------+
```

### Architectural Principles

- **Modularity:** Separate application services from model inference.
- **Explainability:** Provide inspectable feature contributions.
- **Human oversight:** Preserve human authority over grievance decisions.
- **Security:** Enforce access permissions in the backend.
- **Traceability:** Maintain audit and review records.
- **Extensibility:** Support future integration of additional models and analytics.

**Integration note:** The AI/ML component provides a standalone inference interface. The documented backend complaint-creation flow does not currently invoke model inference automatically, so the complete AI-to-backend workflow requires further integration.

---

## 🛠️ Technology Stack

| Component | Technologies |
|---|---|
| Frontend | React, TypeScript, Vite |
| Backend | Python, FastAPI |
| Database | PostgreSQL |
| ORM | SQLAlchemy 2.0 |
| Database Migrations | Alembic |
| Data Validation | Pydantic v2 |
| Authentication | JWT, PyJWT |
| Password Security | Argon2id |
| Machine Learning | Scikit-learn, Logistic Regression |
| Text Processing | Word and Character TF-IDF |
| Model Persistence | Joblib |
| Data Processing | Pandas, NumPy |
| Testing | Pytest |
| Code Quality | Ruff |

---

## 🚀 Getting Started

### Prerequisites

Install the following tools:

- Git
- Node.js and npm
- Python 3.11 for the documented backend environment
- Python 3.12 for the documented AI/ML environment
- PostgreSQL for database-backed backend operation

### 1. Clone the Repository

```bash
git clone https://github.com/Tejaswaykole/CivicLens_AI.git
cd CivicLens_AI
```

### 2. Run the Frontend

Open a terminal:

```bash
cd frontend
npm install
npm run dev
```

Vite displays the local development URL in the terminal. The default is typically:

```text
http://localhost:5173
```

### 3. Configure the Backend

Open a separate terminal:

```powershell
cd backend
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Configure the environment variables in `.env`.

Generate a strong JWT secret:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Set `JWT_SECRET` to the generated value and configure `DATABASE_URL` for the intended development database.

Never commit `.env` or expose database credentials.

### 4. Configure PostgreSQL

Ensure `DATABASE_URL` points to the intended development database.

After verifying the connection settings, apply the migrations:

```powershell
alembic upgrade head
```

Do not run migrations against an unknown or production database.

### 5. Start the Backend

From the `backend` directory:

```powershell
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

The local API address is:

```text
http://127.0.0.1:8000
```

Health endpoint:

```text
http://127.0.0.1:8000/api/v1/health
```

Interactive API documentation is normally available during local development at:

```text
http://127.0.0.1:8000/docs
```

A successful startup does not guarantee that PostgreSQL is connected. The health endpoint reports database connectivity separately.

### 6. Run the AI/ML Model Comparison

Use the dedicated Python 3.12 environment documented for the AI/ML component.

From the repository root:

```powershell
& ai-ml\.venv\Scripts\python.exe ai-ml\src\v2_model_comparison.py
```

The command trains and evaluates the documented candidate pipelines on the V2 dataset.

### 7. Run the AI/ML Tests

From the repository root:

```powershell
& ai-ml\.venv\Scripts\python.exe -m pytest ai-ml\tests
```

The AI/ML test suite covers dataset validation, model comparison, feature-contribution calculations, error analysis, human-review workflows, and inference contracts.

---

## 🧪 Testing and Code Quality

### Backend Checks

Run from the `backend` directory:

```powershell
ruff check app tests alembic
python -m compileall app alembic tests
pytest -rs
```

PostgreSQL-dependent tests require `TEST_DATABASE_URL` to point to a separate disposable PostgreSQL test database whose name contains `_test`.

Skipped tests must be reported as skipped rather than passed.

### AI/ML Checks

Run from the repository root:

```powershell
& ai-ml\.venv\Scripts\python.exe -m pytest ai-ml\tests
```

The model evaluation and tests should be run in the documented AI/ML environment to maintain reproducibility.

---

## 🔒 Responsible AI and Security

CivicLens AI is designed to assist public officials, not replace their judgment.

### Human Authority

AI-generated categories, priority levels, and department recommendations are decision-support outputs. Authorized officers retain final responsibility for consequential administrative decisions.

### Explainability

Feature-contribution explanations help reviewers inspect the model's predictions and understand which textual signals influenced a classification.

### Dataset Limitations

The current reported evaluation uses synthetic complaint data. Additional representative real-world evaluation is needed to assess generalization, fairness, and operational suitability.

### Data Privacy

Real citizen complaints may contain sensitive information. Any future use of real grievance data should follow appropriate access controls, data minimization, retention policies, and privacy safeguards.

### Application Security

The backend implements authentication, authorization, rate limiting, and audit controls. Database-dependent behavior must be verified against PostgreSQL before deployment.

---

## 🌍 Expected Impact

CivicLens AI aims to support more effective public-service delivery by enabling:

- More consistent complaint categorization.
- Better visibility into grievance workflows.
- Explainable classification recommendations.
- More structured departmental coordination.
- Human-reviewed decision-making.
- Improved traceability and accountability.

By combining AI-assisted analysis with transparent workflows and human oversight, CivicLens AI explores how technology can contribute to more responsive and accountable civic services.

---

## 👥 Project Information

**Project Name:** CivicLens AI  
**Domain:** CivicTech · Governance · Explainable AI  
**Application:** Public Grievance Management and Decision Support  
**Repository:** [Tejaswaykole/CivicLens_AI](https://github.com/Tejaswaykole/CivicLens_AI)

---

<div align="center">

### CivicLens AI

**Understand the complaint. Explain the recommendation.  
Empower the decision-maker.**

</div>
