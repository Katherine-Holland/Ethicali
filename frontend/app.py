import streamlit as st
import sys
import os
from web3 import Web3
import json
from dotenv import load_dotenv

# Dynamically add backend path
BACKEND_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend", "blockchain", "scripts"))
if BACKEND_PATH not in sys.path:
    sys.path.append(BACKEND_PATH)

# Import BlockchainManager
try:
    from blockchain_manager import BlockchainManager
except ImportError as e:
    st.error("❌ Failed to import BlockchainManager.")
    st.stop()

# Load environment variables
load_dotenv()
PRIVATE_KEY = os.getenv("PRIVATE_KEY")

# Contract settings
CONTRACT_ADDRESS = "0xC62d657394C521Fc5735a6C4cA8daBb7d5369c0b"
ABI_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend", "blockchain", "abi", "contract_abi.json"))
PROVIDER_URL = "https://eth-sepolia.g.alchemy.com/v2/REDACTED_ALCHEMY_KEY_1"

# Initialize connection
try:
    blockchain_manager = BlockchainManager(CONTRACT_ADDRESS, ABI_PATH, PROVIDER_URL)
    st.success("✅ Connected to Sepolia network.")
except Exception as e:
    st.error("❌ Failed to connect to Sepolia network. Check your API key and connection.")
    st.exception(e)
    st.stop()

# Example UI
st.title("Compliance Results Dashboard")
st.write("This dashboard will show your stored compliance records soon!")
