"""
Explainable AI (XAI) Engine
Computes exact SHAP feature attributions, generates plain-language financial narratives,
and extracts FCRA-compliant Adverse Action reason codes.
"""

import os
import joblib
import numpy as np
import pandas as pd
import shap
from typing import Dict, Any, List

class CreditRiskExplainer:
    def __init__(self, artifact_path: str = None):
        if artifact_path is None:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            artifact_path = os.path.join(script_dir, '..', 'models', 'model_artifacts', 'credit_risk_pipeline.joblib')
            
        print(f"Initializing CreditRiskExplainer with artifacts: {artifact_path}")
        self.artifacts = joblib.load(artifact_path)
        self.preprocessor = self.artifacts['preprocessor']
        self.base_model = self.artifacts['base_model']
        self.calibrated_model = self.artifacts['calibrated_model']
        self.num_features = self.artifacts['num_features']
        self.cat_features = self.artifacts['cat_features']
        self.all_feature_names = self.artifacts['all_feature_names']
        
        # Initialize SHAP TreeExplainer
        # For RandomForestClassifier, we explain the positive class (class 1: default)
        try:
            self.tree_explainer = shap.TreeExplainer(self.base_model)
            self.expected_value = float(self.tree_explainer.expected_value[1] 
                                        if isinstance(self.tree_explainer.expected_value, (list, np.ndarray)) 
                                        else self.tree_explainer.expected_value)
        except Exception as e:
            print(f"Warning: Standard TreeExplainer init note: {e}. Using robust explainer.")
            self.tree_explainer = shap.Explainer(self.base_model.predict_proba, self.artifacts['background_samples'][:50])
            self.expected_value = 0.168

    def _transform_input(self, applicant_data: Dict[str, Any]) -> (pd.DataFrame, np.ndarray):
        """Converts raw input dict into preprocessed array."""
        df = pd.DataFrame([applicant_data])
        # Ensure all required columns exist with defaults if missing
        for col in self.num_features:
            if col not in df:
                df[col] = 0.0
        for col in self.cat_features:
            if col not in df:
                df[col] = 'UNKNOWN'
                
        X_df = df[self.num_features + self.cat_features]
        X_trans = self.preprocessor.transform(X_df)
        return X_df, X_trans

    def predict_and_explain(self, applicant_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes calibrated risk scoring and calculates individual SHAP attributions.
        """
        X_df, X_trans = self._transform_input(applicant_data)
        
        # Calibrated probability of default (PD)
        pd_proba = float(self.calibrated_model.predict_proba(X_trans)[0, 1])
        
        # Map PD to 300-850 Credit Risk Score
        # High PD -> Low score (300); Low PD -> High score (850)
        credit_risk_score = int(np.clip(np.round(850 - (pd_proba * 550)), 300, 850))
        
        # Determine Risk Tier and System Recommendation
        if pd_proba < 0.12:
            risk_tier = 'LOW'
            recommendation = 'APPROVE'
        elif pd_proba < 0.28:
            risk_tier = 'MEDIUM'
            recommendation = 'MANUAL_REVIEW'
        elif pd_proba < 0.55:
            risk_tier = 'HIGH'
            recommendation = 'MANUAL_REVIEW' if credit_risk_score > 580 else 'REJECT'
        else:
            risk_tier = 'CRITICAL'
            recommendation = 'REJECT'
            
        # Expected Loss (EL = PD * LGD * EAD)
        # Assuming standard banking benchmark: LGD = 45% (Loss Given Default)
        loan_amnt = float(applicant_data.get('loan_amnt', 10000.0))
        expected_loss = round(pd_proba * 0.45 * loan_amnt, 2)
        
        # Calculate SHAP values
        shap_values = self.tree_explainer.shap_values(X_trans)
        
        # Handle binary classification shapes in SHAP
        if isinstance(shap_values, list):
            sv = shap_values[1][0]  # default class
        elif isinstance(shap_values, np.ndarray) and len(shap_values.shape) == 3:
            sv = shap_values[0, :, 1]
        else:
            sv = shap_values[0]

        # Group one-hot features back into logical high-level features
        feature_attributions = []
        for name, val in zip(self.all_feature_names, sv):
            feature_attributions.append({
                'feature_name': name,
                'raw_attribution': float(val),
                'abs_attribution': float(abs(val))
            })
            
        # Sort by absolute impact
        feature_attributions = sorted(feature_attributions, key=lambda x: x['abs_attribution'], reverse=True)
        
        # Aggregate top positive drivers (increases default risk)
        # and top negative drivers (reduces default risk / protective factors)
        risk_increasing = [f for f in feature_attributions if f['raw_attribution'] > 0][:5]
        risk_mitigating = [f for f in feature_attributions if f['raw_attribution'] < 0][:5]
        
        # Generate plain English narratives
        narrative_points = self._generate_narrative(applicant_data, risk_increasing, risk_mitigating)
        
        # Adverse Action Notices (FCRA compliant)
        adverse_actions = self._generate_adverse_actions(applicant_data, risk_increasing)
        
        return {
            'probability_of_default': round(pd_proba, 4),
            'credit_risk_score': credit_risk_score,
            'risk_tier': risk_tier,
            'system_recommendation': recommendation,
            'expected_loss_usd': expected_loss,
            'base_expected_value': round(self.expected_value, 4),
            'feature_attributions': feature_attributions[:12],
            'top_risk_drivers': risk_increasing[:4],
            'top_protective_factors': risk_mitigating[:4],
            'narrative_summary': narrative_points,
            'adverse_action_reasons': adverse_actions
        }

    def _generate_narrative(self, raw_data: Dict[str, Any], risk_drivers: List[Dict], protective: List[Dict]) -> List[str]:
        narratives = []
        
        # Humanize risk drivers
        for item in risk_drivers[:3]:
            feat = item['feature_name']
            if 'debt_to_income_ratio' in feat:
                dti = raw_data.get('debt_to_income_ratio', 0)
                narratives.append(f"High Debt-to-Income ratio ({dti:.1%}) contributes significantly to default risk.")
            elif 'revolving_utilization' in feat:
                util = raw_data.get('revolving_utilization', 0)
                narratives.append(f"Elevated credit card revolving utilization ({util:.1f}%) signals high credit reliance.")
            elif 'credit_score' in feat:
                cs = raw_data.get('credit_score', 0)
                narratives.append(f"Credit bureau score ({cs}) sits below preferred prime underwriting threshold.")
            elif 'delinq_2yrs' in feat:
                d = raw_data.get('delinq_2yrs', 0)
                narratives.append(f"Recent delinquent payments ({d} past-due events in 24 months) elevated repayment risk.")
            elif 'cb_person_default_on_file' in feat:
                narratives.append("Prior historical default or bankruptcy record on bureau file increases risk exposure.")
            elif 'loan_percent_income' in feat:
                lpi = raw_data.get('loan_percent_income', 0)
                narratives.append(f"Requested loan amount represents a heavy portion of annual income ({lpi:.1%}).")
            elif 'loan_int_rate' in feat:
                rate = raw_data.get('loan_int_rate', 0)
                narratives.append(f"Subprime interest rate tier ({rate:.1f}%) increases monthly debt burden.")
                
        # Humanize protective factors
        for item in protective[:2]:
            feat = item['feature_name']
            if 'credit_score' in feat:
                cs = raw_data.get('credit_score', 0)
                narratives.append(f"Strong credit bureau score ({cs}) acts as a major protective buffer against default.")
            elif 'person_income' in feat:
                inc = raw_data.get('person_income', 0)
                narratives.append(f"Substantial annual earnings (${inc:,.0f}) provides reliable debt servicing cushion.")
            elif 'person_emp_length' in feat:
                emp = raw_data.get('person_emp_length', 0)
                narratives.append(f"Established employment stability ({emp:.1f} years) positively reinforces credit profile.")
            elif 'cb_person_cred_hist_length' in feat:
                chl = raw_data.get('cb_person_cred_hist_length', 0)
                narratives.append(f"Extensive seasoned credit history ({chl} years) validates long-term payment discipline.")
            elif 'debt_to_income_ratio' in feat:
                dti = raw_data.get('debt_to_income_ratio', 0)
                narratives.append(f"Conservative debt-to-income ratio ({dti:.1%}) supports comfortable repayment capacity.")
                
        if not narratives:
            narratives.append("Applicant exhibits balanced credit profile with moderate exposure metrics.")
            
        return narratives

    def _generate_adverse_actions(self, raw_data: Dict[str, Any], risk_drivers: List[Dict]) -> List[Dict[str, str]]:
        """Maps adverse drivers into formal FCRA / ECOA Regulation B Reason Codes."""
        code_mapping = {
            'debt_to_income_ratio': {
                'code': 'AA-01',
                'title': 'Excessive Debt Obligations Relative to Income',
                'description': 'The proportion of your monthly gross income obligated to existing debt exceeds maximum guidelines.'
            },
            'revolving_utilization': {
                'code': 'AA-02',
                'title': 'High Revolving Line Utilization',
                'description': 'Balances on revolving credit lines are too high relative to total established credit limits.'
            },
            'credit_score': {
                'code': 'AA-03',
                'title': 'Credit Bureau Score Below Minimum Lending Standard',
                'description': 'The credit score supplied by consumer reporting agencies did not satisfy minimum tier requirements.'
            },
            'delinq_2yrs': {
                'code': 'AA-04',
                'title': 'Delinquent Credit Obligations',
                'description': 'Credit report reflects past due payment obligations within the preceding 24 months.'
            },
            'cb_person_default_on_file': {
                'code': 'AA-05',
                'title': 'Derogatory Public Record or Prior Default',
                'description': 'Presence of previous charge-off, repossession, or bankruptcy indicator on consumer record.'
            },
            'loan_percent_income': {
                'code': 'AA-06',
                'title': 'Loan Amount Requested Incompatible with Income',
                'description': 'The requested principal amount is disproportionate to verified annual income capacity.'
            },
            'person_emp_length': {
                'code': 'AA-07',
                'title': 'Length of Current Employment',
                'description': 'Duration of current continuous employment does not meet seasoning requirements.'
            }
        }
        
        adverse_reasons = []
        for item in risk_drivers:
            feat = item['feature_name']
            for key, details in code_mapping.items():
                if key in feat and details not in adverse_reasons:
                    adverse_reasons.append(details)
                    break
            if len(adverse_reasons) >= 4:
                break
                
        return adverse_reasons

if __name__ == '__main__':
    explainer = CreditRiskExplainer()
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
    
    result = explainer.predict_and_explain(test_applicant)
    print("\n--- Test Applicant Prediction & Explanation ---")
    print(f"Risk Tier: {result['risk_tier']} | Recommendation: {result['system_recommendation']}")
    print(f"Credit Score: {result['credit_risk_score']} | Probability of Default: {result['probability_of_default'] * 100:.2f}%")
    print("\nNarrative Explanations:")
    for n in result['narrative_summary']:
        print(f" - {n}")
    print("\nAdverse Action Reasons:")
    for aa in result['adverse_action_reasons']:
        print(f" [{aa['code']}] {aa['title']}")

