# backend/validator/eu_robustness_node.py

import os
import pandas as pd
import numpy as np

class RobustnessNode:
    def __init__(self, noise_level=0.05, variation_threshold=0.10):
        self.noise_level = noise_level
        self.variation_threshold = variation_threshold

    def evaluate_dataset(self, dataset):
        results = {}
        numeric_columns = dataset.select_dtypes(include=[np.number]).columns
        overall_compliance = True

        if numeric_columns.empty:
            return {
                "compliant": False,
                "reason": "No numeric features found for robustness test",
                "details": {}
            }

        for col in numeric_columns:
            original = dataset[col].dropna()
            if original.empty:
                results[col] = {
                    "compliant": False,
                    "reason": "Column empty or all nulls"
                }
                overall_compliance = False
                continue

            noise = np.random.normal(0, self.noise_level, size=original.shape)
            perturbed = original + noise

            mean_diff = abs(original.mean() - perturbed.mean()) / (original.mean() + 1e-9)  # avoid divide-by-zero
            compliant = mean_diff < self.variation_threshold

            results[col] = {
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

# ✅ Wrapper for validator orchestration
def validate_robustness(dataset_path=None, algorithm_path=None):
    node = RobustnessNode()
    results = {}

    if dataset_path:
        try:
            dataset = pd.read_csv(dataset_path)
            dataset_result = node.evaluate_dataset(dataset)
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
