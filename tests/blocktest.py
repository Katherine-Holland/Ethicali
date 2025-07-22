from backend.blockchain.blockchain_manager import blockchain_manager

print("Connected to contract at:", blockchain_manager.contract.address)
print("Default account is:", blockchain_manager.w3.eth.default_account)
