from blockchain_manager import BlockchainManager

# Define the required arguments
contract_address = "0xC62d657394C521Fc5735a6C4cA8daBb7d5369c0b"
abi_path = "backend/blockchain/abi/contract_abi.json"
provider_url = "https://eth-sepolia.g.alchemy.com/v2/REDACTED_ALCHEMY_KEY_1"  # Or use your .env loader if you prefer

# Create an instance of BlockchainManager
blockchain_manager = BlockchainManager(
    contract_address=contract_address,
    abi_path=abi_path,
    provider_url=provider_url
)

# Print info
print("✅ Connected to contract at:", blockchain_manager.contract.address)
print("👤 Default account is:", blockchain_manager.w3.eth.default_account)
