# USER & UNDERWRITER OPERATING MANUAL
## CredX AI — Explainable Credit Risk Platform

**Document ID:** USR-001  
**Version:** 1.0.0  

---

### 1. Navigating the Underwriting Cockpit

#### Portfolio Dashboard
- High-level overview of total applications, approval rates, average portfolio default probability, and total requested capital.
- Distribution graphs for loan purposes and calibrated risk tiers (`Low`, `Medium`, `High`, `Critical`).

#### Applications Pipeline
- Review all submitted credit applications.
- Filter by status (`SUBMITTED`, `ASSESSED`, `APPROVED`, `REJECTED`, `ESCALATED`).
- Search by applicant name, email, or application reference ID (`CRX-2026-XXXX`).

#### Submitting a New Loan Application
1. Click **+ New Loan Application** in the top navigation bar.
2. Fill in applicant demographics, employment length, home ownership, and income.
3. Enter loan parameters: requested principal, interest rate, loan intent.
4. Input credit bureau indicators: FICO credit score, debt-to-income (DTI), credit card revolving utilization, delinquencies in the past 2 years, prior default flag, and credit history length.
5. Click **Submit & Run XAI Scoring**. The system automatically computes the default probability, credit risk score, SHAP attributions, and opens the applicant profile.

#### Interpreting Explainable AI (XAI) & SHAP
- **Credit Score Gauge**: Maps calibrated Probability of Default (PD) to standard 300 - 850 credit score scale.
- **XAI Executive Narrative**: Plain English bullet points summarizing the core drivers behind the prediction.
- **SHAP Waterfall Attribution**:
  - **Red / Orange bars**: Features increasing default risk (e.g. high revolving balance, high DTI).
  - **Green / Cyan bars**: Protective features lowering risk (e.g. high credit score, high income, lengthy employment).
- **FCRA / ECOA Adverse Action Notice**: Automatically populated for high-risk applications, listing specific consumer reason codes required by regulatory law.
- **Interactive "What-If" Sensitivity Simulator**: Adjust utilization, DTI, or loan amount sliders to see the applicant's score adjust in real time.
- **Actionable Counterfactual Scenarios**: Concrete remediation milestones (e.g., "Paying down credit cards to 25% utilization lowers default risk by 49.5%").

#### Human-in-the-Loop Decisioning
- Underwriters can click **Approve Loan**, **Reject Loan**, or **Escalate to Committee**.
- If departing from the AI recommendation (e.g. approving an application flagged as Reject), the system enforces a mandatory **Override Justification Note** that is saved permanently in the regulatory audit trail.

