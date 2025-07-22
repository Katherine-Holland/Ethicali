# validator/eu_ai_act/validate_eu.py

from backend.validator.eu_ai_act.eu_bias_node import validate_bias
from backend.validator.eu_ai_act.eu_transparency_node import validate_transparency
from backend.validator.eu_ai_act.eu_fairness_node import validate_fairness
from backend.validator.eu_ai_act.eu_accountability_node import validate_accountability



def validate_eu_framework(dataset_path, algorithm_path=None):
    """
    Run all EU AI Act compliance checks on the given dataset and algorithm.
    Returns a dictionary of results.
    """
    results = {}

    try:
        results['bias'] = validate_bias(dataset_path, algorithm_path)
    except Exception as e:
        results['bias'] = {"status": "error", "message": str(e)}

    try:
        results['transparency'] = validate_transparency(dataset_path)
    except Exception as e:
        results['transparency'] = {"status": "error", "message": str(e)}

    try:
        results['fairness'] = validate_fairness(dataset_path, algorithm_path)
    except Exception as e:
        results['fairness'] = {"status": "error", "message": str(e)}

    try:
        results['accountability'] = validate_accountability(dataset_path, algorithm_path)
    except Exception as e:
        results['accountability'] = {"status": "error", "message": str(e)}

    return results
