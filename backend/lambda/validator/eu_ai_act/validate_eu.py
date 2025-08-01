import json
import sys, os
import csv
import traceback

# Add backend root to path
BACKEND_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
if BACKEND_PATH not in sys.path:
    sys.path.append(BACKEND_PATH)

from validator.eu_ai_act.eu_bias_node import validate_bias
from validator.eu_ai_act.eu_transparency_node import validate_transparency
from validator.eu_ai_act.eu_fairness_node import validate_fairness
from validator.eu_ai_act.eu_accountability_node import validate_accountability
from validator.eu_ai_act.eu_risk_node import validate_risk
from validator.eu_ai_act.eu_explainability_node import validate_explainability
from validator.eu_ai_act.eu_robustness_node import validate_robustness
from validator.eu_ai_act.eu_oversight_node import validate_oversight

# ✅ Using logging.audit_logger now
from logging.audit_logger import save_audit_log

print("✅ Running validate_eu.py from S3 bundle!")


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

def normalize_node_output(result, dataset_path, algorithm_path):
    """Ensure every node returns {dataset:..., algorithm:...} structure."""
    if not isinstance(result, dict):
        return {"dataset": {"status": "error", "message": "Invalid node output"}, 
                "algorithm": {"status": "error", "message": "Invalid node output"}}

    # If already in dataset/algorithm format, return as-is
    if "dataset" in result or "algorithm" in result:
        if "dataset" not in result:
            result["dataset"] = {"status": "skipped", "message": "No dataset provided"}
        if "algorithm" not in result:
            result["algorithm"] = {"status": "skipped", "message": "No algorithm provided"}
        return result

    # Wrap single result in both keys if needed
    return {
        "dataset": result if dataset_path else {"status": "skipped", "message": "No dataset provided"},
        "algorithm": result if algorithm_path else {"status": "skipped", "message": "No algorithm provided"}
    }

def validate_eu_framework(dataset_path=None, algorithm_path=None):
    """Validate dataset + algorithm for EU AI Act compliance."""
    results = {}

    nodes = {
        "bias": validate_bias,
        "transparency": validate_transparency,
        "fairness": validate_fairness,
        "accountability": validate_accountability,
        "risk": validate_risk,
        "explainability": validate_explainability,
        "robustness": validate_robustness,
        "oversight": validate_oversight
    }

    for node_name, node_func in nodes.items():
        try:
            raw_result = node_func(dataset_path, algorithm_path)
            results[node_name] = to_json_safe(
                normalize_node_output(raw_result, dataset_path, algorithm_path)
            )
        except Exception as e:
            log_error(e)
            results[node_name] = {"dataset": {"status": "error", "message": str(e)},
                                  "algorithm": {"status": "error", "message": str(e)}}

    # ✅ Save audit log to DynamoDB and local
    save_audit_log(
        results=results,
        framework="EU AI Act",
        dataset_path=dataset_path,
        algorithm_path=algorithm_path,
        client_id="default_client"
    )

    return to_json_safe(results)