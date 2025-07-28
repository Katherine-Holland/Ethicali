import os
import csv

class RiskNode:
    def __init__(self, high_risk_features=None, missing_data_threshold=0.2):
        self.high_risk_features = high_risk_features or ["health_condition", "credit_score", "biometric_data"]
        self.missing_data_threshold = missing_data_threshold

    def evaluate_dataset(self, dataset_rows, headers):
        results = {}
        overall_compliance = True

        # ✅ Check for presence of high-risk features
        for feature in self.high_risk_features:
            feature_found = feature in headers
            results[feature] = {
                "present": feature_found,
                "compliant": feature_found,
                "reason": "Found in dataset" if feature_found else "Missing expected high-risk field"
            }
            if not feature_found:
                overall_compliance = False

        # ✅ Check for excessive missing values (row-by-row)
        missing_report = {}
        total_rows = len(dataset_rows)
        if total_rows > 0:
            for i, col in enumerate(headers):
                missing_count = sum(1 for row in dataset_rows if row[i] == "" or row[i] is None)
                missing_ratio = missing_count / total_rows
                compliant = missing_ratio < self.missing_data_threshold
                missing_report[col] = {
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

    if dataset_path and os.path.exists(dataset_path):
        try:
            with open(dataset_path, "r", newline="", encoding="utf-8") as f:
                reader = csv.reader(f)
                headers = next(reader)
                rows = list(reader)

            return node.evaluate_dataset(rows, headers)

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

