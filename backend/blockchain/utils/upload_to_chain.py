from blockchain_manager import BlockchainManager
from web3 import Web3
from eth_account import Account
from dotenv import load_dotenv
import os

load_dotenv()

# Environment
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
ACCOUNT_ADDRESS = os.getenv("METAMASK_ACCOUNT_ADDRESS")
PROVIDER_URL = os.getenv("PROVIDER_URL") or "https://eth-sepolia.g.alchemy.com/v2/YOUR-KEY"
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS") or "0xYourDeployedContractAddress"
ABI_PATH = "backend/blockchain/abi/contract_abi.json"

# Init manager
blockchain_manager = BlockchainManager(CONTRACT_ADDRESS, ABI_PATH, PROVIDER_URL)

def upload_compliance_result(framework, overall_status, hash_value, metadata):
    """
    Uploads a compliance result to the blockchain using the selected framework and result.
    """
    if not PRIVATE_KEY:
        raise ValueError("❌ PRIVATE_KEY is not set in environment.")
    
    if not ACCOUNT_ADDRESS:
        raise ValueError("❌ METAMASK_ACCOUNT_ADDRESS is not set in environment.")

    # 🔧 Dynamic summary
    summary = f"{overall_status} compliance check under {framework}"

    account = Account.from_key(PRIVATE_KEY)
    nonce = blockchain_manager.w3.eth.get_transaction_count(account.address)

    txn = blockchain_manager.contract.functions.addComplianceRecord(
        summary,
        hash_value,
        metadata
    ).build_transaction({
        'from': account.address,
        'nonce': nonce,
        'gas': 2000000,
        'gasPrice': blockchain_manager.w3.eth.gas_price
    })

    signed_txn = blockchain_manager.w3.eth.account.sign_transaction(txn, PRIVATE_KEY)

    # ⛓️ Push to chain
    tx_hash = blockchain_manager.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    receipt = blockchain_manager.w3.eth.wait_for_transaction_receipt(tx_hash)

    print("✅ Compliance record uploaded.")
    print("🔗 Tx Hash:", receipt.transactionHash.hex())
    print("🧾 Summary:", summary)
    print("🔒 Metadata:", metadata)

    return receipt.transactionHash.hex()  # ✅ Return the tx hash!
