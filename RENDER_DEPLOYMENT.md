# Deploying Ethicali to Render

This guide walks through deploying the Ethicali AI Validator Streamlit app to Render.

## Prerequisites

- GitHub account with this repository
- Render account (free tier available at [render.com](https://render.com))
- Environment variables ready (see below)

## Deployment Steps

### Option 1: Deploy via render.yaml (Recommended)

1. **Push code to GitHub**
   ```bash
   git add .
   git commit -m "Add Render deployment configuration"
   git push origin main
   ```

2. **Connect to Render**
   - Go to [render.com](https://render.com) and sign in
   - Click "New +" → "Blueprint"
   - Connect your GitHub repository
   - Render will automatically detect `render.yaml`

3. **Configure Environment Variables**
   In the Render dashboard, add these secret environment variables:
   - `PRIVATE_KEY` - Your MetaMask private key (without 0x prefix)
   - `METAMASK_ACCOUNT_ADDRESS` - Your wallet address (with 0x prefix)
   - `SEPOLIA_RPC_URL` - Your Alchemy Sepolia RPC endpoint
   - `AWS_ACCESS_KEY_ID` - (Optional) For DynamoDB audit logs
   - `AWS_SECRET_ACCESS_KEY` - (Optional) For DynamoDB audit logs

4. **Deploy**
   - Click "Apply" to start deployment
   - Wait 5-10 minutes for build to complete
   - Your app will be live at `https://ethicali-streamlit.onrender.com`

### Option 2: Manual Web Service Setup

1. **Create New Web Service**
   - Go to Render Dashboard
   - Click "New +" → "Web Service"
   - Connect your GitHub repository

2. **Configure Service**
   - **Name**: `ethicali-streamlit`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `./start.sh` or `streamlit run frontend/app.py --server.port=$PORT --server.address=0.0.0.0 --server.headless=true`
   - **Plan**: Free (or paid for better performance)

3. **Add Environment Variables** (same as Option 1)

4. **Deploy**
   - Click "Create Web Service"
   - Monitor build logs for any errors

## Environment Variables Reference

| Variable | Required | Description |
|----------|----------|-------------|
| `PRIVATE_KEY` | Yes | MetaMask private key for blockchain transactions |
| `METAMASK_ACCOUNT_ADDRESS` | Yes | Your Ethereum wallet address |
| `SEPOLIA_RPC_URL` | Yes | Alchemy or Infura Sepolia testnet RPC URL |
| `ETHICALI_DDB_TABLE` | No | DynamoDB table name (default: EthicaliAuditLogs) |
| `AWS_REGION` | No | AWS region (default: us-east-1) |
| `AWS_ACCESS_KEY_ID` | No | For DynamoDB access |
| `AWS_SECRET_ACCESS_KEY` | No | For DynamoDB access |

## Post-Deployment

### Verify Deployment
1. Visit your Render URL
2. Test file upload functionality
3. Verify blockchain connection (check logs)

### Monitor Logs
```bash
# View logs in Render dashboard or via CLI
render logs -s ethicali-streamlit
```

### Update Deployment
Render auto-deploys on every push to your main branch. To disable:
- Go to Settings → Build & Deploy
- Toggle "Auto-Deploy" off

## Troubleshooting

### Build Fails
- Check `requirements.txt` for incompatible versions
- Verify Python version (3.12.3 recommended)
- Review build logs in Render dashboard

### App Crashes on Startup
- Verify all required environment variables are set
- Check that `temp/` directory creation works
- Review application logs

### Blockchain Connection Issues
- Verify `SEPOLIA_RPC_URL` is correct
- Check Alchemy/Infura API key limits
- Ensure wallet has Sepolia ETH for gas

### File Upload Errors
- Render free tier has limited disk space
- Consider using S3 for file storage in production
- Check file size limits

## Performance Optimization

### Free Tier Limitations
- Service spins down after 15 minutes of inactivity
- First request after spin-down takes 30-60 seconds
- 512 MB RAM limit

### Upgrade to Paid Plan
For production use, consider:
- **Starter Plan** ($7/month): Always-on, 512 MB RAM
- **Standard Plan** ($25/month): 2 GB RAM, better performance
- **Pro Plan** ($85/month): 4 GB RAM, priority support

## Security Notes

- Never commit `.env` files or secrets to Git
- Use Render's environment variable encryption
- Rotate API keys and private keys regularly
- Enable HTTPS (automatic on Render)
- Consider IP whitelisting for sensitive operations

## Next Steps

- Set up custom domain (Render supports this)
- Configure AWS services (DynamoDB, S3, Lambda)
- Add monitoring and alerting
- Implement rate limiting
- Set up CI/CD pipeline

## Support

- Render Docs: [render.com/docs](https://render.com/docs)
- Streamlit Docs: [docs.streamlit.io](https://docs.streamlit.io)
- Project Issues: [GitHub Issues](https://github.com/Katherine-Holland/Ethicali/issues)
