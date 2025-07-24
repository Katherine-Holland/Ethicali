from backend.validator.eu_ai_act.eu_bias_node import validate_bias
from backend.validator.eu_ai_act.eu_transparency_node import validate_transparency
from backend.validator.eu_ai_act.eu_fairness_node import validate_fairness
from backend.validator.eu_ai_act.eu_accountability_node import validate_accountability
from backend.validator.eu_ai_act.eu_risk_node import validate_risk
from backend.validator.eu_ai_act.eu_explainability_node import validate_explainability
from backend.validator.eu_ai_act.eu_robustness_node import validate_robustness
from backend.validator.eu_ai_act.eu_oversight_node import validate_oversight


def validate_eu_framework(dataset_path=None, algorithm_path=None):
    results = {}

    # --- Bias Node ---
    bias_result = {}
    if dataset_path:
        try:
            bias_result['dataset'] = validate_bias(dataset_path)
        except Exception as e:
            bias_result['dataset'] = {"status": "error", "message": str(e)}
    else:
        bias_result['dataset'] = {"status": "skipped", "message": "No dataset provided"}

    if algorithm_path:
        try:
            bias_result['algorithm'] = validate_bias(dataset_path=None, algorithm_path=algorithm_path)
        except Exception as e:
            bias_result['algorithm'] = {"status": "error", "message": str(e)}
    else:
        bias_result['algorithm'] = {"status": "skipped", "message": "No algorithm provided"}

    results['bias'] = bias_result

    # --- Transparency Node ---
    results['transparency'] = (
        validate_transparency(dataset_path)
        if dataset_path else {"status": "skipped", "message": "No dataset provided"}
    )

    # --- Fairness Node ---
    results['fairness'] = (
        validate_fairness(dataset_path, algorithm_path)
        if dataset_path else {"status": "skipped", "message": "No dataset provided"}
    )

    # --- Accountability Node ---
    accountability_result = {}
    if dataset_path:
        try:
            accountability_result['dataset'] = validate_accountability(dataset_path)
        except Exception as e:
            accountability_result['dataset'] = {"status": "error", "message": str(e)}
    else:
        accountability_result['dataset'] = {"status": "skipped", "message": "No dataset provided"}

    if algorithm_path:
        try:
            from backend.validator.eu_ai_act.eu_accountability_node import AccountabilityNode
            import json
            with open(algorithm_path, "r") as f:
                algo_code = f.read()

            mock_algo = {
                "timestamp": "2023-01-01T12:00:00Z",
                "version": "1.0.0",
                "decision_log": "Logged automatically"
            }

            node = AccountabilityNode()
            accountability_result['algorithm'] = node.evaluate_algorithm(mock_algo)
        except Exception as e:
            accountability_result['algorithm'] = {"status": "error", "message": str(e)}
    else:
        accountability_result['algorithm'] = {"status": "skipped", "message": "No algorithm provided"}

    results['accountability'] = accountability_result

    # --- Risk Node ---
    results['risk'] = (
        validate_risk(dataset_path, algorithm_path)
        if dataset_path or algorithm_path else {"status": "skipped", "message": "No inputs provided"}
    )

    # --- Explainability Node ---
    results['explainability'] = (
        validate_explainability(dataset_path, algorithm_path)
        if dataset_path or algorithm_path else {"status": "skipped", "message": "No inputs provided"}
    )

    # --- Robustness Node ---
    results['robustness'] = (
        validate_robustness(dataset_path, algorithm_path)
        if dataset_path or algorithm_path else {"status": "skipped", "message": "No inputs provided"}
    )

    # --- Oversight Node ---
    results['oversight'] = (
        validate_oversight(dataset_path, algorithm_path)
        if dataset_path or algorithm_path else {"status": "skipped", "message": "No inputs provided"}
    )

    return results
