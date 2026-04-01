from web3 import Web3
import json
import os
from dotenv import load_dotenv

load_dotenv()

class BlockchainManager:
    def __init__(self, contract_address, abi_path, provider_url):
        # Initialize Web3 connection
        self.web3 = Web3(Web3.HTTPProvider(provider_url))
        print(f"Connected to blockchain: {self.web3.isConnected()}")  # Debug statement to check connection
        if not self.web3.isConnected():
            raise Exception("Unable to connect to blockchain.")
        
        # Set contract address and ABI
        self.contract_address = Web3.toChecksumAddress(contract_address)
        try:
            with open(abi_path, 'r') as file:
                self.abi = json.load(file)
        except json.JSONDecodeError as e:
            raise ValueError(f"Error decoding ABI file: {e}")
        except FileNotFoundError:
            raise FileNotFoundError(f"ABI file not found at path: {abi_path}")
        
        # Initialize contract
        self.contract = self.web3.eth.contract(address=self.contract_address, abi=self.abi)
    
    def add_compliance_record(self, key, result, description):
        """
        Add a compliance record to the blockchain.
        """
        account = self.web3.eth.accounts[0]  # Replace this with your account management logic
        txn = self.contract.functions.addComplianceRecord(key, result, description).buildTransaction({
            'from': account,
            'nonce': self.web3.eth.getTransactionCount(account),
            'gas': 3000000,
            'gasPrice': self.web3.toWei('20', 'gwei')
        })
        private_key = os.getenv("PRIVATE_KEY")
        if not private_key:
            raise ValueError("PRIVATE_KEY environment variable is not set.")
        signed_txn = self.web3.eth.account.signTransaction(txn, private_key=private_key)
        tx_hash = self.web3.eth.sendRawTransaction(signed_txn.rawTransaction)
        return self.web3.toHex(tx_hash)
    
    def get_compliance_record(self, key):
        """
        Retrieve a compliance record from the blockchain.
        """
        return self.contract.functions.getComplianceRecord(key).call()