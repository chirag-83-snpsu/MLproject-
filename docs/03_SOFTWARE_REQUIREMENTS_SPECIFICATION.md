# SOFTWARE REQUIREMENTS SPECIFICATION (SRS)
## CredX AI — Explainable Credit Risk Assessment Platform

**Document ID:** SRS-001  
**Standard:** IEEE 830 / ISO/IEC/IEEE 29148  
**Version:** 1.0.0  

---

### 1. Functional Requirements (FR)

| Req ID | Module | Title | Description | Priority |
|---|---|---|---|---|
| **FR-001** | Auth | User Authentication | Secure user login via JWT tokens with bcrypt-hashed passwords. Roles: Admin, Risk Analyst, Loan Officer, Compliance. | Must Have |
| **FR-002** | Applications | Application Submission | Form and API to submit loan applicant data (demographics, income, debts, credit history, loan purpose). | Must Have |
| **FR-003** | Applications | Application Management | View, filter, search, and paginate through submitted loan applications by status, applicant name, risk tier. | Must Have |
| **FR-004** | ML Scoring | Real-Time Risk Scoring | Compute default probability (0.0 to 1.0), credit risk score (300 to 850 scale), and risk tier (`Low`, `Medium`, `High`, `Critical`). | Must Have |
| **FR-005** | ML Scoring | Financial Metrics Engine | Auto-calculate Debt-to-Income (DTI), Payment-to-Income (PTI), and Revolving Credit Utilization. | Must Have |
| **FR-006** | XAI | SHAP Feature Attribution | Generate SHAP values for applicant features showing direction (risk-increasing vs risk-decreasing) and impact magnitude. | Must Have |
| **FR-007** | XAI | Plain-Language Explanations | Translate raw SHAP mathematical vectors into executive sentences (e.g. "High debt-to-income ratio (48%) increased risk by +18.4%"). | Must Have |
| **FR-008** | XAI | Counterfactual Simulation | "What-If" simulator allowing loan officers to test parameter tweaks (e.g. higher down payment, lower loan amount) and see new predicted score. | Must Have |
| **FR-009** | Compliance | Adverse Action Generator | Automatically draft FCRA-compliant notice with top 4 specific denial reasons for applications categorized as High/Critical. | Must Have |
| **FR-010** | Underwriting | Human Review & Override | Allow authorized underwriters to approve/reject an application with mandatory audit reason logging. | Must Have |
| **FR-011** | Analytics | Portfolio Risk Dashboard | Interactive dashboard showing risk distribution, average default probabilities, application volume, and approval trends. | Must Have |
| **FR-012** | Fairness | Bias & Fairness Audit | Calculate Disparate Impact Ratio (DIR) across age groups (young, middle-aged, senior) and evaluate against the 4/5ths (80%) rule. | Must Have |
| **FR-013** | ModelOps | Drift Monitoring | Population Stability Index (PSI) calculation to identify feature drift between training baseline and incoming live applicant stream. | Should Have |
| **FR-014** | Audit | Immutable Audit Trail | Record every application creation, assessment run, underwriter override, and login event with timestamp, user ID, and IP. | Must Have |

---

### 2. Non-Functional Requirements (NFR)

| Req ID | Category | Specification |
|---|---|---|
| **NFR-001** | **Performance** | API inference latency <= 250ms for risk assessment including XAI explanations. |
| **NFR-002** | **Security** | Zero plaintext passwords; JWT token expiration (60 mins); strict CORS policy; input sanitization against XSS & SQLi. |
| **NFR-003** | **Scalability** | Stateless REST backend capable of horizontal scaling; async I/O handlers. |
| **NFR-004** | **Reliability** | Graceful degradation: if complex XAI calculation encounters edge cases, fallback to tree feature importance or linear surrogate attribution. |
| **NFR-005** | **Explainability** | 100% of assessed applications must have auditable feature attribution records stored in the database. |
| **NFR-006** | **Usability** | WCAG 2.1 AA accessibility compliant UI, responsive layout across desktop, tablet, and mobile displays. |
| **NFR-007** | **Data Integrity** | Foreign key constraints, ACID compliance via SQLite/SQLAlchemy transactions, automated schema migrations. |

