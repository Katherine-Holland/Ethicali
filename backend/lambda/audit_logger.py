# backend/lambda/audit_logger.py
import os
import json
import uuid
import hashlib
import time
from datetime import datetime, timezone, timedelta
from decimal import Decimal

import boto3
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key, Attr

# ----------- FastAPI (user-facing API) -----------
try:
    from fastapi import FastAPI, Query, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    _FASTAPI_AVAILABLE = True
except Exception:
    _FASTAPI_AVAILABLE = False

# --------------- Config ----------------
TABLE_NAME = os.getenv("ETHICALI_DDB_TABLE", "EthicaliAuditLogs")
REGION = os.getenv("AWS_REGION") or os.getenv("AWS_DEFAULT_REGION", "us-east-1")

dynamodb = boto3.resource("dynamodb", region_name=REGION)
table = dynamodb.Table(TABLE_NAME)

# ------------- Helpers -----------------
def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

def _now_filename_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

def generate_result_hash(results: dict | list) -> str:
    serialized = json.dumps(results, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(serialized).hexdigest()

def convert_floats_to_decimal(obj):
    if isinstance(obj, float):
        return Decimal(str(obj))
    if isinstance(obj, dict):
        return {k: convert_floats_to_decimal(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [convert_floats_to_decimal(v) for v in obj]
    return obj

def convert_decimal_to_float(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    if isinstance(obj, dict):
        return {k: convert_decimal_to_float(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [convert_decimal_to_float(v) for v in obj]
    return obj

# ------------- Write API ----------------
def save_audit_log(
    results: dict | list,
    framework: str = "EU_AI_ACT",
    dataset_path: str | None = None,
    algorithm_path: str | None = None,
    client_id: str = "default_client",
) -> tuple[str, str, str]:
    """
    Save validation results to DynamoDB and a local JSON file.
    Keys:
      pk = TENANT#{client_id}
      sk = RUN#{ISO_TIMESTAMP}#{run_id}
    """
    log_dir = os.path.join("/tmp", "audit_logs")
    os.makedirs(log_dir, exist_ok=True)

    result_hash = generate_result_hash(results)
    results_dec = convert_floats_to_decimal(results)

    ts_iso = _now_iso()
    ts_epoch = int(time.time())
    run_id = uuid.uuid4().hex[:12]

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
        "framework": framework,
        "status": compliance_status,
        "result_hash": result_hash,
        "metadata": {
            "dataset": os.path.basename(dataset_path) if dataset_path else None,
            "algorithm": os.path.basename(algorithm_path) if algorithm_path else None,
            "region": REGION,
        },
        "results": results_dec,
    }

    try:
        table.put_item(Item=item)
        print(f"✅ DynamoDB write OK → table={TABLE_NAME}, region={REGION}")
    except ClientError as e:
        msg = e.response.get("Error", {}).get("Message", str(e))
        print(f"❌ DynamoDB ClientError: {msg}")
    except Exception as e:
        print(f"❌ DynamoDB unexpected error: {e}")

    log_entry = {
        "id": run_id,
        "timestamp": ts_iso,
        "framework": framework,
        "dataset": os.path.basename(dataset_path) if dataset_path else None,
        "algorithm": os.path.basename(algorithm_path) if algorithm_path else None,
        "results": results,
        "hash": result_hash,
    }
    json_safe_entry = convert_decimal_to_float(log_entry)
    filename = f"log_{_now_filename_stamp()}.json"
    filepath = os.path.join(log_dir, filename)
    with open(filepath, "w") as f:
        json.dump(json_safe_entry, f, indent=4)

    print(f"📁 Local log saved: {filepath}")
    print(f"🔐 SHA-256 Hash: {result_hash}")
    return filepath, result_hash, run_id
# ------------- Read APIs ----------------
def fetch_latest_runs(tenant_id: str, limit: int = 20) -> list[dict]:
    pk = f"TENANT#{tenant_id}"
    try:
        resp = table.query(
            KeyConditionExpression=Key("pk").eq(pk) & Key("sk").begins_with("RUN#"),
            ScanIndexForward=False,
            Limit=max(1, min(limit, 100)),
        )
        items = resp.get("Items", [])
        return [convert_decimal_to_float(it) for it in items]
    except Exception as e:
        print(f"❌ fetch_latest_runs error: {e}")
        return []

def fetch_runs_by_status(tenant_id: str, status: str, limit: int = 20) -> list[dict]:
    pk = f"TENANT#{tenant_id}"
    try:
        resp = table.query(
            KeyConditionExpression=Key("pk").eq(pk) & Key("sk").begins_with("RUN#"),
            FilterExpression=Attr("status").eq(status.upper()),
            ScanIndexForward=False,
            Limit=max(1, min(limit, 100)),
        )
        items = resp.get("Items", [])
        return [convert_decimal_to_float(it) for it in items]
    except Exception as e:
        print(f"❌ fetch_runs_by_status error: {e}")
        return []

def fetch_runs_in_range(tenant_id: str, start_iso: str, end_iso: str, limit: int = 100) -> list[dict]:
    if start_iso > end_iso:
        start_iso, end_iso = end_iso, start_iso
    pk = f"TENANT#{tenant_id}"
    start_sk = f"RUN#{start_iso}"
    end_sk   = f"RUN#{end_iso}\uffff"
    try:
        resp = table.query(
            KeyConditionExpression=Key("pk").eq(pk) & Key("sk").between(start_sk, end_sk),
            ScanIndexForward=False,
            Limit=max(1, min(limit, 1000)),
        )
        items = resp.get("Items", [])
        return [convert_decimal_to_float(it) for it in items]
    except Exception as e:
        print(f"❌ fetch_runs_in_range error: {e}")
        return []

# --- New: robust fetch by run_id (no timestamp required) ---
def fetch_run_by_id(tenant_id: str, run_id: str) -> dict | None:
    """
    Scans this tenant's runs newest→oldest in pages until run_id matches.
    Works for MVP sizes; upgrade to GSI on run_id later if needed.
    """
    pk = f"TENANT#{tenant_id}"
    start_key = None
    while True:
        try:
            params = {
                "KeyConditionExpression": Key("pk").eq(pk) & Key("sk").begins_with("RUN#"),
                "ScanIndexForward": False,
                "Limit": 100,
            }
            if start_key:  # only include when present
                params["ExclusiveStartKey"] = start_key

            resp = table.query(**params)

            for it in resp.get("Items", []):
                if it.get("run_id") == run_id:
                    return convert_decimal_to_float(it)

            start_key = resp.get("LastEvaluatedKey")
            if not start_key:
                return None
        except Exception as e:
            print(f"❌ fetch_run_by_id error: {e}")
            return None


# --- New: exact get by full sort key (pk + sk) ---
def fetch_run_by_sk(tenant_id: str, sk: str) -> dict | None:
    """
    Fast O(1) lookup when you have the exact 'sk' from a list.
    Example sk: 'RUN#2025-08-10T07:55:38+00:00#a1b0e1c7815c'
    """
    try:
        resp = table.get_item(Key={"pk": f"TENANT#{tenant_id}", "sk": sk})
        item = resp.get("Item")
        return convert_decimal_to_float(item) if item else None
    except Exception as e:
        print(f"❌ fetch_run_by_sk error: {e}")
        return None

# ------------- FastAPI App --------------
app = None
if _FASTAPI_AVAILABLE:
    app = FastAPI(title="Ethicali Audit API", version="1.0.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    def health():
        return {"ok": True, "table": TABLE_NAME, "region": REGION, "time": _now_iso()}

    @app.get("/audit/latest")
    def api_latest(
        tenant_id: str = Query(..., description="Tenant identifier"),
        limit: int = Query(10, ge=1, le=100),
    ):
        items = fetch_latest_runs(tenant_id, limit)
        return {"ok": True, "count": len(items), "items": items}

    @app.get("/audit/status")
    def api_status(
        tenant_id: str = Query(..., description="Tenant identifier"),
        status: str = Query(..., pattern="^(?i)(PASS|FAIL|WARN)$", description="PASS/FAIL/WARN"),
        limit: int = Query(20, ge=1, le=100),
    ):
        items = fetch_runs_by_status(tenant_id, status.upper(), limit)
        return {"ok": True, "count": len(items), "items": items}

    @app.get("/audit/range")
    def api_range(
        tenant_id: str = Query(..., description="Tenant identifier"),
        start_iso: str = Query(..., description="ISO start, e.g. 2025-08-03T00:00:00+00:00"),
        end_iso: str = Query(..., description="ISO end, e.g. 2025-08-10T23:59:59+00:00"),
        limit: int = Query(100, ge=1, le=1000),
    ):
        items = fetch_runs_in_range(tenant_id, start_iso, end_iso, limit)
        return {"ok": True, "count": len(items), "items": items}

    # Rewritten: works with run_id only (no timestamp)
    @app.get("/audit/run")
    def api_run(
        tenant_id: str = Query(..., description="Tenant identifier"),
        run_id: str = Query(..., description="Run identifier returned by writes"),
    ):
        item = fetch_run_by_id(tenant_id, run_id)
        if not item:
            raise HTTPException(status_code=404, detail="Run not found")
        return {"ok": True, "item": item}

    # Exact-key route (pk+sk) — handy from list view
    @app.get("/audit/run_by_sk")
    def api_run_by_sk(
        tenant_id: str = Query(..., description="Tenant identifier"),
        sk: str = Query(..., description="Exact sort key from list response"),
    ):
        item = fetch_run_by_sk(tenant_id, sk)
        if not item:
            raise HTTPException(status_code=404, detail="Run not found")
        return {"ok": True, "item": item}

# ------------- CLI Smoke Test ----------
if __name__ == "__main__":
    fake_results = {
        "bias": {"compliance": "Yes", "score": 0.02, "threshold": 0.05},
        "transparency": {"compliance": "Yes"},
        "accountability": {"compliance": "Yes"},
    }
    path, h = save_audit_log(
        results=fake_results,
        framework="EU_AI_ACT",
        dataset_path="dataset.csv",
        algorithm_path="model.pkl",
        client_id="demo-tenant",
    )
    print("Result JSON:", path)
    print("Result Hash:", h)

    latest = fetch_latest_runs("demo-tenant", limit=5)
    print("Latest runs:", json.dumps(latest, indent=2))
