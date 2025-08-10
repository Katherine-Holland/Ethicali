# backend/logging/audit_logger.py
import os
import json
import uuid
import hashlib
import time
from datetime import datetime, timezone
from decimal import Decimal

import boto3
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key

# -------- Config --------
TABLE_NAME = os.getenv("ETHICALI_DDB_TABLE", "EthicaliAuditLogs")
REGION = os.getenv("AWS_REGION") or os.getenv("AWS_DEFAULT_REGION", "us-east-1")

dynamodb = boto3.resource("dynamodb", region_name=REGION)
table = dynamodb.Table(TABLE_NAME)


# -------- Helpers --------
def _now_iso() -> str:
    """UTC ISO-8601 without microseconds, timezone-aware."""
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _now_filename_stamp() -> str:
    """UTC timestamp suitable for filenames (no colons)."""
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def generate_result_hash(results: dict | list) -> str:
    """Generate SHA-256 over a canonical JSON encoding of results."""
    serialized = json.dumps(results, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(serialized).hexdigest()


def convert_floats_to_decimal(obj):
    """Recursively convert float -> Decimal for DynamoDB."""
    if isinstance(obj, float):
        return Decimal(str(obj))
    if isinstance(obj, dict):
        return {k: convert_floats_to_decimal(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [convert_floats_to_decimal(v) for v in obj]
    return obj


def convert_decimal_to_float(obj):
    """Recursively convert Decimal -> float for JSON serialization."""
    if isinstance(obj, Decimal):
        return float(obj)
    if isinstance(obj, dict):
        return {k: convert_decimal_to_float(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [convert_decimal_to_float(v) for v in obj]
    return obj


# -------- Write API --------
def save_audit_log(
    results: dict | list,
    framework: str = "EU_AI_ACT",
    dataset_path: str | None = None,
    algorithm_path: str | None = None,
    client_id: str = "default_client",
) -> tuple[str, str]:
    """
    Save validation results to DynamoDB and a local JSON file.
    Returns (local_json_filepath, sha256_hash).

    DynamoDB keys:
      pk = TENANT#{client_id}
      sk = RUN#{ISO_TIMESTAMP}#{run_id}
    """
    # Lambda-safe local dir
    log_dir = os.path.join("/tmp", "audit_logs")
    os.makedirs(log_dir, exist_ok=True)

    # Hash BEFORE Decimal conversion
    result_hash = generate_result_hash(results)

    # Convert floats for DynamoDB
    results_dec = convert_floats_to_decimal(results)

    # IDs and timestamps
    ts_iso = _now_iso()
    ts_epoch = int(time.time())
    run_id = uuid.uuid4().hex[:12]

    # Derive PASS/FAIL: any {"compliance": "No"} in results => FAIL
    compliance_status = "PASS"
    if isinstance(results, dict):
        entries = results.values()
    elif isinstance(results, list):
        entries = results
    else:
        entries = []
    if any(isinstance(r, dict) and r.get("compliance") == "No" for r in entries):
        compliance_status = "FAIL"

    item = {
        "pk": f"TENANT#{client_id}",
        "sk": f"RUN#{ts_iso}#{run_id}",
        "tenant_id": client_id,
        "run_id": run_id,
        "ts": ts_iso,
        "ts_epoch": ts_epoch,
        "framework": framework,          # e.g., EU_AI_ACT
        "status": compliance_status,     # PASS / FAIL
        "result_hash": result_hash,
        "metadata": {
            "dataset": os.path.basename(dataset_path) if dataset_path else None,
            "algorithm": os.path.basename(algorithm_path) if algorithm_path else None,
            "region": REGION,
        },
        "results": results_dec,          # Decimal-safe payload
    }

    try:
        table.put_item(Item=item)
        print(f"✅ DynamoDB write OK → table={TABLE_NAME}, region={REGION}")
    except ClientError as e:
        msg = e.response.get("Error", {}).get("Message", str(e))
        print(f"❌ DynamoDB ClientError: {msg}")
    except Exception as e:
        print(f"❌ DynamoDB unexpected error: {e}")

    # Local JSON copy (useful in Lambda + debugging)
    log_entry = {
        "id": run_id,
        "timestamp": ts_iso,
        "framework": framework,
        "dataset": os.path.basename(dataset_path) if dataset_path else None,
        "algorithm": os.path.basename(algorithm_path) if algorithm_path else None,
        "results": results,  # original structure (floats OK for JSON)
        "hash": result_hash,
    }
    json_safe_entry = convert_decimal_to_float(log_entry)
    filename = f"log_{_now_filename_stamp()}.json"
    filepath = os.path.join(log_dir, filename)
    with open(filepath, "w") as f:
        json.dump(json_safe_entry, f, indent=4)

    print(f"📁 Local log saved: {filepath}")
    print(f"🔐 SHA-256 Hash: {result_hash}")

    return filepath, result_hash


# -------- Read API --------
def fetch_latest_runs(tenant_id: str, limit: int = 20) -> list[dict]:
    """
    Query the latest runs for a tenant, newest first.
    Relies on sk starting with 'RUN#<ISO>...'
    """
    pk = f"TENANT#{tenant_id}"
    try:
        resp = table.query(
            KeyConditionExpression=Key("pk").eq(pk) & Key("sk").begins_with("RUN#"),
            ScanIndexForward=False,  # newest first
            Limit=max(1, min(limit, 100)),
        )
        items = resp.get("Items", [])
        # Convert Decimals back to floats for easy JSON use
        return [convert_decimal_to_float(it) for it in items]
    except ClientError as e:
        msg = e.response.get("Error", {}).get("Message", str(e))
        print(f"❌ Query ClientError: {msg}")
        return []
    except Exception as e:
        print(f"❌ Query unexpected error: {e}")
        return []


# -------- Optional CLI smoke test --------
if __name__ == "__main__":
    # 1) Write
    fake_results = {
        "bias": {"compliance": "Yes", "score": 0.02, "threshold": 0.05},
        "transparency": {"compliance": "Yes"},
        "accountability": {"compliance": "Yes"},
    }
    path, h = save_audit_log(
        results=fake_results,
        framework="EU_AI_ACT",
        dataset_path="/path/to/dataset.csv",
        algorithm_path="/path/to/model.pkl",
        client_id="demo-tenant",
    )
    print("Result JSON:", path)
    print("Result Hash:", h)

    # 2) Read latest
    latest = fetch_latest_runs("demo-tenant", limit=5)
    print("Latest runs:", json.dumps(latest, indent=2))
