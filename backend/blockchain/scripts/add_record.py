import sys
import os
import time

# Add project root to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from blockchain.utils.upload_to_chain import upload_compliance_result

# Example usage
framework = "EU AI Act"
overall_status = "Passed"
hash_of_report = "abc123securehash456"
metadata = f"Generated on {int(time.time())}"

upload_compliance_result(
    framework=framework,
    overall_status=overall_status,
    hash_value=hash_of_report,
    metadata=metadata
)
