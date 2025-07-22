import streamlit as st
from web3 import Web3
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Connect to Sepolia network
alchemy_url = f"https://eth-sepolia.g.alchemy.com/v2/{os.getenv('ALCHEMY_API_KEY')}"
web3 = Web3(Web3.HTTPProvider(alchemy_url))

if web3.is_connected():
    st.success("Connected to Sepolia test network!")
else:
    st.error("Failed to connect to Sepolia network. Check your API key and connection.")

# Contract details (replace with actual details)
contract_address = "0xA570AA4ba24d271af3855d44a5995d90e6FA056c"  # Replace with your contract address
contract_abi = [
    {
        "inputs": [{"internalType": "string", "name": "_description", "type": "string"}],
        "name": "submitDecision",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
]

contract = web3.eth.contract(address=contract_address, abi=contract_abi)

# Streamlit Dashboard
st.title("Compliance Results Dashboard")

st.subheader("Fetch Compliance Results")

# Input transaction hash
tx_hash = st.text_input("Enter Transaction Hash:")

if tx_hash:
    try:
        # Fetch transaction receipt
        tx_receipt = web3.eth.get_transaction_receipt(tx_hash)
        st.write("Raw Transaction Receipt:")
        st.json(tx_receipt)

        # Decode logs
        st.write("Decoded Logs (if available):")
        decoded_logs = contract.events.DecisionFinalized().processReceipt(tx_receipt)
        st.json(decoded_logs)

    except Exception as e:
        st.error(f"Error fetching transaction: {e}")
