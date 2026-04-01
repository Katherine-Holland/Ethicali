import os
from dotenv import load_dotenv
from blockchain_manager import BlockchainManager

load_dotenv()

# Load required arguments from environment variables
contract_address = os.getenv("CONTRACT_ADDRESS")
abi_path = "backend/blockchain/abi/contract_abi.json"
provider_url = os.getenv("SEPOLIA_RPC_URL")

if not contract_address or not provider_url:
    raise ValueError("CONTRACT_ADDRESS and SEPOLIA_RPC_URL must be set in environment variables.")

# Create an instance of BlockchainManager
blockchain_manager = BlockchainManager(
    contract_address=contract_address,
    abi_path=abi_path,
    provider_url=provider_url
)

# Print info
print("Connected to contract at:", blockchain_manager.contract.address)
print("Default account is:", blockchain_manager.w3.eth.default_account)
