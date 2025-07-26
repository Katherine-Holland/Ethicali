import json
import os
import traceback
from backend.validator.eu_ai_act.eu_bias_node import validate_bias
from backend.validator.eu_ai_act.eu_transparency_node import validate_transparency
from backend.validator.eu_ai_act.eu_fairness_node import validate_fairness
from backend.validator.eu_ai_act.eu_accountability_node import validate_accountability
from backend.validator.eu_ai_act.eu_risk_node import validate_risk
from backend.validator.eu_ai_act.eu_explainability_node import validate_explainability
from backend.validator.eu_ai_act.eu_robustness_node import validate_robustness
from backend.validator.eu_ai_act.eu_oversight_node import validate_oversight

DEBUG_LOG = os.path.join(os.path.dirname(__file__), "..", "..", "logging", "debug.log")
os.makedirs(os.path.dirname(DEBUG_LOG), exist_ok=True)

def log_error(e):
    with open(DEBUG_LOG, "a") as log:
        log.write("\n" + "-"*50 + "\n")
        log.write(traceback.format_exc())
        log.write("\n")

def to_json_safe(data):
    try:
        return json.loads(json.dumps(data, default=str))
    except Exception:
        return str(data)

def validate_eu_framework(dataset_path=None, algorithm_path=None):
    """Validate dataset + algorithm for EU AI Act compliance."""
    results = {}

    # === Bias Node ===
    bias_result = {}
    if dataset_path:
        try:
            bias_result['dataset'] = to_json_safe(validate_bias(dataset_path))
        except Exception as e:
            log_error(e)
            bias_result['dataset'] = {"status": "error", "message": str(e)}
    else:
        bias_result['dataset'] = {"status": "skipped", "message": "No dataset provided"}

    if algorithm_path:
        try:
            bias_result['algorithm'] = to_json_safe(validate_bias(dataset_path=None, algorithm_path=algorithm_path))
        except Exception as e:
            log_error(e)
            bias_result['algorithm'] = {"status": "error", "message": str(e)}
    else:
        bias_result['algorithm'] = {"status": "skipped", "message": "No algorithm provided"}

    results['bias'] = bias_result

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
    accountability_result = {}
    if dataset_path:
        try:
            accountability_result['dataset'] = to_json_safe(validate_accountability(dataset_path))
        except Exception as e:
            log_error(e)
            accountability_result['dataset'] = {"status": "error", "message": str(e)}
    else:
        accountability_result['dataset'] = {"status": "skipped", "message": "No dataset provided"}

    if algorithm_path:
        try:
            from backend.validator.eu_ai_act.eu_accountability_node import AccountabilityNode
            with open(algorithm_path, "r") as f:
                algo_code = f.read()
            mock_algo = {"timestamp": "2023-01-01T12:00:00Z", "version": "1.0.0", "decision_log": "Logged automatically"}
            node = AccountabilityNode()
            accountability_result['algorithm'] = to_json_safe(node.evaluate_algorithm(mock_algo))
        except Exception as e:
            log_error(e)
            accountability_result['algorithm'] = {"status": "error", "message": str(e)}
    else:
        accountability_result['algorithm'] = {"status": "skipped", "message": "No algorithm provided"}

    results['accountability'] = accountability_result

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
