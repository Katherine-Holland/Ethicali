import os
import csv

class TransparencyNode:
    def __init__(self, required_columns=None):
        self.required_columns = required_columns or []

    def evaluate_dataset(self, headers):
        missing_columns = [col for col in self.required_columns if col not in headers]
        return {
            "compliant": not missing_columns,
            "missing_columns": missing_columns,
            "reason": f"Missing columns: {missing_columns}" if missing_columns else "All required columns present"
        }

# ✅ Wrapper function for validator node
def validate_transparency(dataset_path=None, algorithm_path=None):
    required_columns = ["id", "gender", "ethnicity", "age_group"]
    node = TransparencyNode(required_columns)
    results = {}

    if dataset_path and os.path.exists(dataset_path):
        try:
            with open(dataset_path, "r", newline="", encoding="utf-8") as f:
                reader = csv.reader(f)
                headers = next(reader)

            results = node.evaluate_dataset(headers)

        except Exception as e:
            results = {
                "status": "error",
                "message": f"Dataset error: {str(e)}"
            }
    else:
        results = {
            "status": "skipped",
            "message": "No dataset provided"
        }

    # Algorithm transparency not required yet — skipping
    return results
