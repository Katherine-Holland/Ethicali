import os
import csv

class RiskNode:
    def __init__(self, high_risk_features=None, missing_data_threshold=0.2):
        self.high_risk_features = high_risk_features or ["health_condition", "credit_score", "biometric_data"]
        self.missing_data_threshold = missing_data_threshold

    def evaluate_dataset(self, dataset_rows, headers):
        results = {}
        overall_compliance = True
        # ✅ High-risk feature presence
        for feature in self.high_risk_features:
            feature_found = feature in headers
            results[feature] = {
                "present": feature_found,
                "compliant": feature_found,
                "reason": "Found in dataset" if feature_found else "Missing expected high-risk field"
            }
            if not feature_found:
                overall_compliance = False

        # ✅ Missing data analysis
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

    def evaluate_algorithm(self, algorithm_obj):
        """Validate if algorithm handles high-risk features and mitigation."""
        results = {}
        overall_compliance = True

        for feature in self.high_risk_features:
            handles_feature = feature in algorithm_obj.get("handles", [])
            mitigation = algorithm_obj.get("mitigation", {}).get(feature, None)
            compliant = handles_feature and mitigation is not None
            results[feature] = {
                "handled": handles_feature,
                "mitigation": mitigation,
                "compliant": compliant,
                "reason": (
                    "Algorithm handles and mitigates this risk"
                    if compliant else
                    "Missing handling or mitigation for this risk"
                )
            }
            if not compliant:
                overall_compliance = False

        human_review = algorithm_obj.get("human_review_enabled", False)
        if not human_review:
            overall_compliance = False

        return {
            "compliant": overall_compliance,
            "high_risk_handling": results,
            "human_review_enabled": human_review
        }

# ✅ Wrapper at module level
def validate_risk(dataset_path=None, algorithm_path=None):
    node = RiskNode()

    dataset_results = {"status": "skipped", "message": "No dataset provided"}
    algorithm_results = {"status": "skipped", "message": "No algorithm provided"}

    if dataset_path and os.path.exists(dataset_path):
        try:
            with open(dataset_path, "r", newline="", encoding="utf-8") as f:
                reader = csv.reader(f)
                headers = next(reader)
                rows = list(reader)
            dataset_results = node.evaluate_dataset(rows, headers)
        except Exception as e:
            dataset_results = {"status": "error", "message": f"Dataset error: {str(e)}"}

    if algorithm_path and os.path.exists(algorithm_path):
        try:
            algo_namespace = {}
            with open(algorithm_path, "r") as f:
                exec(f.read(), algo_namespace)
            algorithm_obj = algo_namespace.get("algorithm", {})
            algorithm_results = node.evaluate_algorithm(algorithm_obj)
        except Exception as e:
            algorithm_results = {"status": "error", "message": f"Algorithm error: {str(e)}"}

    return {"dataset": dataset_results, "algorithm": algorithm_results}
