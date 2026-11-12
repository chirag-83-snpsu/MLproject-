# DATA DICTIONARY & DATABASE SCHEMA
## CredX AI — Explainable Credit Risk Platform

**Document ID:** DATA-001  
**Version:** 1.0.0  

---

### 1. Credit Risk Feature Set

| Feature Name | Type | Description | Range / Categories | Impact Direction on Default Risk |
|---|---|---|---|---|
| `person_age` | Integer | Applicant age in years | 18 - 85 | Generally higher risk for younger/inexperienced credit histories |
| `person_income` | Float | Annual personal income in USD | $10,000 - $500,000 | Inversely proportional: Higher income lowers default risk |
| `person_emp_length` | Float | Employment duration in years | 0.0 - 45.0 | Inversely proportional: Stable employment reduces risk |
| `person_home_ownership` | String | Residence ownership status | `RENT`, `OWN`, `MORTGAGE`, `OTHER` | `OWN` lowest risk, `RENT` moderate risk |
| `loan_intent` | String | Purpose of loan | `PERSONAL`, `EDUCATION`, `MEDICAL`, `VENTURE`, `HOMEIMPROVEMENT`, `DEBTCONSOLIDATION` | `DEBTCONSOLIDATION` & `MEDICAL` historically higher risk |
| `loan_grade` | String | Internal credit grade | `A`, `B`, `C`, `D`, `E`, `F`, `G` | Grade `A` lowest risk, `G` highest risk |
| `loan_amnt` | Float | Requested loan amount in USD | $1,000 - $100,000 | Higher principal increases risk exposure |
| `loan_int_rate` | Float | Loan interest rate (%) | 4.0% - 32.0% | Higher interest rate increases monthly payment burden |
| `loan_percent_income` | Float | Loan amount as a % of annual income | 0.01 - 0.85 | Above 0.40 significantly increases default probability |
| `cb_person_default_on_file` | String | Historical default on credit record | `Y`, `N` | `Y` is a strong positive driver of default risk |
| `cb_person_cred_hist_length` | Integer | Credit bureau history length (years) | 1 - 40 | Longer seasoning typically reduces risk |
| `credit_score` | Integer | Standard bureau credit score (FICO proxy) | 300 - 850 | Below 580: Poor; 580-669: Fair; 670-739: Good; 740-799: Very Good; 800+: Exceptional |
| `debt_to_income_ratio` | Float | Total monthly debt obligations / Gross monthly income | 0.05 - 0.75 | Above 0.43 triggers underwriting scrutiny |
| `revolving_utilization` | Float | Credit card balance / Total limit (%) | 0.0% - 100.0% | Above 50% signals credit distress |
| `delinq_2yrs` | Integer | Number of 30+ days delinquent payments in past 2 years | 0 - 15 | Greater than 1 indicates repayment instability |

---

### 2. Entity-Relationship (ER) Schema

#### Entity: `users`
- `id` (PK, Integer, Autoincrement)
- `email` (String, Unique, Index)
- `hashed_password` (String)
- `full_name` (String)
- `role` (Enum: `loan_officer`, `risk_analyst`, `compliance_officer`, `admin`)
- `is_active` (Boolean, Default True)
- `created_at` (DateTime)

#### Entity: `loan_applications`
- `id` (PK, Integer, Autoincrement)
- `application_number` (String, Unique, Indexed) e.g. `CRX-2026-0042`
- `applicant_name` (String)
- `applicant_email` (String)
- `applicant_phone` (String)
- `person_age` (Integer)
- `person_income` (Float)
- `person_emp_length` (Float)
- `person_home_ownership` (String)
- `loan_intent` (String)
- `loan_grade` (String)
- `loan_amnt` (Float)
- `loan_int_rate` (Float)
- `credit_score` (Integer)
- `debt_to_income_ratio` (Float)
- `revolving_utilization` (Float)
- `delinq_2yrs` (Integer)
- `cb_person_default_on_file` (String)
- `cb_person_cred_hist_length` (Integer)
- `status` (Enum: `SUBMITTED`, `ASSESSED`, `APPROVED`, `REJECTED`, `ESCALATED`)
- `created_by_user_id` (FK -> `users.id`)
- `created_at` (DateTime)
- `updated_at` (DateTime)

#### Entity: `credit_assessments`
- `id` (PK, Integer, Autoincrement)
- `application_id` (FK -> `loan_applications.id`, Unique)
- `model_version` (String)
- `probability_of_default` (Float, 0.0 - 1.0)
- `credit_risk_score` (Integer, 300 - 850)
- `risk_tier` (Enum: `LOW`, `MEDIUM`, `HIGH`, `CRITICAL`)
- `system_recommendation` (Enum: `APPROVE`, `MANUAL_REVIEW`, `REJECT`)
- `expected_loss` (Float)
- `shap_values_json` (Text / JSON): Array of feature contributions
- `top_risk_drivers_json` (Text / JSON): Top negative and positive factors
- `adverse_action_reasons_json` (Text / JSON): FCRA compliant reason codes
- `counterfactual_recommendation` (Text): Human-readable guidance
- `assessed_at` (DateTime)

#### Entity: `underwriter_decisions`
- `id` (PK, Integer, Autoincrement)
- `application_id` (FK -> `loan_applications.id`)
- `decided_by_user_id` (FK -> `users.id`)
- `final_decision` (Enum: `APPROVED`, `REJECTED`, `ESCALATED`)
- `is_override` (Boolean)
- `override_reason` (Text)
- `notes` (Text)
- `decided_at` (DateTime)

#### Entity: `audit_logs`
- `id` (PK, Integer, Autoincrement)
- `user_id` (Integer, Nullable)
- `action` (String) e.g., `USER_LOGIN`, `SUBMIT_APPLICATION`, `RUN_ASSESSMENT`, `OVERRIDE_DECISION`
- `entity_type` (String) e.g., `LoanApplication`, `CreditAssessment`
- `entity_id` (String)
- `details_json` (Text / JSON)
- `ip_address` (String)
- `timestamp` (DateTime)

