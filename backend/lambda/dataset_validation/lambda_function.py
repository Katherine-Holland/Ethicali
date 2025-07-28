import json
import os
import boto3
import traceback

from validator.eu_ai_act.validate_eu import validate_eu_framework

s3 = boto3.client('s3')

TMP_DATASET = "/tmp/dataset.csv"
TMP_ALGORITHM = "/tmp/algorithm.py"

def lambda_handler(event, context):
    try:
        # ✅ Parse API Gateway payload
        if "body" in event and isinstance(event["body"], str):
            payload = json.loads(event["body"])
        else:
            payload = event

        bucket = payload.get("bucket")
        dataset_key = payload.get("dataset_key")
        algorithm_key = payload.get("algorithm_key")

        dataset_path = None
        algorithm_path = None

        # === Download dataset from S3 ===
        if bucket and dataset_key:
            dataset_path = TMP_DATASET
            s3.download_file(bucket, dataset_key, dataset_path)

        # === Download algorithm from S3 ===
        if bucket and algorithm_key:
            algorithm_path = TMP_ALGORITHM
            s3.download_file(bucket, algorithm_key, algorithm_path)

        if not dataset_path and not algorithm_path:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "No dataset or algorithm provided"})
            }

        # === Run EU AI validation ===
        results = validate_eu_framework(dataset_path=dataset_path, algorithm_path=algorithm_path)

        return {
            "statusCode": 200,
            "body": json.dumps({
                "status": "success",
                "results": results
            }, default=str)
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({
                "status": "error",
                "message": str(e),
                "traceback": traceback.format_exc()
            })
        }
