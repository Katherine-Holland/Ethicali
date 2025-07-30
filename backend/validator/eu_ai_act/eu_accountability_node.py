import csv
import os

class AccountabilityNode:
    def __init__(self, required_metadata=None):
        self.required_metadata = required_metadata or ["timestamp", "version", "decision_log"]

    def evaluate_dataset(self, headers):
        missing = [meta for meta in self.required_metadata if meta not in headers]
        return {
            "compliant": not missing,
            "missing_metadata": missing,
            "reason": f"Missing mandatory metadata: {missing}" if missing else "All metadata present",
        }

    def evaluate_algorithm(self, algorithm_obj):
        missing_keys = [key for key in self.required_metadata if key not in algorithm_obj]
        return {
            "compliant": not missing_keys,
            "missing_keys": missing_keys,
            "reason": f"Missing mandatory keys: {missing_keys}" if missing_keys else "All keys present",
        }

# ✅ Wrapper for validator orchestration
def validate_accountability(dataset_path=None, algorithm_path=None):
    node = AccountabilityNode()

    dataset_results = {"status": "skipped", "message": "No dataset provided"}
    algorithm_results = {"status": "skipped", "message": "No algorithm provided"}

    # Dataset evaluation
    if dataset_path and os.path.exists(dataset_path):
        try:
            with open(dataset_path, newline="", encoding="utf-8") as f:
                reader = csv.reader(f)
                rows = list(reader)
                headers = rows[0] if rows else []
            dataset_results = node.evaluate_dataset(headers)
        except Exception as e:
            dataset_results = {"status": "error", "message": f"Dataset error: {str(e)}"}

    # Algorithm evaluation
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
