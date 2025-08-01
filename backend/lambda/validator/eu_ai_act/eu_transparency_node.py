import csv
import os
import json

class TransparencyNode:
    def __init__(self):
        self.required_columns = ["id", "timestamp", "version", "decision_log"]

    def evaluate_dataset(self, dataset_path):
        missing_columns = []
        try:
            with open(dataset_path, "r") as f:
                reader = csv.DictReader(f)
                columns = reader.fieldnames or []
        except Exception as e:
            return {
                "status": "error",
                "message": f"Dataset read error: {str(e)}"
            }

        for col in self.required_columns:
            if col not in columns:
                missing_columns.append(col)

        compliant = len(missing_columns) == 0
        return {
            "compliant": compliant,
            "missing_columns": missing_columns,
            "reason": "All required columns present" if compliant else "Missing required columns"
        }

    def evaluate_algorithm(self, algorithm_path):
        missing_keys = []
        try:
            algo_namespace = {}
            with open(algorithm_path, "r") as f:
                exec(f.read(), algo_namespace)
            algorithm = algo_namespace.get("algorithm", {})
        except Exception as e:
            return {
                "status": "error",
                "message": f"Algorithm read error: {str(e)}"
            }

        required_keys = ["description", "version", "author", "decision_log"]
        for key in required_keys:
            if key not in algorithm:
                missing_keys.append(key)

        compliant = len(missing_keys) == 0
        return {
            "compliant": compliant,
            "missing_keys": missing_keys,
            "reason": "All transparency keys present" if compliant else "Missing transparency keys"
        }

# ✅ Wrapper for validator orchestration
def validate_transparency(dataset_path=None, algorithm_path=None):
    node = TransparencyNode()

    dataset_results = {"status": "skipped", "message": "No dataset provided"}
    algorithm_results = {"status": "skipped", "message": "No algorithm provided"}

    if dataset_path:
        dataset_results = node.evaluate_dataset(dataset_path)

    if algorithm_path:
        algorithm_results = node.evaluate_algorithm(algorithm_path)

    return {"dataset": dataset_results, "algorithm": algorithm_results}
