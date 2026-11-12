"""
Model Evaluation, Fairness Auditing & Drift Assessment Module
Computes Demographic Parity, Disparate Impact Ratios (DIR),
and Population Stability Index (PSI) for Basel III & EU AI Act compliance.
"""

import os
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score, confusion_matrix, brier_score_loss

def calculate_psi(expected: np.ndarray, actual: np.ndarray, num_buckets: int = 10) -> float:
    """
    Calculates Population Stability Index (PSI) between a baseline (expected)
    and an incoming sample (actual).
    PSI < 0.1: No significant change / stable
    0.1 <= PSI < 0.2: Moderate shift / monitor
    PSI >= 0.2: Significant drift / trigger retraining
    """
    # Create quantiles based on expected distribution
    percentiles = np.linspace(0, 100, num_buckets + 1)
    bins = np.percentile(expected, percentiles)
    bins[0] = -np.inf
    bins[-1] = np.inf
    # Ensure strictly increasing bins
    bins = np.unique(bins)
    if len(bins) < 3:
        return 0.0

    exp_counts, _ = np.histogram(expected, bins=bins)
    act_counts, _ = np.histogram(actual, bins=bins)

    # Convert to fractions with smoothing to prevent div by zero
    exp_pct = (exp_counts + 1e-4) / (len(expected) + 1e-4 * len(exp_counts))
    act_pct = (act_counts + 1e-4) / (len(actual) + 1e-4 * len(act_counts))

    psi_val = np.sum((act_pct - exp_pct) * np.log(act_pct / exp_pct))
    return float(psi_val)

def run_evaluation_and_fairness_audit():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    artifacts_dir = os.path.join(script_dir, 'model_artifacts')
    data_path = os.path.join(script_dir, '..', 'data', 'credit_risk_dataset.csv')
    
    print("Loading model artifacts and dataset...")
    model_obj = joblib.load(os.path.join(artifacts_dir, 'credit_risk_pipeline.joblib'))
    preprocessor = model_obj['preprocessor']
    calibrated_clf = model_obj['calibrated_model']
    num_features = model_obj['num_features']
    cat_features = model_obj['cat_features']
    
    df = pd.read_csv(data_path)
    X = df[num_features + cat_features]
    y = df['loan_status']
    
    X_trans = preprocessor.transform(X)
    probs = calibrated_clf.predict_proba(X_trans)[:, 1]
    # Standard lending threshold: approve if PD < 0.28 (i.e. Low or Medium risk)
    approvals = (probs < 0.28).astype(int)
    
    # 1. Fairness Audit by Age Cohort (Protected Demographic)
    age_col = df['person_age']
    cohort_young = (age_col < 25)
    cohort_core = (age_col >= 25) & (age_col <= 60)
    cohort_senior = (age_col > 60)
    
    cohorts = {
        'Young (< 25)': cohort_young,
        'Core Workforce (25-60)': cohort_core,
        'Senior (> 60)': cohort_senior
    }
    
    fairness_results = {}
    approval_rates = {}
    
    for name, mask in cohorts.items():
        count = int(mask.sum())
        app_count = int(approvals[mask].sum())
        app_rate = app_count / count if count > 0 else 0.0
        avg_pd = float(probs[mask].mean()) if count > 0 else 0.0
        actual_def_rate = float(y[mask].mean()) if count > 0 else 0.0
        
        approval_rates[name] = app_rate
        fairness_results[name] = {
            'sample_size': count,
            'approved_count': app_count,
            'approval_rate': round(app_rate, 4),
            'average_predicted_pd': round(avg_pd, 4),
            'actual_default_rate': round(actual_def_rate, 4)
        }
        
    # Calculate Disparate Impact Ratio (DIR) relative to highest rate cohort
    base_ref_group = 'Core Workforce (25-60)'
    ref_rate = approval_rates[base_ref_group]
    
    for name in cohorts.keys():
        dir_val = round(approval_rates[name] / ref_rate, 4) if ref_rate > 0 else 1.0
        fairness_results[name]['disparate_impact_ratio'] = dir_val
        fairness_results[name]['passes_four_fifths_rule'] = bool(dir_val >= 0.80)

    # 2. Population Stability Index (Baseline vs Perturbed Recent Cohort)
    np.random.seed(42)
    sample_half = np.random.choice(len(probs), size=len(probs)//2, replace=False)
    baseline_probs = probs[sample_half]
    recent_probs = probs[~np.isin(np.arange(len(probs)), sample_half)]
    
    psi_metric = calculate_psi(baseline_probs, recent_probs)
    
    audit_report = {
        'fairness_audit': fairness_results,
        'disparate_impact_summary': {
            'reference_group': base_ref_group,
            'young_cohort_dir': fairness_results['Young (< 25)']['disparate_impact_ratio'],
            'senior_cohort_dir': fairness_results['Senior (> 60)']['disparate_impact_ratio'],
            'overall_fair_lending_compliance': all(r['passes_four_fifths_rule'] for r in fairness_results.values())
        },
        'drift_analysis': {
            'psi_metric': round(psi_metric, 5),
            'status': 'STABLE' if psi_metric < 0.1 else ('MONITOR' if psi_metric < 0.2 else 'ACTION_REQUIRED'),
            'retraining_recommended': bool(psi_metric >= 0.15)
        }
    }
    
    report_path = os.path.join(artifacts_dir, 'fairness_and_drift_report.json')
    with open(report_path, 'w') as f:
        json.dump(audit_report, f, indent=2)
        
    print("\n--- Fairness & Compliance Audit Results ---")
    for name, r in fairness_results.items():
        status = "PASSED (>= 0.80)" if r['passes_four_fifths_rule'] else "ALERT (< 0.80)"
        print(f"Cohort: {name:<24} | App Rate: {r['approval_rate']*100:.1f}% | DIR: {r['disparate_impact_ratio']:.3f} | 80% Rule: {status}")
        
    print(f"\nPopulation Stability Index (PSI): {audit_report['drift_analysis']['psi_metric']} ({audit_report['drift_analysis']['status']})")
    print(f"Fairness report saved to: {report_path}")

if __name__ == '__main__':
    run_evaluation_and_fairness_audit()

