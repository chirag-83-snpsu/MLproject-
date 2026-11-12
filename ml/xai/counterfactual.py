"""
Counterfactual & "What-If" Recommendation Engine
Generates actionable remedial steps showing applicants how to reach lower risk tiers.
"""

from typing import Dict, Any, List
import copy
from .shap_explainer import CreditRiskExplainer

class CounterfactualEngine:
    def __init__(self, explainer: CreditRiskExplainer = None):
        self.explainer = explainer or CreditRiskExplainer()

    def generate_counterfactuals(self, applicant: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculates actionable scenarios to transition applicant to lower risk tiers.
        """
        baseline = self.explainer.predict_and_explain(applicant)
        base_pd = baseline['probability_of_default']
        base_score = baseline['credit_risk_score']
        base_tier = baseline['risk_tier']
        
        # If already LOW risk, no major remediation required
        if base_tier == 'LOW':
            return {
                'baseline_tier': base_tier,
                'baseline_pd': base_pd,
                'baseline_score': base_score,
                'message': "Applicant profile already qualifies for prime low-risk lending terms.",
                'scenarios': []
            }

        scenarios = []
        
        # Scenario 1: Credit Card Debt Reduction (Revolving Utilization)
        curr_util = float(applicant.get('revolving_utilization', 50.0))
        if curr_util > 30.0:
            target_util = 25.0
            candidate_1 = copy.deepcopy(applicant)
            candidate_1['revolving_utilization'] = target_util
            # Recalculate slightly improved DTI as card minimum payments drop
            dti_drop = (curr_util - target_util) * 0.0015
            candidate_1['debt_to_income_ratio'] = max(0.10, float(candidate_1.get('debt_to_income_ratio', 0.40)) - dti_drop)
            
            res_1 = self.explainer.predict_and_explain(candidate_1)
            pd_delta = base_pd - res_1['probability_of_default']
            score_delta = res_1['credit_risk_score'] - base_score
            
            scenarios.append({
                'id': 'SCENARIO_PAY_DOWN_CARDS',
                'title': 'Pay Down Revolving Credit Card Balances',
                'action_summary': f"Reduce credit card utilization from {curr_util:.1f}% down to {target_util:.1f}%.",
                'new_probability_of_default': res_1['probability_of_default'],
                'new_credit_risk_score': res_1['credit_risk_score'],
                'new_risk_tier': res_1['risk_tier'],
                'new_recommendation': res_1['system_recommendation'],
                'pd_reduction': round(pd_delta * 100, 2),
                'score_increase': score_delta,
                'feasibility': 'HIGH (within 30-60 days)'
            })

        # Scenario 2: Principal Reduction / Increased Down Payment
        curr_loan = float(applicant.get('loan_amnt', 10000.0))
        income = float(applicant.get('person_income', 50000.0))
        if curr_loan > 5000.0:
            reduced_loan = round(curr_loan * 0.75, -2) # 25% down payment or reduction
            candidate_2 = copy.deepcopy(applicant)
            candidate_2['loan_amnt'] = reduced_loan
            candidate_2['loan_percent_income'] = round(reduced_loan / income, 3)
            
            res_2 = self.explainer.predict_and_explain(candidate_2)
            pd_delta = base_pd - res_2['probability_of_default']
            score_delta = res_2['credit_risk_score'] - base_score
            
            scenarios.append({
                'id': 'SCENARIO_INCREASE_DOWNPAYMENT',
                'title': 'Reduce Requested Loan Principal (or Increase Down Payment)',
                'action_summary': f"Lower loan amount from ${curr_loan:,.0f} to ${reduced_loan:,.0f} (a ${(curr_loan - reduced_loan):,.0f} reduction).",
                'new_probability_of_default': res_2['probability_of_default'],
                'new_credit_risk_score': res_2['credit_risk_score'],
                'new_risk_tier': res_2['risk_tier'],
                'new_recommendation': res_2['system_recommendation'],
                'pd_reduction': round(pd_delta * 100, 2),
                'score_increase': score_delta,
                'feasibility': 'IMMEDIATE (Structuring Adjustment)'
            })

        # Scenario 3: Combined Comprehensive Remediation
        candidate_3 = copy.deepcopy(applicant)
        if curr_util > 30.0:
            candidate_3['revolving_utilization'] = 25.0
        if curr_loan > 5000.0:
            candidate_3['loan_amnt'] = round(curr_loan * 0.80, -2)
            candidate_3['loan_percent_income'] = round(candidate_3['loan_amnt'] / income, 3)
        candidate_3['debt_to_income_ratio'] = max(0.15, float(applicant.get('debt_to_income_ratio', 0.40)) * 0.80)
        
        res_3 = self.explainer.predict_and_explain(candidate_3)
        pd_delta_3 = base_pd - res_3['probability_of_default']
        score_delta_3 = res_3['credit_risk_score'] - base_score
        
        scenarios.append({
            'id': 'SCENARIO_COMPREHENSIVE',
            'title': 'Comprehensive Restructuring (Lower Debt + Targeted Loan Amount)',
            'action_summary': f"Reduce utilization to 25%, streamline monthly debt obligations by 20%, and adjust loan to ${candidate_3['loan_amnt']:,.0f}.",
            'new_probability_of_default': res_3['probability_of_default'],
            'new_credit_risk_score': res_3['credit_risk_score'],
            'new_risk_tier': res_3['risk_tier'],
            'new_recommendation': res_3['system_recommendation'],
            'pd_reduction': round(pd_delta_3 * 100, 2),
            'score_increase': score_delta_3,
            'feasibility': 'MODERATE (Structured Rehabilitation Plan)'
        })

        return {
            'baseline_tier': base_tier,
            'baseline_pd': base_pd,
            'baseline_score': base_score,
            'scenarios': scenarios
        }

if __name__ == '__main__':
    engine = CounterfactualEngine()
    test_applicant = {
        'person_age': 29,
        'person_income': 48000.0,
        'person_emp_length': 3.0,
        'person_home_ownership': 'RENT',
        'loan_intent': 'DEBTCONSOLIDATION',
        'loan_grade': 'D',
        'loan_amnt': 18000.0,
        'loan_int_rate': 16.5,
        'loan_percent_income': 0.375,
        'credit_score': 590,
        'debt_to_income_ratio': 0.48,
        'revolving_utilization': 78.5,
        'delinq_2yrs': 1,
        'cb_person_default_on_file': 'N',
        'cb_person_cred_hist_length': 6
    }
    
    cf = engine.generate_counterfactuals(test_applicant)
    print("\n--- Counterfactual Scenarios ---")
    for s in cf['scenarios']:
        print(f"\n[{s['title']}]")
        print(f"Action: {s['action_summary']}")
        print(f"New PD: {s['new_probability_of_default'] * 100:.2f}% (Reduced by {s['pd_reduction']}%) | New Score: {s['new_credit_risk_score']} (+{s['score_increase']})")
        print(f"Resulting Tier: {s['new_risk_tier']} | Recommendation: {s['new_recommendation']}")

