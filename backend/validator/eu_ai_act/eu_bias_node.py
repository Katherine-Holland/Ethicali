import pandas as pd
import json

class BiasDetectionNode:
    def __init__(self, thresholds, optional_features=None):
        self.thresholds = thresholds
        self.optional_features = optional_features or []

    def evaluate_dataset(self, dataset):
        results = {}
        overall_compliance = True

        for feature, threshold in self.thresholds.items():
            if feature in dataset:
                feature_data = dataset[feature].dropna()
                if feature_data.empty:
                    results[feature] = {
                        "compliant": False,
                        "representation": {},
                        "below_threshold": {},
                        "threshold": threshold,
                        "reason": "Skipped due to missing values",
                    }
                    overall_compliance = False
                    continue

                counts = feature_data.value_counts(normalize=True)
                below_threshold = counts[counts < threshold]
                compliant = below_threshold.empty
                results[feature] = {
                    "compliant": compliant,
                    "representation": counts.to_dict(),
                    "below_threshold": below_threshold.to_dict(),
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

    def evaluate_algorithm(self, algorithm):
        results = {}
        overall_compliance = True

        for feature, weights in algorithm.get("weights", {}).items():
            if feature in self.thresholds:
                threshold = self.thresholds[feature]
                below_threshold = {group: weight for group, weight in weights.items() if weight < threshold}
                compliant = not below_threshold
                results[feature] = {
                    "compliant": compliant,
                    "weights": weights,
                    "below_threshold": below_threshold,
                    "threshold": threshold,
                    "reason": "Below threshold" if not compliant else "Meets threshold",
                }
                overall_compliance = overall_compliance and compliant
            elif feature in self.optional_features:
                results[feature] = {
                    "compliant": True,
                    "weights": {},
                    "below_threshold": {},
                    "threshold": None,
                    "reason": "Optional feature not found in algorithm weights",
                }
            else:
                results[feature] = {
                    "compliant": False,
                    "weights": {},
                    "below_threshold": {},
                    "threshold": None,
                    "reason": "Feature not found in algorithm weights",
                }
                overall_compliance = False

        # Extra check: weights must sum to 1
        for feature, weights in algorithm.get("weights", {}).items():
            if abs(sum(weights.values()) - 1.0) > 0.01:
                results[feature]["warning"] = "Weights do not sum to 1, which may indicate bias."

        return {
            "compliant": overall_compliance,
            "features": results,
        }

# ✅ Wrapper for the validator node (called by `validate_eu.py`)
def validate_bias(dataset_path=None, algorithm_path=None):
    thresholds = {
        "gender": 0.2,
        "ethnicity": 0.1,
        "age_group": 0.15,
    }

    detector = BiasDetectionNode(thresholds)

    dataset_results = {"status": "skipped", "message": "No dataset provided"}
    algorithm_results = {"status": "skipped", "message": "No algorithm provided"}

    # Dataset bias check
    if dataset_path:
        try:
            dataset = pd.read_csv(dataset_path)
            dataset_results = detector.evaluate_dataset(dataset)
        except Exception as e:
            dataset_results = {"status": "error", "message": str(e)}

    # Algorithm bias check
    if algorithm_path:
        try:
            with open(algorithm_path, "r") as f:
                algo_code = f.read()
                # Mock: You can improve this later with real parsing
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

    return {
        "dataset": dataset_results,
        "algorithm": algorithm_results,
    }
