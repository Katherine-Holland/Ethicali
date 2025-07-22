from blockchain_manager import BlockchainManager
from web3 import Web3
from eth_account import Account
from dotenv import load_dotenv
import os
import time

# Load private key from .env
load_dotenv()
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
if not PRIVATE_KEY:
    raise ValueError("❌ PRIVATE_KEY not found in environment. Please check your .env file.")

# Setup
CONTRACT_ADDRESS = "0xC62d657394C521Fc5735a6C4cA8daBb7d5369c0b"
ABI_PATH = "backend/blockchain/abi/contract_abi.json"
PROVIDER_URL = "https://eth-sepolia.g.alchemy.com/v2/REDACTED_ALCHEMY_KEY_1"

# Initialize blockchain manager
blockchain_manager = BlockchainManager(CONTRACT_ADDRESS, ABI_PATH, PROVIDER_URL)

# Prepare compliance data
summary = "Bias check: Passed EU AI compliance"
data_hash = "abc123securehash456"
metadata = f"Added via test script at {int(time.time())}"

# Build and sign transaction
account = Account.from_key(PRIVATE_KEY)
nonce = blockchain_manager.w3.eth.get_transaction_count(account.address)

txn = blockchain_manager.contract.functions.addComplianceRecord(
    summary, data_hash, metadata
).build_transaction({
    'from': account.address,
    'nonce': nonce,
    'gas': 2000000,
    'gasPrice': blockchain_manager.w3.eth.gas_price
})

signed_txn = blockchain_manager.w3.eth.account.sign_transaction(txn, PRIVATE_KEY)

# Send and wait for receipt
tx_hash = blockchain_manager.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
tx_receipt = blockchain_manager.w3.eth.wait_for_transaction_receipt(tx_hash)

# Output
print("✅ Compliance record added.")
print("📦 Transaction hash:", tx_receipt.transactionHash.hex())
