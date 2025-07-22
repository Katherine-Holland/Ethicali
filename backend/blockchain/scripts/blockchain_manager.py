from web3 import Web3
import json
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class BlockchainManager:
    def __init__(self, contract_address, abi_path, provider_url):
        self.contract_address = contract_address
        self.abi_path = abi_path
        self.provider_url = provider_url

                # Initialize Web3
        self.w3 = Web3(Web3.HTTPProvider(self.provider_url))
        if not self.w3.is_connected():
            raise ConnectionError("Unable to connect to the blockchain provider.")

        # Check environment variable for account address
        account_address = os.getenv("METAMASK_ACCOUNT_ADDRESS")
        if not account_address:
            raise ValueError("Environment variable METAMASK_ACCOUNT_ADDRESS is not set or is empty.")
        self.w3.eth.default_account = self.w3.to_checksum_address(account_address)

        # Load ABI
        try:
            with open(self.abi_path, "r") as abi_file:
                abi_content = json.load(abi_file)
                if isinstance(abi_content, dict) and "abi" in abi_content:
                    self.contract_abi = json.loads(abi_content["abi"]) if isinstance(abi_content["abi"], str) else abi_content["abi"]
                elif isinstance(abi_content, list):
                    self.contract_abi = abi_content
                else:
                    raise ValueError("ABI file does not contain valid 'abi' structure.")
        except FileNotFoundError:
            raise FileNotFoundError(f"ABI file not found at {self.abi_path}. Please check the path.")
        except json.JSONDecodeError as e:
            raise ValueError(f"Error decoding JSON ABI file: {e}")

        # Initialize Contract
        self.contract = self.w3.eth.contract(address=self.contract_address, abi=self.contract_abi)

    def upload_compliance_summary(self, summary, hash_value, metadata):
        """
        Upload a compliance summary, its hash, and metadata to the blockchain.
        """
        account = os.getenv("METAMASK_ACCOUNT_ADDRESS")
        private_key = os.getenv("PRIVATE_KEY")

        if not account or not private_key:
            raise ValueError("Account address or private key is not set in the environment variables.")

        account = self.w3.to_checksum_address(account)

        try:
            # Build the transaction
            txn = self.contract.functions.addComplianceRecord(summary, hash_value, metadata).build_transaction({
                'from': account,
                'nonce': self.w3.eth.get_transaction_count(account),
                'gas': 3000000,
                'gasPrice': self.w3.to_wei('20', 'gwei')
            })

            # Sign the transaction
            signed_txn = self.w3.eth.account.sign_transaction(txn, private_key=private_key)

            # Send the transaction
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.raw_transaction)

            # Wait for transaction receipt
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            return receipt.transactionHash.hex()
        except Exception as e:
            raise RuntimeError(f"Error uploading compliance summary: {e}")

    def fetch_compliance_summary(self, record_id):
        """
        Fetch a compliance summary from the blockchain.
        """
        try:
            record = self.contract.functions.getComplianceRecord(record_id).call()
            return {
                "id": record[0],
                "summary": record[1],
                "hash": record[2],
                "timestamp": record[3],
                "metadata": record[4]
            }
        except Exception as e:
            raise ValueError(f"Error fetching compliance summary: {e}")
    
    def fetch_event_logs(self, event_name):
        """
        Fetch event logs from the blockchain.
        """
        try:
            event_filter = self.contract.events[event_name].createFilter(fromBlock="latest")
            logs = event_filter.get_all_entries()
            return logs
        except Exception as e:
            raise RuntimeError(f"Error fetching event logs: {e}")

# Adjusted ABI path to reflect actual structure
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "blockchain", "abi"))
abi_path = os.path.join(base_dir, "contract_abi.json")

# Updated deployed contract address
blockchain_manager = BlockchainManager(
    provider_url="https://eth-sepolia.g.alchemy.com/v2/REDACTED_ALCHEMY_KEY_2",
    contract_address="0xE8D30d2031468a1B17e1BB06c142b06c9fd98f04",
    abi_path=abi_path
)
