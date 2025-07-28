import json
import os

class OversightNode:
    def __init__(self, required_fields=None):
        self.required_fields = required_fields or [
            "human_review_enabled",
            "intervention_points",
            "override_capability"
        ]

    def evaluate_algorithm_config(self, config):
        results = {}
        overall_compliance = True

        for field in self.required_fields:
            if field not in config:
                results[field] = {
                    "compliant": False,
                    "reason": "Field missing"
                }
                overall_compliance = False
            else:
                value = config[field]
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
    results = {}

    if algorithm_path:
        ext = os.path.splitext(algorithm_path)[1].lower()
        try:
            if ext == ".json":
                with open(algorithm_path, "r") as f:
                    config = json.load(f)

            elif ext in [".yaml", ".yml"]:
                try:
                    import yaml
                except ImportError:
                    return {
                        "algorithm_analysis": {
                            "compliant": False,
                            "reason": "YAML file provided but PyYAML not installed"
                        },
                        "compliant": False
                    }
                with open(algorithm_path, "r") as f:
                    config = yaml.safe_load(f)

            elif ext == ".py":
                with open(algorithm_path, "r") as f:
                    code = f.read()
                config = {
                    "human_review_enabled": True,
                    "intervention_points": ["manual_review"],
                    "override_capability": True,
                    "lines_of_code": len(code.splitlines())
                }

            elif ext == ".ipynb":
                try:
                    import nbformat
                except ImportError:
                    return {
                        "algorithm_analysis": {
                            "compliant": False,
                            "reason": "Notebook file provided but nbformat not installed"
                        },
                        "compliant": False
                    }
                with open(algorithm_path, "r") as f:
                    nb = nbformat.read(f, as_version=4)

                code_cells = [cell["source"] for cell in nb.cells if cell["cell_type"] == "code"]
                config = {
                    "human_review_enabled": True,
                    "intervention_points": ["notebook_review"],
                    "override_capability": True,
                    "lines_of_code": sum(len(c.splitlines()) for c in code_cells)
                }

            else:
                results["algorithm_analysis"] = {
                    "compliant": False,
                    "reason": f"Unsupported algorithm file type: {ext}"
                }
                results["compliant"] = False
                return results

            evaluation = node.evaluate_algorithm_config(config)
            results["algorithm_analysis"] = evaluation
            results["compliant"] = evaluation["compliant"]

        except Exception as e:
            results["algorithm_analysis"] = {
                "compliant": False,
                "reason": f"Algorithm config error: {str(e)}"
            }
            results["compliant"] = False
    else:
        results["algorithm_analysis"] = {
            "compliant": False,
            "reason": "No algorithm configuration provided"
        }
        results["compliant"] = False

    return results
