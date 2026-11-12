# TEST PLAN & VERIFICATION REPORT
## CredX AI — Explainable Credit Risk Platform

**Document ID:** TEST-001  
**Version:** 1.0.0  

---

### 1. Verification Strategy
Quality assurance was conducted across five distinct layers:
1. **Model Performance & Calibration Verification**:
   - Stratified holdout evaluation on 750 unseen credit records.
   - ROC-AUC: `0.8543` (Exceeds prime benchmark of 0.80).
   - Kolmogorov-Smirnov (KS) statistic: `0.5641` (Demonstrates strong separation between default and non-default distributions).
   - Brier Score: `0.1023` (Demonstrates sharp probability calibration).
2. **Explainability & SHAP Integrity**:
   - Verification of exact local Shapley additivity ($\sum \phi_i = f(x) - \mathbb{E}[f(X)]$).
   - Generation of FCRA adverse action codes matching top negative Shapley attributions.
3. **Fair Lending & Bias Auditing**:
   - Verification of 4/5ths (80%) rule across Age Protected Demographics.
   - Cohort `Young (< 25)`: Disparate Impact Ratio = `0.977` (PASSED).
   - Cohort `Senior (> 60)`: Disparate Impact Ratio = `1.033` (PASSED).
4. **Drift Assessment (PSI)**:
   - Population Stability Index evaluated at `0.00407` (Far below the 0.10 warning threshold).
5. **API & End-to-End Integration Testing**:
   - Automated Pytest execution covering 9 core test suites with 100% pass rate.

---

### 2. Automated Test Execution Summary

| Test Case | Module | Description | Result |
|---|---|---|---|
| `test_health_endpoint` | Health | Verifies `/health` returns status `HEALTHY` and metadata | **PASSED** |
| `test_login_success` | Auth / RBAC | Validates JWT generation and role claims for loan officer | **PASSED** |
| `test_login_invalid_password` | Auth / Security | Confirms 401 Unauthorized upon incorrect credentials | **PASSED** |
| `test_list_applications` | Applications | Verifies seeded pipeline retrieval and pagination | **PASSED** |
| `test_create_and_fetch_application` | Applications | Validates submission of new application and ID retrieval | **PASSED** |
| `test_fairness_audit_endpoint` | Governance | Asserts demographic parity, DIR calculations, and PSI status | **PASSED** |
| `test_underwriter_decision_override` | Underwriting | Verifies human-in-the-loop override and rationale logging | **PASSED** |
| `test_assessment_execution_and_shap` | ML & XAI | Asserts real-time PD scoring, 300-850 score, SHAP values | **PASSED** |
| `test_what_if_simulation` | Counterfactual | Tests dynamic parameter slider sensitivity calculations | **PASSED** |

