# RESPONSIBLE AI, FAIRNESS & REGULATORY COMPLIANCE
## CredX AI — Explainable Credit Risk Platform

**Document ID:** GOV-001  
**Version:** 1.0.0  

---

### 1. Regulatory Context
Lending algorithms operate under stringent regulatory mandates worldwide:
- **Equal Credit Opportunity Act (ECOA) & Regulation B (12 CFR Part 1002)**: Creditors are prohibited from discriminating on prohibited bases (age, race, marital status, gender, religion, national origin). If an application is denied or terms offered are unfavorable, creditors must provide a specific statement of reasons ("Adverse Action Notice").
- **Fair Credit Reporting Act (FCRA)**: Requires disclosure of key negative factors that adversely affected the credit score used in the decision.
- **European Union AI Act (Regulation 2024/1689)**: Classifies credit scoring and creditworthiness assessment AI as **High-Risk AI Systems** (Annex III, point 5b). High-risk AI systems must implement:
  - Robust risk management and data governance.
  - Technical documentation and automated logging.
  - Transparency and provision of clear information to deployers.
  - Human oversight mechanisms (Human-in-the-Loop / Human-on-the-Loop).
  - High levels of accuracy, robustness, and cybersecurity.
- **Basel III / IV Framework**: Standards for internal ratings-based (IRB) approaches to credit risk, capital adequacy calculations, and stress testing.

---

### 2. Fair Lending & Disparate Impact Evaluation

CredX AI implements quantitative fairness metrics:
1. **Demographic Parity / Statistical Parity**:
   $$P(\hat{Y} = 1 | A = a) = P(\hat{Y} = 1 | A = b)$$
   The probability of receiving a favorable outcome (e.g. loan approval) should not unfairly diverge between demographic groups.

2. **Disparate Impact Ratio (DIR) / Four-Fifths Rule (80% Rule)**:
   $$\text{DIR} = \frac{P(\text{Approved} | \text{Unprivileged Group})}{P(\text{Approved} | \text{Privileged Group})}$$
   Under US EEOC and CFPB enforcement guidelines, a selection rate for any group that is less than four-fifths (80%) of the rate for the highest group will generally be regarded as evidence of adverse impact.

3. **CredX Fairness Auditing Pipeline**:
   - The platform evaluates approval rates across age segments:
     - Young Applicants (Age < 25)
     - Core Working Age (Age 25 - 60)
     - Senior Applicants (Age > 60)
   - The dashboard dynamically surfaces the DIR metric. If DIR < 0.80, the system triggers a **Fairness Alert** for compliance officers.

---

### 3. Explainability Standard (SHAP & Adverse Action Generation)

1. **SHAP (SHapley Additive exPlanations)**:
   - Rooted in cooperative game theory, Shapley values allocate credit among input features toward the prediction output:
     $$f(x) = \phi_0 + \sum_{i=1}^M \phi_i(x)$$
   - Each feature $i$ receives a contribution $\phi_i$, representing its positive or negative push relative to base expected portfolio risk.

2. **Adverse Action Reason Extraction**:
   - For applications in `HIGH` or `CRITICAL` risk tiers, CredX extracts the top 4 negative Shapley features.
   - These are mapped to consumer-friendly, CFPB-standard adverse action descriptions:
     - `high_debt_to_income`: "Proportion of monthly debt obligations relative to income is too high."
     - `high_revolving_utilization`: "Excessive credit balance relative to available revolving credit limits."
     - `delinq_2yrs`: "Delinquent past payment history reported on credit accounts within the last 24 months."
     - `cb_person_default_on_file`: "Previous derogatory credit record or bankruptcy on file."
     - `low_credit_score`: "Credit bureau score does not meet prime risk underwriting threshold."

3. **Counterfactual Guidance ("What-If" Analysis)**:
   - Rather than an opaque rejection, applicants receive concrete remedial milestones:
     - "Reducing credit card balances by \$2,800 decreases credit utilization below 30%, which is estimated to reduce default probability from 38% to 19%."

