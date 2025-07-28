import os
import csv
import random

class RobustnessNode:
    def __init__(self, noise_level=0.05, variation_threshold=0.10):
        self.noise_level = noise_level
        self.variation_threshold = variation_threshold

    def evaluate_dataset(self, dataset_rows, headers):
        results = {}
        overall_compliance = True

        # ✅ Identify numeric columns by attempting float conversion
        numeric_indices = []
        for i, col in enumerate(headers):
            try:
                # Check if most values are numeric
                sample_values = [row[i] for row in dataset_rows if row[i] != ""]
                if sample_values and all(self._is_number(v) for v in sample_values[:10]):
                    numeric_indices.append(i)
            except Exception:
                continue

        if not numeric_indices:
            return {
                "compliant": False,
                "reason": "No numeric features found for robustness test",
                "details": {}
            }

        for idx in numeric_indices:
            col_name = headers[idx]
            try:
                original = [float(row[idx]) for row in dataset_rows if row[idx] != ""]
            except ValueError:
                continue

            if not original:
                results[col_name] = {
                    "compliant": False,
                    "reason": "Column empty or all nulls"
                }
                overall_compliance = False
                continue

            # ✅ Add noise manually
            perturbed = [x + random.gauss(0, self.noise_level) for x in original]

            original_mean = sum(original) / len(original)
            perturbed_mean = sum(perturbed) / len(perturbed)
            mean_diff = abs(original_mean - perturbed_mean) / (original_mean + 1e-9)

            compliant = mean_diff < self.variation_threshold
            results[col_name] = {
                "compliant": compliant,
                "mean_difference_ratio": round(mean_diff, 4),
                "threshold": self.variation_threshold,
                "reason": "Stable under noise" if compliant else "Sensitive to small noise"
            }

            if not compliant:
                overall_compliance = False

        return {
            "compliant": overall_compliance,
            "details": results
        }

    def _is_number(self, value):
        try:
            float(value)
            return True
        except ValueError:
            return False

# ✅ Wrapper for validator orchestration
def validate_robustness(dataset_path=None, algorithm_path=None):
    node = RobustnessNode()
    results = {}

    if dataset_path and os.path.exists(dataset_path):
        try:
            with open(dataset_path, "r", newline="", encoding="utf-8") as f:
                reader = csv.reader(f)
                headers = next(reader)
                rows = list(reader)

            dataset_result = node.evaluate_dataset(rows, headers)
            results["dataset_analysis"] = dataset_result
            results["compliant"] = dataset_result["compliant"]

        except Exception as e:
            results["dataset_analysis"] = {
                "compliant": False,
                "reason": f"Dataset error: {str(e)}"
            }
            results["compliant"] = False
    else:
        results["dataset_analysis"] = {
            "compliant": False,
            "reason": "No dataset provided"
        }
        results["compliant"] = False

    return results
