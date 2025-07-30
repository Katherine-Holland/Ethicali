import csv
import os
from collections import Counter

class FairnessNode:
    def __init__(self, thresholds):
        self.thresholds = thresholds

    def evaluate_dataset(self, dataset_path):
        results = {}
        overall_compliance = True

        try:
            with open(dataset_path, "r") as f:
                reader = csv.DictReader(f)
                rows = list(reader)
        except Exception as e:
            return {
                "status": "error",
                "message": f"Dataset read error: {str(e)}"
            }

        if not rows:
            return {
                "status": "error",
                "message": "Dataset is empty"
            }

        for feature, threshold in self.thresholds.items():
            values = [row.get(feature) for row in rows if row.get(feature)]
            if not values:
                results[feature] = {
                    "compliant": False,
                    "representation": {},
                    "below_threshold": {},
                    "threshold": threshold,
                    "reason": "Feature missing or all values empty",
                }
                overall_compliance = False
                continue

            total = len(values)
            counts = Counter(values)
            normalized = {k: v / total for k, v in counts.items()}
            below_threshold = {k: v for k, v in normalized.items() if v < threshold}
            compliant = not below_threshold

            results[feature] = {
                "compliant": compliant,
                "representation": normalized,
                "below_threshold": below_threshold,
                "threshold": threshold,
                "reason": "Below threshold" if not compliant else "Meets threshold",
            }
            overall_compliance = overall_compliance and compliant

        return {
            "compliant": overall_compliance,
            "features": results,
        }

    def evaluate_algorithm(self, algorithm_obj):
        """Evaluate algorithm for fairness (weight distribution)."""
        results = {}
        overall_compliance = True

        weights_block = algorithm_obj.get("weights", {})
        if not weights_block:
            return {
                "compliant": False,
                "reason": "No weights found in algorithm for fairness evaluation"
            }

        for feature, threshold in self.thresholds.items():
            weights = weights_block.get(feature, {})
            if not weights:
                results[feature] = {
                    "compliant": False,
                    "weights": {},
                    "threshold": threshold,
                    "reason": "Feature not present in algorithm weights",
                }
                overall_compliance = False
                continue

            total = sum(weights.values()) or 1.0
            normalized = {k: v / total for k, v in weights.items()}
            below_threshold = {k: v for k, v in normalized.items() if v < threshold}
            compliant = not below_threshold

            results[feature] = {
                "compliant": compliant,
                "weights": normalized,
                "below_threshold": below_threshold,
                "threshold": threshold,
                "reason": "Below threshold" if not compliant else "Meets threshold",
            }
            overall_compliance = overall_compliance and compliant

        return {
            "compliant": overall_compliance,
            "features": results,
        }

# ✅ Wrapper for validator orchestration
def validate_fairness(dataset_path=None, algorithm_path=None):
    thresholds = {
        "gender": 0.15,
        "ethnicity": 0.10,
        "age_group": 0.10,
    }

    node = FairnessNode(thresholds)

    dataset_results = {"status": "skipped", "message": "No dataset provided"}
    algorithm_results = {"status": "skipped", "message": "No algorithm provided"}

    if dataset_path:
        dataset_results = node.evaluate_dataset(dataset_path)

    if algorithm_path:
        try:
            algo_namespace = {}
            with open(algorithm_path, "r") as f:
                exec(f.read(), algo_namespace)
            algorithm_obj = algo_namespace.get("algorithm", {})
            algorithm_results = node.evaluate_algorithm(algorithm_obj)
        except Exception as e:
            algorithm_results = {"status": "error", "message": str(e)}

    return {"dataset": dataset_results, "algorithm": algorithm_results}
