# Ethicali AI Assurance Platform

This repository contains the full codebase for the Ethicali AI assurance platform. The system enables compliance validation of datasets and algorithms against leading AI governance frameworks including:

- EU AI Act
- ISO 42001
- NIST AI RMF
- California, Texas, and New York AI requirements

## Repository Structure

```
ethicalinew/
├── app/                      # Streamlit UI
├── backend/
│   ├── blockchain/
│   │   ├── abi/              # Compiled ABI and metadata
│   │   ├── contracts/        # Solidity smart contracts
│   │   ├── scripts/          # Hardhat deployment scripts
│   └── validator/            # Compliance logic (bias, transparency, etc.)
├── frontend/                 # Web frontend (future)
├── config/                   # Internal configuration files
├── integrations/             # Placeholder for APIs (e.g., Slack, Chrome)
├── tests/                    # Python + smart contract tests
├── .env                      # Local dev secrets (excluded from git)
├── hardhat.config.js
└── requirements.txt
```

## Prerequisites

Make sure you have the following installed:

- Node.js (v16+)
- Python 3.9+
- MetaMask wallet (Sepolia testnet funded)
- [Alchemy](https://www.alchemy.com/) Sepolia RPC endpoint
- Gitpod or VS Code (recommended for environment)

## Environment Variables

Create a `.env` file in the root directory:

```env
PRIVATE_KEY=your_metamask_private_key (without 0x)
METAMASK_ACCOUNT_ADDRESS=your_wallet_address (starting with 0x)
SEPOLIA_RPC_URL=https://eth-sepolia.g.alchemy.com/v2/YOUR_API_KEY
```

## Installation

Install all required dependencies:

```bash
npm install
pip install -r requirements.txt
```

## Smart Contract Deployment

Compile and deploy the `EthicalAI` contract to the Sepolia testnet:

```bash
npx hardhat compile
npx hardhat run backend/blockchain/scripts/deploy.js --network sepolia
```

The deployment script outputs:
- Contract address
- ABI saved to `backend/blockchain/abi/contract_abi.json`

Ensure the ABI path matches the expected structure in your blockchain integration script.

## Streamlit Application

To launch the interface:

```bash
streamlit run app/app.py
```

Tabs include:
- Upload Dataset
- Upload Algorithm
- Combined Analysis
- Fetch Blockchain Results
- Generate Compliance Report

## Blockchain Integration

Smart contract interactions are managed via the `BlockchainManager` class, located in the backend. The class allows:

- Uploading a compliance summary and hash
- Fetching a compliance record by ID
- Pulling event logs from the blockchain

Ensure the correct contract address and ABI path are configured in `BlockchainManager`.

## Deployment Targets

| Component       | Network     | Status         |
|----------------|-------------|----------------|
| Smart Contract | Sepolia     | ✅ Connected    |
| Streamlit App  | Localhost   | ✅ Operational  |
| Frontend (Web) | TBA         | 🚧 In Progress |

## Internal Notes

- All `.env` values are excluded via `.gitignore`.
- Default contract output location: `backend/blockchain/abi/contract_abi.json`
- Future frameworks (NIST, state laws) will be implemented as modular validators.
- Always verify ABI structure after contract changes.

## Next Steps

- Rebuild Streamlit tabs (if reset)
- Add PDF export and full framework mapping
- Integrate Slack + Chrome API hooks
- Expand compliance frameworks (USA state + global)

## Contact

For internal use.