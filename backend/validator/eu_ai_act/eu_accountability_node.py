import pandas as pd

class AccountabilityNode:
    def __init__(self, required_metadata=None):
        self.required_metadata = required_metadata or ["timestamp", "version", "decision_log"]

    def evaluate_dataset(self, dataset):
        missing_metadata = [meta for meta in self.required_metadata if meta not in dataset.columns]
        return {
            "compliant": not missing_metadata,
            "missing_metadata": missing_metadata,
            "reason": f"Missing mandatory metadata: {missing_metadata}" if missing_metadata else "All metadata present",
        }

    def evaluate_algorithm(self, algorithm):
        missing_keys = [key for key in self.required_metadata if key not in algorithm]
        return {
            "compliant": not missing_keys,
            "missing_keys": missing_keys,
            "reason": f"Missing mandatory keys: {missing_keys}" if missing_keys else "All keys present",
        }

# ✅ Wrapper for validator system
def validate_accountability(dataset_path, algorithm_path=None):
    dataset = pd.read_csv(dataset_path)

    required_metadata = ["timestamp", "version", "decision_log"]
    node = AccountabilityNode(required_metadata)

    return node.evaluate_dataset(dataset)
