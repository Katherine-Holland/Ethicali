import os
import json
import uuid
from datetime import datetime

def save_audit_log(results, framework="EU AI Act", dataset_path=None, algorithm_path=None):
    """
    Saves the compliance validation results to a local JSON audit log.
    """
    # Create log directory if it doesn't exist
    log_dir = os.path.join("backend", "logging", "audit_logs")
    os.makedirs(log_dir, exist_ok=True)

    # Build log entry
    log_entry = {
        "id": str(uuid.uuid4()),
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "framework": framework,
        "dataset": os.path.basename(dataset_path) if dataset_path else None,
        "algorithm": os.path.basename(algorithm_path) if algorithm_path else None,
        "results": results
    }

    # Filename pattern: log_<timestamp>.json
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = f"log_{timestamp}.json"
    filepath = os.path.join(log_dir, filename)

    # Save to file
    with open(filepath, "w") as f:
        json.dump(log_entry, f, indent=4)

    print(f"📁 Audit log saved: {filepath}")
    return filepath
