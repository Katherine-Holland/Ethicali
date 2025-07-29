import sys, os
# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from backend.logging import audit_logger

# Fake validation results for testing
results = [
    {"check": "Bias", "compliance": "Yes"},
    {"check": "Fairness", "compliance": "No"}
]

# Call the function
audit_logger.save_audit_log(
    results=results,
    framework="EU AI Act",
    dataset_path="test_dataset.csv",
    algorithm_path="test_algorithm.py",
    client_id="test_client"
)
