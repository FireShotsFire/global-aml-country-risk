import pandas as pd

"""
Global AML/CFT Country Risk Index
Scoring engine v1.0
This is an independent analytical model.
It is NOT an official FATF, EU, AMLA or government rating.
"""

WEIGHTS = {
    "fatf_score": 0.35,
    "eu_score": 0.30,
    "effectiveness_score": 0.20,
    "structural_score": 0.10,
    "sanctions_score": 0.05,
}

def calculate_score(row):
    """
    Calculates overall score dynamically scaling weights if data is missing.
    """
    total_weight = 0.0
    weighted_score = 0.0

    for key, weight in WEIGHTS.items():
        val = row.get(key)
        if pd.notna(val):
            weighted_score += val * weight
            total_weight += weight

    if total_weight == 0:
        return None

    # Scale back to 100% basis
    final_score = weighted_score / total_weight
    return round(min(max(final_score, 0), 100), 1)

def risk_band(score):
    """
    Convert numerical score into risk category.
    """
    if pd.isna(score) or score is None:
        return "Insufficient Data"
    if score >= 80:
        return "Critical"
    elif score >= 60:
        return "High"
    elif score >= 40:
        return "Elevated"
    elif score >= 20:
        return "Moderate"
    return "Low"

def confidence_score(row):
    """
    Estimate data coverage proportion.
    """
    available = sum(1 for field in WEIGHTS.keys() if pd.notna(row.get(field)))
    return round((available / len(WEIGHTS)) * 100)

def component_contributions(row):
    """
    Calculate weighted contribution of each component to overall score.
    """
    contributions = {}
    label_map = {
        "fatf_score": "FATF",
        "eu_score": "EU AMLR",
        "effectiveness_score": "Effectiveness",
        "structural_score": "Structural Risk",
        "sanctions_score": "Sanctions / PF",
    }
    for key, weight in WEIGHTS.items():
        val = row.get(key)
        label = label_map.get(key, key)
        contributions[label] = round(val * weight, 1) if pd.notna(val) else 0.0
    return contributions
