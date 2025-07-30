import os

class OversightNode:
    def __init__(self, required_fields=None):
        self.required_fields = required_fields or [
            "human_review_enabled",
            "intervention_points",
            "override_capability"
        ]

    def evaluate_algorithm(self, algorithm_obj):
        results = {}
        overall_compliance = True

        for field in self.required_fields:
            if field not in algorithm_obj:
                results[field] = {
                    "compliant": False,
                    "reason": "Field missing"
                }
                overall_compliance = False
            else:
                value = algorithm_obj[field]
                if isinstance(value, bool):
                    compliant = value
                elif isinstance(value, list):
                    compliant = len(value) > 0
                else:
                    compliant = bool(value)

                results[field] = {
                    "compliant": compliant,
                    "value": value,
                    "reason": "OK" if compliant else "Field set to false or empty"
                }
                if not compliant:
                    overall_compliance = False

        return {
            "compliant": overall_compliance,
            "fields": results
        }

# ✅ Wrapper for validator orchestration
def validate_oversight(dataset_path=None, algorithm_path=None):
    node = OversightNode()
    dataset_results = {"status": "skipped", "message": "No dataset provided"}
    algorithm_results = {"status": "skipped", "message": "No algorithm provided"}

    # Oversight is algorithm-focused
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
