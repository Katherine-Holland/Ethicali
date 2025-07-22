import pandas as pd

class BiasDetectionNode:
    def __init__(self, thresholds, optional_features=None):
        self.thresholds = thresholds
        self.optional_features = optional_features or []  # List of optional features

    def evaluate_dataset(self, dataset):
        results = {}
        overall_compliance = True

        for feature, threshold in self.thresholds.items():
            if feature in dataset:
                feature_data = dataset[feature].dropna()  # Handle missing values
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

        for feature, weights in algorithm.get("weights", {}).items():
            if sum(weights.values()) != 1:
                results[feature]["warning"] = "Weights do not sum to 1, which may indicate bias."

        return {
            "compliant": overall_compliance,
            "features": results,
        }

# ✅ Wrapper function used by the validator node
def validate_bias(dataset_path, algorithm_path=None):
    thresholds = {
        "gender": 0.2,
        "ethnicity": 0.1,
        "age_group": 0.15,
    }

    detector = BiasDetectionNode(thresholds)
    dataset = pd.read_csv(dataset_path)
    results = detector.evaluate_dataset(dataset)

    if algorithm_path:
        with open(algorithm_path, "r") as f:
            algo_code = f.read()

        # Temporary mock: parse real weights from algo_code later
        mock_algo = {
            "weights": {
                "gender": {"male": 0.5, "female": 0.5},
                "ethnicity": {"group1": 0.9, "group2": 0.05, "group3": 0.05}
            }
        }

        algo_results = detector.evaluate_algorithm(mock_algo)
        results["algorithm_bias"] = algo_results

    return results
