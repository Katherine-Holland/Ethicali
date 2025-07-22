class TransparencyNode:
    def __init__(self, required_columns=None):
        self.required_columns = required_columns or []

    def evaluate_dataset(self, dataset):
        missing_columns = [col for col in self.required_columns if col not in dataset.columns]
        return {
            "compliant": not missing_columns,
            "missing_columns": missing_columns,
            "reason": f"Missing columns: {missing_columns}" if missing_columns else "All required columns present",
        }

    def evaluate_algorithm(self, algorithm):
        required_keys = ["weights", "description"]
        missing_keys = [key for key in required_keys if key not in algorithm]
        return {
            "compliant": not missing_keys,
            "missing_keys": missing_keys,
            "reason": f"Missing keys: {missing_keys}" if missing_keys else "All required keys present",
        }