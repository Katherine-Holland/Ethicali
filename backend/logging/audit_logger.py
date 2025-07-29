import os
import json
import uuid
import hashlib
from datetime import datetime
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv
from decimal import Decimal

# Load AWS credentials
load_dotenv()

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb', region_name=os.getenv('AWS_DEFAULT_REGION', 'us-east-1'))
audit_table = dynamodb.Table('AuditLogs')

def generate_result_hash(results):
    """Generate SHA-256 hash of results for tamper-proof logging."""
    serialized = json.dumps(results, sort_keys=True).encode('utf-8')
    return hashlib.sha256(serialized).hexdigest()

def convert_floats_to_decimal(obj):
    """Recursively convert floats to Decimal for DynamoDB."""
    if isinstance(obj, float):
        return Decimal(str(obj))
    elif isinstance(obj, list):
        return [convert_floats_to_decimal(i) for i in obj]
    elif isinstance(obj, dict):
        return {k: convert_floats_to_decimal(v) for k, v in obj.items()}
    else:
        return obj

def convert_decimal_to_float(obj):
    """Recursively convert Decimal values back to float for JSON serialization."""
    if isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, list):
        return [convert_decimal_to_float(i) for i in obj]
    elif isinstance(obj, dict):
        return {k: convert_decimal_to_float(v) for k, v in obj.items()}
    else:
        return obj

def save_audit_log(results, framework="EU AI Act", dataset_path=None, algorithm_path=None, client_id="default_client"):
    """
    Saves compliance validation results to DynamoDB and local JSON with SHA-256 hash.
    """
    # Create log directory if it doesn't exist
    log_dir = os.path.join("backend", "logging", "audit_logs")
    os.makedirs(log_dir, exist_ok=True)

    # ✅ Generate hash from original results before Decimal conversion
    result_hash = generate_result_hash(results)

    # ✅ Convert floats in results to Decimal for DynamoDB compatibility
    results = convert_floats_to_decimal(results)

    # Generate IDs and timestamps
    log_id = str(uuid.uuid4())
    timestamp_utc = datetime.utcnow().isoformat() + "Z"

    # Build log entry
    log_entry = {
        "id": log_id,
        "timestamp": timestamp_utc,
        "framework": framework,
        "dataset": os.path.basename(dataset_path) if dataset_path else None,
        "algorithm": os.path.basename(algorithm_path) if algorithm_path else None,
        "results": results,
        "hash": result_hash
    }

    # ✅ Save to DynamoDB
    try:
        compliance_status = "PASS"

        # Support both dict and list result formats
        if isinstance(results, dict):
            entries = results.values()
        elif isinstance(results, list):
            entries = results
        else:
            entries = []

        if any(isinstance(r, dict) and r.get("compliance") == "No" for r in entries):
            compliance_status = "FAIL"

        audit_table.put_item(Item={
            "ClientID": client_id,
            "Timestamp": timestamp_utc,
            "Framework": framework,
            "ComplianceStatus": compliance_status,
            "ResultHash": result_hash,
            "Metadata": {
                "Dataset": os.path.basename(dataset_path) if dataset_path else None,
                "Algorithm": os.path.basename(algorithm_path) if algorithm_path else None
            },
            "Results": results
        })
        print(f"✅ Audit log saved to DynamoDB with SHA-256 hash: {result_hash}")
    except ClientError as e:
        print(f"❌ Error saving to DynamoDB: {e}")

    # ✅ Save to local JSON (convert Decimals back to floats)
    json_safe_entry = convert_decimal_to_float(log_entry)
    timestamp_file = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = f"log_{timestamp_file}.json"
    filepath = os.path.join(log_dir, filename)

    with open(filepath, "w") as f:
        json.dump(json_safe_entry, f, indent=4)

    print(f"📁 Audit log saved locally: {filepath}")
    print(f"🔐 SHA-256 Hash: {result_hash}")
    return filepath, result_hash
