# Ethicali — AI Compliance Assurance Platform

Ethicali is a full-stack AI governance platform that automatically audits datasets and algorithms against major regulatory frameworks, then writes tamper-proof compliance records to the Ethereum blockchain.

Built as a response to the growing regulatory pressure on AI systems — EU AI Act enforcement, ISO 42001 certification, and US state-level AI laws — Ethicali gives organisations a verifiable, auditable trail of compliance decisions.

---

## What It Does

Upload a dataset or algorithm and Ethicali runs it through a multi-node validation pipeline covering:

| Framework | Coverage |
|---|---|
| **EU AI Act** | Bias, fairness, transparency, explainability, robustness, risk classification, accountability, human oversight |
| **ISO 42001** | AI management system requirements |
| **NIST AI RMF** | Govern, Map, Measure, Manage functions |
| **US State Laws** | California, Texas, and New York AI requirements |

Each validation run produces a structured compliance report. The report summary and a cryptographic hash of the full document are then written to a Solidity smart contract on the Ethereum Sepolia testnet — creating an immutable, timestamped record that cannot be altered after the fact.

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                  Streamlit UI                        │
│  Upload → Validate → Report → Blockchain Record     │
└────────────────────┬────────────────────────────────┘
                     │
        ┌────────────▼────────────┐
        │   Validation Pipeline   │
        │  (multi-node per frame- │
        │   work, AWS Lambda)     │
        └────────────┬────────────┘
                     │
        ┌────────────▼────────────┐
        │   EthicalAI.sol         │
        │   Solidity smart        │
        │   contract (Sepolia)    │
        └─────────────────────────┘
```

**Stack:**
- **Frontend:** Streamlit (Python)
- **Validation engine:** Python, modular per-framework node architecture
- **Cloud:** AWS Lambda + DynamoDB + S3 (Terraform-provisioned)
- **Blockchain:** Solidity smart contract, Hardhat, Web3.py, Ethereum Sepolia testnet
- **Audit logging:** Structured JSON audit trail with agent drift detection
- **IaC:** Terraform

---

## Key Technical Features

**Modular validator architecture** — Each compliance framework is broken into independent validation nodes (e.g. `eu_bias_node.py`, `eu_transparency_node.py`). Adding a new framework or updating a rule set requires no changes to the core pipeline.

**On-chain compliance records** — The `EthicalAI` Solidity contract stores a summary, SHA hash, timestamp, and metadata for every compliance run. Records are append-only and owner-gated, providing a verifiable audit trail.

**Agent drift detection** — The audit logging layer tracks behavioural drift in AI agent outputs over time, flagging deviations from baseline compliance scores.

**Serverless deployment** — Validation runs execute as AWS Lambda functions, with results persisted to DynamoDB and S3. Infrastructure is fully defined in Terraform.

---

## Repository Structure

```
Ethicali/
├── app/                          # Streamlit UI
├── backend/
│   ├── blockchain/
│   │   ├── contracts/            # EthicalAI.sol smart contract
│   │   ├── scripts/              # Deployment and interaction scripts
│   │   └── abi/                  # Compiled ABI
│   ├── validator/
│   │   ├── eu_ai_act/            # 9 validation nodes
│   │   ├── iso_42001/
│   │   ├── nist_rmf/
│   │   ├── california/
│   │   ├── texas/
│   │   └── new_york/
│   ├── lambda/                   # AWS Lambda handlers + audit logging
│   └── terraform/                # Infrastructure as code
├── config/
├── integrations/
├── tests/
├── hardhat.config.js
└── requirements.txt
```

---

## Getting Started

### Prerequisites

- Node.js v16+
- Python 3.9+
- MetaMask wallet (Sepolia testnet)
- [Alchemy](https://www.alchemy.com/) Sepolia RPC endpoint

### Environment Variables

Create a `.env` file in the root:

```env
PRIVATE_KEY=your_wallet_private_key_without_0x
METAMASK_ACCOUNT_ADDRESS=0x_your_wallet_address
SEPOLIA_RPC_URL=https://eth-sepolia.g.alchemy.com/v2/YOUR_API_KEY
CONTRACT_ADDRESS=0x_your_deployed_contract_address
```

### Install Dependencies

```bash
npm install
pip install -r requirements.txt
```

### Deploy the Smart Contract

```bash
npx hardhat compile
npx hardhat run backend/blockchain/scripts/deploy.js --network sepolia
```

### Run the Application

```bash
streamlit run app/app.py
```

---

## Smart Contract

The `EthicalAI` contract (Solidity ^0.8.0) exposes three functions:

```solidity
addComplianceRecord(string summary, string hash, string metadata)
getComplianceRecord(uint recordId)
getTotalRecords()
```

Records are owner-gated and emit a `ComplianceRecordAdded` event on every write, making them indexable by any blockchain explorer or subgraph.

---

## Roadmap

- PDF compliance report export
- Full NIST AI RMF and ISO 42001 node coverage
- Slack and browser extension integrations
- Expanded US state law coverage
- Mainnet deployment option

---

## Contact

[Katherine Holland](https://github.com/Katherine-Holland)
