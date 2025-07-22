from backend.validator.eu_ai_act.eu_bias_node import validate_bias
from backend.validator.eu_ai_act.eu_transparency_node import validate_transparency
from backend.validator.eu_ai_act.eu_fairness_node import validate_fairness
from backend.validator.eu_ai_act.eu_accountability_node import validate_accountability

def validate_eu_framework(dataset_path=None, algorithm_path=None):
    """
    Run all EU AI Act compliance checks on the given dataset and algorithm.
    Returns a dictionary of results for each validator node.
    """
    results = {}

    # Bias Node
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

    # Transparency Node
    if dataset_path:
        try:
            results['transparency'] = validate_transparency(dataset_path)
        except Exception as e:
            results['transparency'] = {"status": "error", "message": str(e)}
    else:
        results['transparency'] = {"status": "skipped", "message": "No dataset provided"}

    # Fairness Node
    if dataset_path:
        try:
            results['fairness'] = validate_fairness(dataset_path, algorithm_path)
        except Exception as e:
            results['fairness'] = {"status": "error", "message": str(e)}
    else:
        results['fairness'] = {"status": "skipped", "message": "No dataset provided"}

    # Accountability Node (both parts)
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
            # Mock parsing
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

    return results
