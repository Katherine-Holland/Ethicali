import json
import csv
from collections import Counter

class BiasDetectionNode:
    def __init__(self, thresholds, optional_features=None):
        self.thresholds = thresholds
        self.optional_features = optional_features or []

    def evaluate_dataset(self, dataset_rows):
        results = {}
        overall_compliance = True

        for feature, threshold in self.thresholds.items():
            if feature in dataset_rows[0]:  # check if column exists
                idx = dataset_rows[0].index(feature)
                feature_data = [row[idx] for row in dataset_rows[1:] if row[idx] != ""]
                if not feature_data:
                    results[feature] = {
                        "compliant": False,
                        "representation": {},
                        "below_threshold": {},
                        "threshold": threshold,
                        "reason": "Skipped due to missing values",
                    }
                    overall_compliance = False
                    continue

                total = len(feature_data)
                counts = Counter(feature_data)
                proportions = {k: v/total for k,v in counts.items()}
                below_threshold = {k: p for k,p in proportions.items() if p < threshold}
                compliant = not below_threshold
                results[feature] = {
                    "compliant": compliant,
                    "representation": proportions,
                    "below_threshold": below_threshold,
                    "threshold": threshold,
                    "reason": "Below threshold" if not compliant else "Meets threshold",
                }
                overall_compliance = overall_compliance and compliant
            elif feature in self.optional_features:
                results[feature] = {
                    "compliant": True,
                    "representation": {},
                    "below_threshold": {},
                    "threshold": threshold,
                    "reason": "Optional feature not found in dataset",
                }
            else:
                results[feature] = {
                    "compliant": False,
                    "representation": {},
                    "below_threshold": {},
                    "threshold": threshold,
                    "reason": "Feature not found in dataset",
                }
                overall_compliance = False

        return {
            "compliant": overall_compliance,
            "features": results,
        }

# ✅ Wrapper
def validate_bias(dataset_path=None, algorithm_path=None):
    thresholds = {"gender": 0.2, "ethnicity": 0.1, "age_group": 0.15}
    detector = BiasDetectionNode(thresholds)

    dataset_results = {"status": "skipped", "message": "No dataset provided"}
    algorithm_results = {"status": "skipped", "message": "No algorithm provided"}

    if dataset_path:
        try:
            with open(dataset_path, newline="") as f:
                reader = csv.reader(f)
                rows = list(reader)
            dataset_results = detector.evaluate_dataset(rows)
        except Exception as e:
            dataset_results = {"status": "error", "message": str(e)}

    if algorithm_path:
        try:
            with open(algorithm_path, "r") as f:
                algo = {
                    "weights": {
                        "gender": {"male": 0.5, "female": 0.5},
                        "ethnicity": {"group1": 0.9, "group2": 0.05, "group3": 0.05}
                    },
                    "description": "Sample ML model"
                }
                algorithm_results = detector.evaluate_algorithm(algo)
        except Exception as e:
            algorithm_results = {"status": "error", "message": str(e)}

    return {"dataset": dataset_results, "algorithm": algorithm_results}
