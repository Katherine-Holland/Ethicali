# backend/validator/eu_risk_node.py

import pandas as pd
import os

class RiskNode:
    def __init__(self, high_risk_features=None, missing_data_threshold=0.2):
        self.high_risk_features = high_risk_features or ["health_condition", "credit_score", "biometric_data"]
        self.missing_data_threshold = missing_data_threshold

    def evaluate_dataset(self, dataset):
        results = {}
        overall_compliance = True

        # Check for presence of high-risk features
        for feature in self.high_risk_features:
            feature_found = feature in dataset.columns
            results[feature] = {
                "present": feature_found,
                "compliant": feature_found,  # In this context, presence is expected and OK
                "reason": "Found in dataset" if feature_found else "Missing expected high-risk field"
            }
            if not feature_found:
                overall_compliance = False

        # Check for excessive missing values
        missing_report = {}
        for column in dataset.columns:
            missing_ratio = dataset[column].isnull().mean()
            compliant = missing_ratio < self.missing_data_threshold
            missing_report[column] = {
                "missing_ratio": round(missing_ratio, 3),
                "compliant": compliant
            }
            if not compliant:
                overall_compliance = False

        return {
            "compliant": overall_compliance,
            "high_risk_fields": results,
            "missing_data_report": missing_report
        }

# ✅ Wrapper for validator orchestration
def validate_risk(dataset_path=None, algorithm_path=None):
    node = RiskNode()

    if dataset_path:
        try:
            dataset = pd.read_csv(dataset_path)
            return node.evaluate_dataset(dataset)
        except Exception as e:
            return {
                "status": "error",
                "message": f"Dataset error: {str(e)}"
            }
    else:
        return {
            "status": "skipped",
            "message": "No dataset provided"
        }
