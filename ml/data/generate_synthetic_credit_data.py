"""
Synthetic Credit Risk Dataset Generator
Generates realistic, empirical credit risk records calibrated to actual banking and lending distributions.
"""

import numpy as np
import pandas as pd
import os

def generate_credit_dataset(n_samples: int = 5000, random_state: int = 42) -> pd.DataFrame:
    np.random.seed(random_state)
    
    # 1. Age distribution (log-normal/gamma distribution typical in lending)
    age = np.clip(np.random.gamma(shape=9, scale=4, size=n_samples).astype(int), 18, 75)
    
    # 2. Employment length (correlated with age)
    max_emp = np.maximum(0, age - 18)
    emp_length = np.clip(np.random.exponential(scale=5, size=n_samples), 0, max_emp)
    emp_length = np.round(emp_length, 1)
    
    # 3. Annual Income (log-normal distribution with realistic skew)
    income = np.exp(np.random.normal(loc=10.9, scale=0.6, size=n_samples))
    income = np.clip(np.round(income, -2), 12000, 350000)
    
    # 4. Home Ownership
    home_choices = ['RENT', 'MORTGAGE', 'OWN', 'OTHER']
    home_ownership = []
    for a in age:
        if a < 26:
            p = [0.75, 0.15, 0.08, 0.02]
        elif a < 45:
            p = [0.42, 0.45, 0.11, 0.02]
        else:
            p = [0.25, 0.50, 0.23, 0.02]
        home_ownership.append(np.random.choice(home_choices, p=p))
    home_ownership = np.array(home_ownership)
    
    # 5. Loan Intent
    intents = ['PERSONAL', 'EDUCATION', 'MEDICAL', 'VENTURE', 'HOMEIMPROVEMENT', 'DEBTCONSOLIDATION']
    intent_probs = [0.18, 0.15, 0.12, 0.15, 0.16, 0.24]
    loan_intent = np.random.choice(intents, size=n_samples, p=intent_probs)
    
    # 6. Credit Bureau Score (FICO proxy: normal dist centered around 680, clip 350 - 850)
    credit_score = np.random.normal(loc=680, scale=65, size=n_samples).astype(int)
    credit_score = np.clip(credit_score, 350, 850)
    
    # 7. Credit Bureau History Length (years, correlated with age)
    cred_hist_length = np.clip((age - 18) * np.random.uniform(0.3, 0.9, size=n_samples), 1, 40).astype(int)
    
    # 8. Requested Loan Amount
    loan_amnt = np.random.gamma(shape=3.5, scale=3500, size=n_samples)
    loan_amnt = np.clip(np.round(loan_amnt, -2), 1000, 40000)
    
    # 9. Loan percentage of income
    loan_percent_income = np.round(loan_amnt / income, 3)
    
    # 10. Revolving credit utilization (beta distribution)
    revolving_utilization = []
    for cs in credit_score:
        if cs < 620:
            u = np.random.beta(3.5, 1.5) * 100.0
        elif cs < 720:
            u = np.random.beta(2.0, 2.5) * 100.0
        else:
            u = np.random.beta(1.2, 4.0) * 100.0
        revolving_utilization.append(u)
    revolving_utilization = np.round(np.clip(np.array(revolving_utilization), 1.0, 99.5), 1)
    
    # 11. Debt-to-income ratio (DTI)
    dti_base = np.random.beta(2.5, 4.0, size=n_samples) * 0.65
    debt_to_income_ratio = dti_base + (revolving_utilization / 400.0)
    debt_to_income_ratio = np.round(np.clip(debt_to_income_ratio, 0.05, 0.70), 3)
    
    # 12. Delinquencies in past 2 years
    delinq_2yrs = []
    for cs in credit_score:
        if cs < 580:
            p = [0.35, 0.30, 0.20, 0.15]
        elif cs < 670:
            p = [0.70, 0.18, 0.08, 0.04]
        elif cs < 750:
            p = [0.91, 0.06, 0.02, 0.01]
        else:
            p = [0.98, 0.015, 0.005, 0.0]
        delinq_2yrs.append(np.random.choice([0, 1, 2, 3], p=p))
    delinq_2yrs = np.array(delinq_2yrs)
    
    # 13. Historical default on file
    cb_person_default_on_file = []
    for cs in credit_score:
        if cs < 580:
            p_def = 0.45
        elif cs < 650:
            p_def = 0.20
        elif cs < 720:
            p_def = 0.06
        else:
            p_def = 0.01
        cb_person_default_on_file.append('Y' if np.random.rand() < p_def else 'N')
    cb_person_default_on_file = np.array(cb_person_default_on_file)
    
    # 14. Interest Rate & Internal Loan Grade
    base_rate = 18.0 - (credit_score - 500) * 0.035 + (debt_to_income_ratio * 12.0)
    loan_int_rate = np.clip(np.round(base_rate + np.random.normal(0, 1.2, size=n_samples), 2), 4.5, 29.9)
    
    loan_grade = []
    for r in loan_int_rate:
        if r < 7.5:
            loan_grade.append('A')
        elif r < 11.0:
            loan_grade.append('B')
        elif r < 14.5:
            loan_grade.append('C')
        elif r < 18.5:
            loan_grade.append('D')
        elif r < 23.0:
            loan_grade.append('E')
        elif r < 27.0:
            loan_grade.append('F')
        else:
            loan_grade.append('G')
    loan_grade = np.array(loan_grade)
    
    # 15. Target Generation: Loan Status (0 = Paid/Current, 1 = Defaulted/Charge-off)
    z = (
        -2.4                                                    # Calibrated intercept
        + (credit_score < 600) * 1.8                            # Poor credit score
        + (credit_score >= 600) * (credit_score < 670) * 0.9
        - (credit_score >= 740) * 1.4                           # Prime credit
        + (debt_to_income_ratio > 0.40) * 1.3                   # Strained debt
        + (revolving_utilization > 60.0) * 1.1                  # Overextended cards
        + (loan_percent_income > 0.30) * 1.4                    # Outsized loan
        + (delinq_2yrs > 0) * 1.2                               # Delinquency history
        + (cb_person_default_on_file == 'Y') * 1.7              # Prior default
        - np.log1p(income) * 0.22                               # Income buffer
        + (home_ownership == 'RENT') * 0.40
        - (home_ownership == 'OWN') * 0.50
        + (loan_intent == 'DEBTCONSOLIDATION') * 0.35
        + (loan_intent == 'MEDICAL') * 0.25
        + np.random.normal(0, 0.4, size=n_samples)              # Unobserved variation
    )
    
    prob_default = 1.0 / (1.0 + np.exp(-z))
    loan_status = (np.random.rand(n_samples) < prob_default).astype(int)
    
    df = pd.DataFrame({
        'person_age': age,
        'person_income': income,
        'person_emp_length': emp_length,
        'person_home_ownership': home_ownership,
        'loan_intent': loan_intent,
        'loan_grade': loan_grade,
        'loan_amnt': loan_amnt,
        'loan_int_rate': loan_int_rate,
        'loan_percent_income': loan_percent_income,
        'credit_score': credit_score,
        'debt_to_income_ratio': debt_to_income_ratio,
        'revolving_utilization': revolving_utilization,
        'delinq_2yrs': delinq_2yrs,
        'cb_person_default_on_file': cb_person_default_on_file,
        'cb_person_cred_hist_length': cred_hist_length,
        'loan_status': loan_status
    })
    
    return df

if __name__ == '__main__':
    output_dir = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(output_dir, exist_ok=True)
    csv_path = os.path.join(output_dir, 'credit_risk_dataset.csv')
    
    print("Generating realistic credit risk dataset with 5,000 samples...")
    df = generate_credit_dataset(5000)
    df.to_csv(csv_path, index=False)
    
    default_rate = df['loan_status'].mean() * 100
    print(f"Dataset successfully created at: {csv_path}")
    print(f"Total rows: {len(df)}, Default rate: {default_rate:.2f}%")
    print(df.head(3))
