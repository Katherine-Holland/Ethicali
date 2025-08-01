import os
print("🔥 Debug: /var/task contents:", os.listdir("/var/task"))
if os.path.exists("/opt"):
    print("🔥 Debug: /opt contents:", os.listdir("/opt"))
import json
import sys, os
import boto3
import traceback

# ✅ Import EU validator
from validator.eu_ai_act.validate_eu import validate_eu_framework
# ✅ Import audit logger from your app_logging folder
from audit_logger import save_audit_log

# === AWS Clients ===
s3 = boto3.client('s3')

# === Temp file paths in Lambda ===
TMP_DATASET = "/tmp/dataset.csv"
TMP_ALGORITHM = "/tmp/algorithm.py"

def lambda_handler(event, context):
    try:
        print("🚀 Lambda triggered, event:", event)

        # ✅ Parse payload
        if "body" in event and isinstance(event["body"], str):
            payload = json.loads(event["body"])
        else:
            payload = event

        bucket = payload.get("bucket")
        dataset_key = payload.get("dataset_key")
        algorithm_key = payload.get("algorithm_key")

        dataset_path = None
        algorithm_path = None

        # ✅ Download dataset if provided
        if bucket and dataset_key:
            dataset_path = TMP_DATASET
            s3.download_file(bucket, dataset_key, dataset_path)
            print(f"✅ Downloaded dataset: s3://{bucket}/{dataset_key}")

        # ✅ Download algorithm if provided
        if bucket and algorithm_key:
            algorithm_path = TMP_ALGORITHM
            s3.download_file(bucket, algorithm_key, algorithm_path)
            print(f"✅ Downloaded algorithm: s3://{bucket}/{algorithm_key}")

        if not dataset_path and not algorithm_path:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "No dataset or algorithm provided"})
            }

        # ✅ Run EU AI Act validation
        print("🚀 Running EU AI Act validation...")
        results = validate_eu_framework(dataset_path=dataset_path, algorithm_path=algorithm_path)

        # ✅ Save audit log to DynamoDB + /tmp
        save_audit_log(results, framework="EU AI Act", dataset_path=dataset_path, algorithm_path=algorithm_path)

        return {
            "statusCode": 200,
            "body": json.dumps({
                "status": "success",
                "results": results
            }, default=str)
        }

    except Exception as e:
        print("❌ Lambda error:", str(e))
        print(traceback.format_exc())
        return {
            "statusCode": 500,
            "body": json.dumps({
                "status": "error",
                "message": str(e),
                "traceback": traceback.format_exc()
            })
        }
