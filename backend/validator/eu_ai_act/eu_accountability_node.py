import json
import csv

class AccountabilityNode:
    def __init__(self, required_metadata=None):
        self.required_metadata = required_metadata or ["timestamp", "version", "decision_log"]

    def evaluate_dataset(self, dataset_headers):
        missing = [meta for meta in self.required_metadata if meta not in dataset_headers]
        return {
            "compliant": not missing,
            "missing_metadata": missing,
            "reason": f"Missing mandatory metadata: {missing}" if missing else "All metadata present",
        }

    def evaluate_algorithm(self, algorithm):
        missing_keys = [key for key in self.required_metadata if key not in algorithm]
        return {
            "compliant": not missing_keys,
            "missing_keys": missing_keys,
            "reason": f"Missing mandatory keys: {missing_keys}" if missing_keys else "All keys present",
        }

# ✅ Wrapper function for validator node
def validate_accountability(dataset_path=None, algorithm_path=None):
    required_metadata = ["timestamp", "version", "decision_log"]
    node = AccountabilityNode(required_metadata)

    result = {}

    # === Dataset ===
    if dataset_path:
        try:
            with open(dataset_path, newline="") as f:
                reader = csv.reader(f)
                rows = list(reader)
                headers = rows[0] if rows else []
            result["dataset"] = node.evaluate_dataset(headers)
        except Exception as e:
            result["dataset"] = {
                "status": "error",
                "message": f"Dataset error: {str(e)}"
            }
    else:
        result["dataset"] = {
            "status": "skipped",
            "message": "No dataset provided"
        }

    # === Algorithm ===
    if algorithm_path:
        try:
            with open(algorithm_path, "r") as f:
                algo_code = f.read()
            # Placeholder mock – replace with real parser
            mock_algo = {
                "timestamp": "2025-07-21T12:34:56",
                "version": "1.0",
                "decision_log": ["decision1", "decision2"]
            }
            result["algorithm"] = node.evaluate_algorithm(mock_algo)
        except Exception as e:
            result["algorithm"] = {
                "status": "error",
                "message": f"Algorithm error: {str(e)}"
            }
    else:
        result["algorithm"] = {
            "status": "skipped",
            "message": "No algorithm provided"
        }

    return result

