# CredX AI — Explainable Credit Risk Assessment & Underwriting Platform

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.162-teal.svg)](https://fastapi.tiangolo.com)
[![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-1.9.1-orange.svg)](https://scikit-learn.org)
[![SHAP](https://img.shields.io/badge/SHAP-0.51.0-red.svg)](https://shap.readthedocs.io)
[![Tests](https://img.shields.io/badge/Tests-9%20Passed-brightgreen.svg)]()
[![License](https://img.shields.io/badge/License-Proprietary-blue.svg)]()

CredX AI is an enterprise-grade, transparent, and auditable credit risk decisioning platform designed for retail banks, commercial lenders, NBFCs, and fintech institutions. The system computes probability of default (PD), assigns calibrated credit risk scores (300-850), and decomposes predictions into local and global feature attributions using **SHAP (SHapley Additive exPlanations)**, counterfactual what-if simulations, and compliant **FCRA/ECOA Adverse Action** reason codes.

---

## Key Highlights

- **Intelligent Credit Scoring Engine**: Calibrated ensemble classifier with **0.8543 ROC-AUC**, **0.5641 KS statistic**, and **0.1023 Brier calibration score**.
- **Explainable AI (XAI) Suite**: Instant SHAP waterfall decomposition of risk-increasing vs protective factors, paired with plain-language executive narratives.
- **Fair Lending & Bias Auditing**: Automated Disparate Impact Ratio (DIR) compliance checks across protected age cohorts fulfilling the 4/5ths (80%) rule under US ECOA and EU AI Act.
- **Model Drift & Governance**: Population Stability Index (PSI) tracking to detect feature drift between training baselines and incoming applicant streams.
- **Human-in-the-Loop Cockpit**: Underwriter override workflows requiring compliance justification notes logged to a tamper-evident audit trail.
- **Interactive "What-If" Sensitivity Simulator**: Real-time slider adjustments simulating credit card pay-downs and principal reductions to guide borderline applicants to approval.

---

## Directory Structure

```text
├── backend/
│   ├── app/
│   │   ├── api/             # REST Routers (Auth, Applications, Assessment, Underwriting, Analytics, Fairness, Audit)
│   │   ├── core/            # Security (bcrypt, JWT), RBAC dependencies, Audit logging
│   │   ├── models/          # SQLAlchemy ORM models (User, LoanApplication, CreditAssessment, etc.)
│   │   ├── schemas/         # Pydantic v2 validation models
│   │   ├── config.py        # Environment settings
│   │   ├── database.py      # Database session & engine
│   │   ├── seed.py          # Demo database seeder
│   │   └── main.py          # FastAPI application entrypoint
├── ml/
│   ├── data/                # Dataset generation & benchmark credit risk dataset
│   ├── models/              # Model training, calibration, and fairness evaluation
│   │   └── model_artifacts/ # Serialized joblib models & metadata
│   └── xai/                 # SHAP TreeExplainer & Counterfactual engine
├── frontend/
│   ├── css/                 # Glassmorphic financial design system
│   ├── js/                  # SPA application & authenticated API client
│   └── index.html           # Underwriting cockpit interface
├── docs/                    # Complete IEEE/ISO standard documentation
│   ├── 01_PROJECT_PROPOSAL.md
│   ├── 02_BUSINESS_REQUIREMENTS_DOCUMENT.md
│   ├── 03_SOFTWARE_REQUIREMENTS_SPECIFICATION.md
│   ├── 04_SYSTEM_ARCHITECTURE.md
│   ├── 05_DATA_DICTIONARY_AND_SCHEMA.md
│   ├── 06_RESPONSIBLE_AI_AND_COMPLIANCE.md
│   ├── 07_TEST_PLAN_AND_EVALUATION.md
│   ├── 08_DEPLOYMENT_AND_OPERATIONS.md
│   └── 09_USER_MANUAL.md
├── tests/                   # Pytest test suite (100% pass rate)
├── Dockerfile               # Container build configuration
├── docker-compose.yml       # Production orchestration
└── requirements.txt         # Pinned python dependencies
```

---

## Quickstart Guide

### 1. Run Locally
```powershell
# 1. Activate Python virtual environment
.\.venv\Scripts\activate

# 2. Start the FastAPI server
uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```

Open your browser to:
- **Cockpit UI**: `http://127.0.0.1:8000/`
- **Swagger Documentation**: `http://127.0.0.1:8000/docs`

---

## Standard Demonstration Credentials

| Role | Email | Password |
|---|---|---|
| **Senior Underwriter** | `sarah.officer@credx.ai` | `Officer@123` |
| **Quantitative Risk Analyst** | `david.analyst@credx.ai` | `Analyst@123` |
| **Compliance Officer** | `elena.compliance@credx.ai` | `Compliance@123` |
| **System Administrator** | `admin@credx.ai` | `Admin@123` |

---

## Verification & Test Results

Run all test suites with:
```powershell
.\.venv\Scripts\pytest -v tests/
```

Results: **9 Passed (100%) in 6.5s**
- Health check & API routes: Verified
- JWT Authentication & RBAC: Verified
- Credit Risk ML & Calibration: Verified
- SHAP Feature Attributions & Adverse Actions: Verified
- What-If Counterfactuals: Verified
- 4/5ths Rule & Disparate Impact Auditing: Verified

