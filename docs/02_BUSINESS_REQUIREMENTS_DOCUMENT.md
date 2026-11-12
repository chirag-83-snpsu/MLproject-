# BUSINESS REQUIREMENTS DOCUMENT (BRD)
## CredX AI — Explainable Credit Risk Assessment Platform

**Document ID:** BRD-001  
**Project:** CredX AI Enterprise  
**Author:** Antigravity Autonomous Engineering Organization  
**Version:** 1.0.0  

---

### 1. Business Objectives
- **BO-1: Reduce Non-Performing Loans (NPLs)**: Accurately identify high-risk applicants, aiming to decrease default rates by an estimated 18-25% without sacrificing prime loan volume.
- **BO-2: Accelerate Underwriting Throughput**: Reduce average decision turnaround time from 48-72 hours to under 30 seconds for straight-through low-risk cases, while routing borderline cases for human review.
- **BO-3: Full Regulatory Compliance**: Meet US FCRA/ECOA Regulation B and European Union AI Act requirements for algorithmic transparency, adverse action notices, and bias auditing.
- **BO-4: Enhance Trust and Customer Experience**: Empower rejected or conditional applicants with actionable counterfactual steps to improve creditworthiness within 3-6 months.
- **BO-5: Model Governance & Drift Protection**: Ensure models remain reliable and recalibrated in response to macroeconomic shifts (inflation, interest rates).

---

### 2. Stakeholder & Persona Matrix

| Role | Persona Name | Key Responsibilities | Primary Needs in CredX AI |
|---|---|---|---|
| **Loan Officer** | Sarah (Commercial Lending) | Reviews applicant files, collects documents, issues credit decisions | Fast risk score, plain-English explanation, actionable summary, adverse action letters |
| **Risk Analyst** | David (Quantitative Risk) | Evaluates portfolio risk, tests model calibrations, monitors credit tiers | Cutoff threshold tuning, Expected Loss (EL) modeling, feature importance metrics |
| **Compliance Officer** | Elena (Legal & Regulatory) | Ensures fair lending compliance, audits decisions, prevents discrimination | Disparate impact reports, demographic parity analytics, audit log inspection |
| **System Admin** | Alex (IT / Platform) | Manages user accounts, assigns RBAC privileges, monitors system health | User management, secure JWT sessions, database backup, system uptime |

---

### 3. Business Workflows

#### Workflow A: Loan Application & Real-time Risk Assessment
1. Loan Officer submits loan applicant details (demographics, income, debt, employment, credit history).
2. CredX Engine runs data validation, calculates financial ratios (DTI, Installment-to-Income, Revolving Utilization).
3. The ML scoring pipeline computes Probability of Default (PD), Risk Tier (`Low`, `Medium`, `High`, `Critical`), and Recommended Action (`Approve`, `Manual Review`, `Reject`).
4. The XAI Engine extracts SHAP values to identify top positive factors (e.g., high credit score, low DTI) and negative factors (e.g., prior delinquency, high utilization).
5. If High/Critical Risk, system synthesizes an Adverse Action Summary citing key factors compliant with FCRA.
6. Counterfactual recommendation engine provides applicant advice (e.g., "Pay down credit card balance by $3,000 to drop DTI below 35%").

#### Workflow B: Human-in-the-Loop Decision Override
1. Loan Officer or Senior Underwriter can review borderline or high-risk applications.
2. Underwriter can manually approve or override model suggestion, entering a mandatory justification note.
3. The decision, model prediction, and justification are recorded permanently in the tamper-evident audit log.

#### Workflow C: Portfolio Risk & Fairness Auditing
1. Risk & Compliance officers access aggregated analytics:
   - Approval rate vs Default rate across credit score bands.
   - Demographic Parity & Disparate Impact Ratio (DIR) across age groups (e.g., young < 25 vs 25-60 vs senior > 60).
   - Population Stability Index (PSI) to detect data distribution drift.

