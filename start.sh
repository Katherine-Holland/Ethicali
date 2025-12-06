#!/bin/bash
# Startup script for Render deployment

# Create temp directory for uploads
mkdir -p temp

# Start Streamlit
streamlit run frontend/app.py \
  --server.port=${PORT:-8501} \
  --server.address=0.0.0.0 \
  --server.headless=true \
  --server.enableXsrfProtection=true
