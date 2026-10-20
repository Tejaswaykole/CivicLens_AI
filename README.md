
<div align="center">

# CivicLens AI
### Explainable Public Grievance Intelligence

**Transforming Public Complaints into Transparent, Actionable Outcomes**

An intelligent civic grievance management platform designed to streamline complaint prioritization, departmental coordination, resolution tracking, and public accountability.

<br/>

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)
![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=for-the-badge&logo=typescript&logoColor=white)


[Overview](#-overview) •
[Problem Statement](#-problem-statement) •
[Features](#-key-features) •
[Architecture](#-system-architecture) •
[Technology](#-technology-stack) •
[Installation](#-getting-started) •
[API](#-api-overview) •
[Roadmap](#-future-enhancements)

</div>

---

## 📌 Overview

CivicLens AI is an AI-enabled public grievance management platform designed to improve how civic complaints are submitted, evaluated, assigned, monitored, and resolved.

Traditional grievance management workflows can suffer from delayed responses, inefficient departmental coordination, unclear prioritization, and limited visibility into complaint resolution.

CivicLens AI brings citizens, grievance officers, department officers, and system administrators together through a unified digital platform.

The system combines structured complaint management, role-based access control, audit trails, and intelligent decision-support capabilities to support more transparent and accountable public services.

### Our Vision

To make civic grievance resolution more accessible, efficient, explainable, and accountable through technology.

---

## 🎯 Problem Statement

Public authorities receive complaints concerning issues such as sanitation, road damage, water supply, waste management, and other essential civic services.

Managing these complaints effectively presents several challenges:

- **Inefficient Prioritization:** Urgent complaints can be difficult to distinguish from routine requests.
- **Delayed Assignment:** Complaints may not reach the appropriate department promptly.
- **Limited Transparency:** Citizens may not understand the progress or status of their complaints.
- **Fragmented Coordination:** Grievance officers and departments may lack a unified workflow.
- **Accountability Gaps:** Tracking actions, responsibility, and resolution history can be difficult.
- **Limited Explainability:** Complaint-prioritization decisions may lack clear supporting explanations.

### Our Objective

Develop a unified grievance intelligence platform that supports complaint prioritization, appropriate departmental assignment, transparent tracking, and verifiable resolution workflows.

---

## 💡 Our Solution

CivicLens AI organizes grievance management into five stages:

<div align="center">

| 01 | 02 | 03 | 04 | 05 |
|:---:|:---:|:---:|:---:|:---:|
| **Understand** | **Prioritize** | **Assign** | **Resolve** | **Verify** |
| Capture complaints | Assess urgency | Route to departments | Track progress | Review outcomes |

</div>

1. **Understand:** Collect and organize complaints submitted by citizens.
2. **Prioritize:** Support the identification of complaints requiring urgent attention.
3. **Assign:** Route complaints to the responsible departments and officers.
4. **Resolve:** Maintain status updates and complaint history throughout the lifecycle.
5. **Verify:** Record review outcomes and support transparent resolution tracking.

The platform is designed to bring these activities into a single, traceable workflow.

---

## ✨ Key Features

### 📝 1. Public Grievance Management

- Structured complaint submission and tracking.
- Complaint categorization and filtering.
- Complaint lifecycle and status management.
- Assignment and resolution history.
- Centralized access to grievance records.

### 🧠 2. Intelligent Prioritization and Explainability

The platform is designed to support intelligent complaint assessment and explainable prioritization.

Potential capabilities include:

- Identifying complaints that require urgent attention.
- Supporting complaint categorization.
- Providing reasons behind prioritization decisions.
- Helping officers focus on high-impact civic issues.

AI-generated predictions and explanations depend on the availability and verification of the corresponding inference pipeline.

### 🏢 3. Departmental Coordination

- Department-based complaint assignment.
- Role-aware complaint management.
- Assignment history and accountability.
- Structured coordination between grievance officers and departments.

### 📊 4. Complaint Tracking and Transparency

- Complaint status monitoring.
- Historical records of important actions.
- Review and resolution tracking.
- Audit logging for accountability.
- Improved visibility into complaint handling.

### 👥 5. Role-Based Dashboards

CivicLens AI is designed around four user roles.

| User Role | Responsibilities |
|---|---|
| **Citizen** | Submit complaints and monitor personal grievances. |
| **Grievance Officer** | Review complaints, coordinate assignments, and manage permitted workflow transitions. |
| **Department Officer** | Handle complaints within the authorized departmental scope. |
| **System Administrator** | Manage users, roles, and system-level operations. |

Role-based authorization helps restrict sensitive operations to permitted users.

### 🔐 6. Authentication and Security

The backend includes security mechanisms such as:

- Password hashing using Argon2id.
- JWT-based authentication.
- Role-based authorization.
- Rate limiting for public login and registration endpoints.
- Email-verification workflow.
- Complaint access restrictions.
- Audit logging.
- Environment-based secret configuration.

Actual email delivery requires configuring an email provider.

---

## 🏗️ System Architecture

CivicLens AI follows a modular architecture that separates the user interface, backend business logic, database operations, and AI/ML capabilities.

```text
┌─────────────────────────────────────────────────────┐
│                    USERS                            │
│                                                     │
│  Citizen | Grievance Officer | Department Officer   │
│                 System Administrator                │
└────────────────────────┬────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────┐
│                  FRONTEND                           │
│                                                     │
│            React + TypeScript + Vite                │
│                                                     │
│  Dashboards | Complaints | Assignments | Tracking   │
└────────────────────────┬────────────────────────────┘
                         │
                    REST API
                         │
                         ▼
┌─────────────────────────────────────────────────────┐
│                  BACKEND                            │
│                                                     │
│                    FastAPI                           │
│                                                     │
│  Authentication       Authorization                 │
│  Complaint Services   Department Services           │
│  Assignment Services  Review Services               │
│  Notification Services   Audit Logging              │
└────────────────────────┬────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────┐
│                 DATA LAYER                          │
│                                                     │
│              PostgreSQL Database                    │
│                                                     │
│        SQLAlchemy ORM + Alembic Migrations           │
└─────────────────────────────────────────────────────┘

             AI/ML DECISION SUPPORT
       Classification | Prioritization | Explanations

       Connected according to the implemented
                inference configuration
```

### Architecture Principles

- **Modularity:** Separate API routes, services, repositories, and data models.
- **Security:** Authentication and authorization enforced by the backend.
- **Maintainability:** Database schema changes managed through migrations.
- **Traceability:** Important actions recorded through audit logging.
- **Extensibility:** Architecture supports additional analytics and inference capabilities.

---

## 🛠️ Technology Stack

| Layer | Technologies |
|---|---|
| Frontend | React, TypeScript, Vite |
| Backend | Python, FastAPI |
| Database | PostgreSQL |
| ORM | SQLAlchemy 2.0 |
| Database Migrations | Alembic |
| Data Validation | Pydantic v2 |
| Authentication | JWT, PyJWT |
| Password Security | Argon2id |
| Testing | Pytest |
| Code Quality | Ruff |
| Database Hosting | Supabase PostgreSQL-compatible setup |

---



The repository separates the frontend, backend, and AI/ML components to support modular development and integration.

---

## 🚀 Getting Started

### Prerequisites

Ensure that the following tools are installed:

- Git
- Python version supported by the backend dependencies
- Node.js and npm
- PostgreSQL or an appropriately configured PostgreSQL-compatible database

### 1. Clone the Repository

```bash
git clone https://github.com/Tejaswaykole/CivicLens_AI.git
cd CivicLens_AI
```

### 2. Start the Frontend

Open a terminal:

```bash
cd frontend
npm install
npm run dev
```

Vite will display the local development URL.

The default is commonly:

```text
http://localhost:5173
```

### 3. Configure the Backend

Open a separate terminal:

```bash
cd backend
```

Create a Python virtual environment:

**Windows PowerShell**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

Create the local environment file:

```powershell
Copy-Item .env.example .env
```

Update the configuration using the settings documented in `backend/README.md`.

Generate a strong JWT secret:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Store the generated value in the local environment configuration.

**Never commit `.env`, database passwords, or JWT secrets to GitHub.**

### 4. Configure the Database

Configure `DATABASE_URL` with the connection details of the intended development PostgreSQL database.

Before applying migrations, verify the connection string and confirm that the database is correct.

Run:

```powershell
alembic upgrade head
```

This command applies pending migrations to the configured database. Do not execute it against an unknown or production database.

### 5. Run the Backend

Start FastAPI using a loopback address:

```powershell
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

The local backend address is:

```text
http://127.0.0.1:8000
```

The health endpoint is:

```text
http://127.0.0.1:8000/api/v1/health
```

The health check's result depends on the application configuration and database availability.

### 6. API Documentation

During local development, interactive API documentation is normally available at:

```text
http://127.0.0.1:8000/docs
```

Documentation endpoints are disabled in production unless explicitly enabled.

---

## 🔌 API Overview

The backend provides REST endpoints for authentication, complaints, departments, assignments, reviews, users, notifications, and audit records.

| Method | Endpoint | Purpose |
|---|---|---|
| `POST` | `/api/v1/auth/register` | Register a citizen account |
| `POST` | `/api/v1/auth/login` | Authenticate a user |
| `POST` | `/api/v1/auth/verify-email` | Verify an email address |
| `GET` | `/api/v1/auth/me` | Retrieve the authenticated user's profile |
| — | `/api/v1/complaints` | Complaint management |
| — | `/api/v1/departments` | Department information |
| — | `/api/v1/assignments` | Complaint assignment operations |
| — | `/api/v1/reviews` | Complaint review operations |
| — | `/api/v1/users` | User management |
| — | `/api/v1/notifications` | Notification management |
| — | `/api/v1/audit-logs` | Audit record access |

Exact HTTP methods, request schemas, and authorization requirements are defined by the backend API implementation.

---

## 🔒 Security and Access Control

Security is a central consideration in CivicLens AI.

### Authentication

The backend uses password hashing and signed JWTs to authenticate users.

### Authorization

Backend authorization rules restrict operations according to the authenticated user's role and permitted access scope.

### Complaint Privacy

Citizens are restricted to their own complaints. Department officers are restricted according to the department-level access rules implemented by the backend.

### Auditability

Important operations are recorded through audit logging to support traceability and accountability.

### Configuration Security

Sensitive credentials are provided through environment variables rather than hardcoded application settings.

### Current Security Limitations

The backend does not yet include a complete password-reset workflow, refresh-token system, token-revocation mechanism, or configured email delivery service.

These capabilities require additional work before a production deployment.

---

## 🧪 Testing and Code Quality

Run backend checks from the `backend` directory.

### Automated Tests

```powershell
pytest -rs
```

### Code Quality

```powershell
ruff check app tests alembic
```

### Python Compilation

```powershell
python -m compileall app alembic tests
```

Database-dependent tests require a PostgreSQL test database configured through `TEST_DATABASE_URL`.

The test database name must contain `_test`. Use a separate disposable test database, never the production database.

Skipped tests must be reported as skipped rather than passed.

---

## 🔄 Grievance Lifecycle

A typical grievance moves through the following workflow:

1. **Registration:** A citizen creates an account.
2. **Verification:** The citizen verifies their email address.
3. **Submission:** The citizen submits a civic complaint.
4. **Assessment:** An authorized officer reviews the complaint.
5. **Assignment:** The complaint is routed to the appropriate department.
6. **Processing:** The responsible department works on the issue.
7. **Review:** The resolution is reviewed according to the configured workflow.
8. **Tracking:** Complaint history and status updates support transparency.

Actual transitions depend on the business rules implemented in the backend.

---

## 🔮 Future Enhancements

Potential areas for continued development include:

- Real-time email notifications.
- Password reset and account recovery.
- Improved notification delivery and per-user read status.
- Advanced grievance analytics.
- Geospatial complaint visualization.
- More comprehensive end-to-end testing.
- Production deployment hardening.
- Further integration of explainable AI/ML inference.
- Expanded resolution verification workflows.

---

## 🌍 Impact

CivicLens AI is designed to support better public-service delivery by making grievance workflows more organized and traceable.

By combining structured complaint management, role-based access, departmental coordination, and explainable decision support, the platform aims to help authorities respond more effectively while giving citizens greater visibility into the handling of their complaints.

**Our goal is simple: make every grievance easier to track, every decision easier to understand, and every resolution more accountable.**

---

## 👥 Project

**Project Name:** CivicLens AI  
**Category:** Governance Technology / CivicTech / Explainable AI  
**Platform:** Web Application  
**Repository:** [Tejaswaykole/CivicLens_AI](https://github.com/Tejaswaykole/CivicLens_AI)

---

<div align="center">

### CivicLens AI
**Building a more transparent and accountable civic ecosystem.**

</div>
