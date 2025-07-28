import json
import os
import csv
import traceback
from validator.eu_ai_act.eu_bias_node import validate_bias
from validator.eu_ai_act.eu_transparency_node import validate_transparency
from validator.eu_ai_act.eu_fairness_node import validate_fairness
from validator.eu_ai_act.eu_accountability_node import validate_accountability
from validator.eu_ai_act.eu_risk_node import validate_risk
from validator.eu_ai_act.eu_explainability_node import validate_explainability
from validator.eu_ai_act.eu_robustness_node import validate_robustness
from validator.eu_ai_act.eu_oversight_node import validate_oversight

DEBUG_LOG = "/tmp/debug.log"

def log_error(e):
    with open(DEBUG_LOG, "a") as log:
        log.write("\n" + "-" * 50 + "\n")
        log.write(traceback.format_exc())
        log.write("\n")

def to_json_safe(data):
    try:
        return json.loads(json.dumps(data, default=str))
    except Exception:
        return str(data)

def read_dataset(path):
    """Minimal CSV reader to avoid pandas/numpy dependencies."""
    if not path or not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = [row for row in reader]
            return {
                "columns": reader.fieldnames or [],
                "rows": rows
            }
    except Exception as e:
        log_error(e)
        return None

def validate_eu_framework(dataset_path=None, algorithm_path=None):
    """Validate dataset + algorithm for EU AI Act compliance."""
    results = {}

    # ✅ Load dataset into minimal structure
    dataset_obj = read_dataset(dataset_path) if dataset_path else None

    # === Bias Node ===
    try:
        results['bias'] = to_json_safe(validate_bias(dataset_path, algorithm_path))
    except Exception as e:
        log_error(e)
        results['bias'] = {"status": "error", "message": str(e)}

    # === Transparency ===
    try:
        results['transparency'] = to_json_safe(
            validate_transparency(dataset_path) if dataset_path else {"status": "skipped", "message": "No dataset provided"}
        )
    except Exception as e:
        log_error(e)
        results['transparency'] = {"status": "error", "message": str(e)}

    # === Fairness ===
    try:
        results['fairness'] = to_json_safe(
            validate_fairness(dataset_path, algorithm_path) if dataset_path else {"status": "skipped", "message": "No dataset provided"}
        )
    except Exception as e:
        log_error(e)
        results['fairness'] = {"status": "error", "message": str(e)}

    # === Accountability ===
    try:
        results['accountability'] = to_json_safe(validate_accountability(dataset_path, algorithm_path))
    except Exception as e:
        log_error(e)
        results['accountability'] = {"status": "error", "message": str(e)}

    # === Risk ===
    try:
        results['risk'] = to_json_safe(
            validate_risk(dataset_path, algorithm_path) if dataset_path or algorithm_path else {"status": "skipped", "message": "No inputs provided"}
        )
    except Exception as e:
        log_error(e)
        results['risk'] = {"status": "error", "message": str(e)}

    # === Explainability ===
    try:
        results['explainability'] = to_json_safe(
            validate_explainability(dataset_path, algorithm_path) if dataset_path or algorithm_path else {"status": "skipped", "message": "No inputs provided"}
        )
    except Exception as e:
        log_error(e)
        results['explainability'] = {"status": "error", "message": str(e)}

    # === Robustness ===
    try:
        results['robustness'] = to_json_safe(
            validate_robustness(dataset_path, algorithm_path) if dataset_path or algorithm_path else {"status": "skipped", "message": "No inputs provided"}
        )
    except Exception as e:
        log_error(e)
        results['robustness'] = {"status": "error", "message": str(e)}

    # === Oversight ===
    try:
        results['oversight'] = to_json_safe(
            validate_oversight(dataset_path, algorithm_path) if dataset_path or algorithm_path else {"status": "skipped", "message": "No inputs provided"}
        )
    except Exception as e:
        log_error(e)
        results['oversight'] = {"status": "error", "message": str(e)}

    return to_json_safe(results)
