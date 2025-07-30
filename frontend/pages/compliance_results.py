import os
import sys
import time
import re
from datetime import datetime
import streamlit as st
from dotenv import load_dotenv

# Load .env
load_dotenv()

# Fix ABI path regardless of working directory
ABI_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "backend", "blockchain", "abi", "contract_abi.json"))

# Add backend blockchain paths
BLOCKCHAIN_SCRIPTS_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "backend", "blockchain", "scripts"))
BLOCKCHAIN_UTILS_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "backend", "blockchain", "utils"))

for path in [BLOCKCHAIN_SCRIPTS_PATH, BLOCKCHAIN_UTILS_PATH]:
    if path not in sys.path:
        sys.path.append(path)

from blockchain_manager import BlockchainManager
from upload_to_chain import upload_compliance_result

# Sepolia Alchemy URL and contract address
PROVIDER_URL = f"https://eth-sepolia.g.alchemy.com/v2/{os.getenv('ALCHEMY_API_KEY')}"
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS")

# ✅ Check contract address early
if not CONTRACT_ADDRESS:
    st.error("❌ CONTRACT_ADDRESS not set in .env")
    st.stop()

# Connect to blockchain
try:
    blockchain_manager = BlockchainManager(CONTRACT_ADDRESS, ABI_PATH, PROVIDER_URL)
    st.success("✅ Connected to Sepolia network.")
except Exception as e:
    st.error("❌ Failed to connect to Sepolia network.")
    st.exception(e)
    st.stop()

# ───────────────────────────────────────────────────────────────
# 🧾 Section 1: Fetch and Decode Compliance Record
# ───────────────────────────────────────────────────────────────
st.title("📊 Compliance Results Dashboard")
st.subheader("🔍 Fetch and Decode Compliance Record")

tx_hash = st.text_input("Enter Transaction Hash")

if tx_hash:
    try:
        tx = blockchain_manager.w3.eth.get_transaction(tx_hash)
        decoded = blockchain_manager.decode_transaction_input(tx)

        # ✅ Ensure expected args exist
        args = decoded.get("args", {})
        if not args:
            st.error("❌ Invalid or non-compliance transaction format.")
        else:
            st.subheader("🧾 Decoded Compliance Record")
            st.success("✅ Record Found and Decoded")

            summary = args.get("_summary", "")
            secure_hash = args.get("_hash", "")
            metadata_raw = args.get("_metadata", "")

            # ✅ Extract readable timestamp if included in metadata
            match = re.search(r"(\d{10})$", metadata_raw)
            if match:
                timestamp = int(match.group(1))
                readable_time = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
                metadata = f"{metadata_raw[:-10].strip()} (at {readable_time})"
            else:
                metadata = metadata_raw

            st.markdown(f"**Summary:** {summary}")
            st.markdown(f"**Hash:** {secure_hash}")
            st.markdown(f"**Metadata:** {metadata}")

            # ✅ Fetch gas used from receipt for accuracy
            receipt = blockchain_manager.w3.eth.get_transaction_receipt(tx_hash)

            st.subheader("📦 Transaction Info")
            st.json({
                "From": tx["from"],
                "To": tx["to"],
                "Gas Used": receipt["gasUsed"],
                "Nonce": tx["nonce"],
                "Block Number": tx["blockNumber"]
            })

    except Exception as e:
        st.error(f"❌ Error: {e}")

# ───────────────────────────────────────────────────────────────
# 📤 Section 2: Submit New Compliance Record to Blockchain
# ───────────────────────────────────────────────────────────────
st.markdown("---")
st.header("📝 Submit New Compliance Result to Audit Ledger")

# Use session state or fallback defaults
selected_framework = st.session_state.get("selected_framework", "EU AI Act")
overall_status = st.session_state.get("overall_status", "Passed")
hash_of_report = st.session_state.get("hash_of_report", "abc123securehash456")
report_timestamp = int(time.time())

st.markdown(f"**Framework:** `{selected_framework}`")
st.markdown(f"**Result:** `{overall_status}`")
st.markdown(f"**Hash:** `{hash_of_report}`")

if st.button("📤 Submit to Audit Ledger"):
    with st.spinner("Submitting compliance record..."):
        try:
            tx_hash = upload_compliance_result(
                framework=selected_framework,
                overall_status=overall_status,
                hash_value=hash_of_report,
                metadata=f"Generated on {report_timestamp}"
            )
            st.success("✅ Record submitted to audit ledger.")
            st.markdown(f"🔗 **Tx Hash**: `{tx_hash}`")
            st.markdown(f"📅 **Timestamp**: {report_timestamp}")
        except Exception as e:
            st.error("❌ Failed to submit record.")
            st.exception(e)
