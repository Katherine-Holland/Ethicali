import pandas as pd

class FairnessNode:
    def __init__(self, thresholds):
        self.thresholds = thresholds

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

# ✅ Wrapper for validator system
def validate_fairness(dataset_path, algorithm_path=None):
    dataset = pd.read_csv(dataset_path)

    thresholds = {
        "gender": 0.15,
        "ethnicity": 0.10,
        "age_group": 0.10,
    }

    node = FairnessNode(thresholds)
    return node.evaluate_dataset(dataset)
