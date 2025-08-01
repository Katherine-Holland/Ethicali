import os
import csv

class ExplainabilityNode:
    def __init__(self, max_features=30):
        self.max_features = max_features
        self.explainable_model_keywords = [
            "decision_tree", "logistic_regression", "linear_model", "explainable_boosting", "rulefit"
        ]

    def evaluate_algorithm(self, algorithm_path):
        result = {
            "model_type_detected": None,
            "compliant_model_type": False,
            "feature_count": None,
            "feature_compliance": False,
            "reason": ""
        }

        if not os.path.exists(algorithm_path):
            return {
                "compliant": False,
                "details": result,
                "reason": "Algorithm file not found"
            }

        try:
            with open(algorithm_path, "r") as f:
                code = f.read().lower()

            for keyword in self.explainable_model_keywords:
                if keyword in code:
                    result["model_type_detected"] = keyword
                    result["compliant_model_type"] = True
                    break

            if not result["compliant_model_type"]:
                result["reason"] = "Model type not clearly explainable"

        except Exception as e:
            return {
                "compliant": False,
                "details": result,
                "reason": f"Error reading algorithm: {str(e)}"
            }

        return {
            "compliant": result["compliant_model_type"],
            "details": result
        }

    def evaluate_dataset(self, dataset_path):
        try:
            with open(dataset_path, "r") as f:
                reader = csv.reader(f)
                headers = next(reader, [])
            feature_count = len(headers)
        except Exception as e:
            return {
                "compliant": False,
                "feature_count": 0,
                "max_allowed": self.max_features,
                "reason": f"Error reading dataset: {str(e)}"
            }

        compliant = feature_count <= self.max_features
        return {
            "compliant": compliant,
            "feature_count": feature_count,
            "max_allowed": self.max_features,
            "reason": "Too many features for human interpretability" if not compliant else "Acceptable number of features"
        }

# ✅ Wrapper
def validate_explainability(dataset_path=None, algorithm_path=None):
    node = ExplainabilityNode()

    dataset_results = {"status": "skipped", "message": "No dataset provided"}
    algorithm_results = {"status": "skipped", "message": "No algorithm provided"}

    if dataset_path:
        dataset_results = node.evaluate_dataset(dataset_path)

    if algorithm_path:
        algorithm_results = node.evaluate_algorithm(algorithm_path)

    return {
        "dataset": dataset_results,
        "algorithm": algorithm_results
    }
