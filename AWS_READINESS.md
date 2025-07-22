# ✅ AWS Readiness Checklist for Ethicali

## 1. 🔧 Modular Code Architecture (already in progress)
- [x] Separate validation logic from Streamlit UI.
- [x] Use class-based backends (`BlockchainManager`, `ValidatorEngine`).
- [ ] Annotate backend modules with `# Ready for Lambda`.

## 2. 📁 Folder Structure Prep
Create (or confirm) the following structure to reflect where things will map in AWS:

```
backend/
│
├── validation/              # Node logic (→ Lambda functions)
│   ├── bias_check.py
│   ├── transparency.py
│
├── blockchain/              # Smart contract deploy/read/write
│   ├── scripts/
│   ├── abi/
│
├── api/                     # API gateway endpoints (later)
│   └── __init__.py
│
├── storage/                 # Future S3 integration
│   └── upload_manager.py
```

## 3. 🔐 .env Variables (for AWS parameter store)
Prepare your `.env` keys as if they’ll be stored in **AWS Systems Manager Parameter Store**:

```bash
PRIVATE_KEY=
METAMASK_ACCOUNT_ADDRESS=
SEPOLIA_RPC_URL=
ALCHEMY_API_KEY=
SLACK_WEBHOOK_URL=
```

Later we’ll move these to AWS SSM securely.

## 4. 🔔 External Integration Hooks
Flag integrations that will eventually move to AWS services:
- Slack alerts → `SNS + Lambda`
- Chrome extension ping → `API Gateway`
- Report generation → `Lambda → S3`

> ✅ Start by wrapping these with small Python functions, so they're easy to port.

## 5. 🧪 Local AWS Emulation (Optional for Dev)
If you're curious:
- `localstack` can emulate S3, Lambda, etc. locally
- But **this is optional for now**, especially with Gitpod

---

## 🧠 Long-Term Vision Diagram (Simplified)

```
[User Upload] → [Streamlit UI] → [Validator Functions]
                                → [Blockchain Log]
                                → [Slack Notify / Chrome Widget]

(Migrates later to)

[User Upload] → [API Gateway]
                                → [Lambda Validator Functions]
                                → [S3 Storage + DynamoDB]
                                → [Blockchain]
                                → [SNS → Slack/Email Alerts]
```
