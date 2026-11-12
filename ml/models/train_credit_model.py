"""
Production Credit Risk Model Training & Calibration Pipeline
Trains benchmark models, performs probability calibration, extracts SHAP explainers,
and evaluates credit risk metrics (ROC-AUC, Brier score, KS statistic).
"""

import os
import json
import joblib
import numpy as np
import pandas as pd
from datetime import datetime

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier
from sklearn.calibration import CalibratedClassifierCV, calibration_curve
from sklearn.metrics import (
    roc_auc_score,
    average_precision_score,
    brier_score_loss,
    f1_score,
    precision_score,
    recall_score,
    confusion_matrix,
    classification_report
)

def calculate_ks_statistic(y_true, y_prob):
    """Calculates the Kolmogorov-Smirnov (KS) statistic standard in credit risk."""
    df = pd.DataFrame({'y': y_true, 'prob': y_prob})
    df = df.sort_values(by='prob', ascending=False)
    df['cum_bads'] = df['y'].cumsum() / df['y'].sum()
    df['cum_goods'] = (1 - df['y']).cumsum() / (1 - df['y']).sum()
    ks = np.max(np.abs(df['cum_bads'] - df['cum_goods']))
    return float(ks)

def train_and_evaluate():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(script_dir, '..', 'data', 'credit_risk_dataset.csv')
    artifacts_dir = os.path.join(script_dir, 'model_artifacts')
    os.makedirs(artifacts_dir, exist_ok=True)
    
    print(f"Loading dataset from: {data_path}")
    df = pd.read_csv(data_path)
    
    # Feature columns
    num_features = [
        'person_age', 'person_income', 'person_emp_length',
        'loan_amnt', 'loan_int_rate', 'loan_percent_income',
        'credit_score', 'debt_to_income_ratio', 'revolving_utilization',
        'delinq_2yrs', 'cb_person_cred_hist_length'
    ]
    
    cat_features = [
        'person_home_ownership', 'loan_intent',
        'loan_grade', 'cb_person_default_on_file'
    ]
    
    target = 'loan_status'
    
    X = df[num_features + cat_features]
    y = df[target]
    
    # Train, validation (for calibration), test split (70% train, 15% calib, 15% test)
    X_train_full, X_test, y_train_full, y_test = train_test_split(
        X, y, test_size=0.15, random_state=42, stratify=y
    )
    X_train, X_val, y_train, y_val = train_test_split(
        X_train_full, y_train_full, test_size=0.1765, random_state=42, stratify=y_train_full
    )
    
    print(f"Dataset split: Train={len(X_train)}, Val={len(X_val)}, Test={len(X_test)}")
    
    # Preprocessor
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), num_features),
            ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), cat_features)
        ],
        remainder='drop'
    )
    
    # Fit preprocessor on training data
    preprocessor.fit(X_train)
    
    # Get feature names after transformation
    cat_encoder = preprocessor.named_transformers_['cat']
    encoded_cat_names = cat_encoder.get_feature_names_out(cat_features).tolist()
    all_feature_names = num_features + encoded_cat_names
    
    # Save transformed arrays
    X_train_trans = preprocessor.transform(X_train)
    X_val_trans = preprocessor.transform(X_val)
    X_test_trans = preprocessor.transform(X_test)
    
    # Candidate Models
    models = {
        'LogisticRegression': LogisticRegression(max_iter=1000, random_state=42, C=0.8),
        'RandomForest': RandomForestClassifier(n_estimators=150, max_depth=9, min_samples_leaf=4, random_state=42, n_jobs=-1),
        'HistGradientBoosting': HistGradientBoostingClassifier(max_iter=150, max_depth=6, min_samples_leaf=15, random_state=42)
    }
    
    results = {}
    best_model_name = None
    best_auc = -1.0
    
    print("\n--- Model Benchmark Evaluation ---")
    for name, clf in models.items():
        clf.fit(X_train_trans, y_train)
        y_prob = clf.predict_proba(X_test_trans)[:, 1]
        y_pred = (y_prob >= 0.35).astype(int)  # 0.35 default threshold for risk aversion
        
        auc = roc_auc_score(y_test, y_prob)
        pr_auc = average_precision_score(y_test, y_prob)
        brier = brier_score_loss(y_test, y_prob)
        ks = calculate_ks_statistic(y_test, y_prob)
        f1 = f1_score(y_test, y_pred)
        
        print(f"Model: {name:<22} | ROC-AUC: {auc:.4f} | PR-AUC: {pr_auc:.4f} | KS: {ks:.4f} | Brier: {brier:.4f} | F1: {f1:.4f}")
        results[name] = {
            'roc_auc': float(auc),
            'pr_auc': float(pr_auc),
            'ks_stat': float(ks),
            'brier_score': float(brier),
            'f1_score': float(f1)
        }
        
        if auc > best_auc:
            best_auc = auc
            best_model_name = name
            best_clf = clf
            
    print(f"\nSelected Best Architecture: {best_model_name} (ROC-AUC: {best_auc:.4f})")
    
    # Probability Calibration using 3-fold cross-validation
    print("Calibrating default probabilities with Sigmoid scaling (cv=3)...")
    calibrated_clf = CalibratedClassifierCV(estimator=best_clf, method='sigmoid', cv=3)
    calibrated_clf.fit(X_train_trans, y_train)
    
    # Evaluate calibrated model on test set
    test_probs = calibrated_clf.predict_proba(X_test_trans)[:, 1]
    test_preds = (test_probs >= 0.35).astype(int)
    
    calib_auc = roc_auc_score(y_test, test_probs)
    calib_brier = brier_score_loss(y_test, test_probs)
    calib_ks = calculate_ks_statistic(y_test, test_probs)
    conf_matrix = confusion_matrix(y_test, test_preds).tolist()
    
    print(f"Calibrated Test Metrics: ROC-AUC={calib_auc:.4f}, KS={calib_ks:.4f}, Brier={calib_brier:.4f}")
    
    # Compute Background dataset for SHAP (100 representative samples)
    background_samples = X_train_trans[:100]
    
    # Calculate feature importances
    if hasattr(best_clf, 'feature_importances_'):
        feat_importances = {name: float(imp) for name, imp in zip(all_feature_names, best_clf.feature_importances_)}
    else:
        # Fallback to absolute coefficients
        feat_importances = {name: float(np.abs(coef)) for name, coef in zip(all_feature_names, best_clf.coef_[0])}
        
    sorted_importances = dict(sorted(feat_importances.items(), key=lambda item: item[1], reverse=True)[:15])
    
    # Prepare package artifacts
    model_artifact = {
        'preprocessor': preprocessor,
        'base_model': best_clf,
        'calibrated_model': calibrated_clf,
        'num_features': num_features,
        'cat_features': cat_features,
        'all_feature_names': all_feature_names,
        'background_samples': background_samples
    }
    
    model_save_path = os.path.join(artifacts_dir, 'credit_risk_pipeline.joblib')
    joblib.dump(model_artifact, model_save_path)
    print(f"Model artifacts successfully serialized to: {model_save_path}")
    
    # Generate metadata file
    metadata = {
        'model_name': 'CredX Gradient Risk Estimator',
        'version': '1.0.0',
        'trained_at': datetime.utcnow().isoformat(),
        'best_architecture': best_model_name,
        'benchmark_comparison': results,
        'test_metrics': {
            'roc_auc': float(calib_auc),
            'ks_statistic': float(calib_ks),
            'brier_score': float(calib_brier),
            'confusion_matrix': conf_matrix,
            'test_sample_size': len(y_test)
        },
        'num_features': num_features,
        'cat_features': cat_features,
        'total_transformed_features': len(all_feature_names),
        'top_global_features': sorted_importances,
        'risk_thresholds': {
            'low_risk_max_pd': 0.12,
            'medium_risk_max_pd': 0.28,
            'high_risk_max_pd': 0.55
        }
    }
    
    metadata_path = os.path.join(artifacts_dir, 'model_metadata.json')
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    print(f"Model metadata saved to: {metadata_path}")
    
    # Save feature names list
    with open(os.path.join(artifacts_dir, 'feature_names.json'), 'w') as f:
        json.dump(all_feature_names, f, indent=2)

if __name__ == '__main__':
    train_and_evaluate()
