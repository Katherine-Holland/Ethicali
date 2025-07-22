import os
import sys
from dotenv import load_dotenv
import streamlit as st
import re
from datetime import datetime

# Load .env
load_dotenv()

# Fix ABI path regardless of working directory
ABI_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "backend", "blockchain", "abi", "contract_abi.json"))

# Add backend path
BACKEND_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "backend", "blockchain", "scripts"))
if BACKEND_PATH not in sys.path:
    sys.path.append(BACKEND_PATH)

from blockchain_manager import BlockchainManager

# Sepolia Alchemy URL
PROVIDER_URL = f"https://eth-sepolia.g.alchemy.com/v2/{os.getenv('ALCHEMY_API_KEY')}"
CONTRACT_ADDRESS = "0xC62d657394C521Fc5735a6C4cA8daBb7d5369c0b"

# Try to connect
try:
    blockchain_manager = BlockchainManager(CONTRACT_ADDRESS, ABI_PATH, PROVIDER_URL)
    st.success("✅ Connected to Sepolia network.")
except Exception as e:
    st.error("❌ Failed to connect to Sepolia network.")
    st.exception(e)
    st.stop()

# UI
st.title("📊 Compliance Results Dashboard")
st.subheader("🔍 Fetch and Decode Compliance Record")

tx_hash = st.text_input("Enter Transaction Hash")

if tx_hash:
    try:
        tx = blockchain_manager.w3.eth.get_transaction(tx_hash)
        decoded = blockchain_manager.decode_transaction_input(tx)

        st.subheader("🧾 Decoded Compliance Record")
        st.success("✅ Record Found and Decoded")

        summary = decoded["args"]["_summary"]
        secure_hash = decoded["args"]["_hash"]
        metadata_raw = decoded["args"]["_metadata"]

        # Extract readable timestamp from metadata if present
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

        st.subheader("📦 Transaction Info")
        st.json({
            "From": tx["from"],
            "To": tx["to"],
            "Gas Used": tx["gas"],
            "Nonce": tx["nonce"],
            "Block Number": tx["blockNumber"]
        })

    except Exception as e:
        st.error(f"❌ Error: {e}")
