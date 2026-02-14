#!/bin/bash

# DermaLens EC2 Quick Setup Script
# Run this on your EC2 instance after connecting via SSH

set -e

echo "🚀 Starting DermaLens EC2 Setup..."
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

# Update system
echo -e "${BLUE}📦 Updating system packages...${NC}"
sudo apt update && sudo apt upgrade -y

# Install dependencies
echo -e "${BLUE}📦 Installing Python and dependencies...${NC}"
sudo apt install -y python3-pip python3-venv git nginx

# Create app directory
echo -e "${BLUE}📁 Setting up application directory...${NC}"
mkdir -p ~/dermalens
cd ~/dermalens

# Check if code already exists
if [ ! -f "requirements.txt" ]; then
    echo -e "${BLUE}📥 Please upload your code now${NC}"
    echo "Options:"
    echo "  1. Git: git clone YOUR-REPO ."
    echo "  2. SCP: scp -r local-folder/* ubuntu@this-server:~/dermalens/"
    echo ""
    read -p "Press Enter after uploading code..."
fi

# Create virtual environment
echo -e "${BLUE}🐍 Creating Python virtual environment...${NC}"
python3 -m venv venv
source venv/bin/activate

# Install requirements
echo -e "${BLUE}📦 Installing Python packages...${NC}"
pip install -r requirements.txt

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo -e "${BLUE}⚙️  Creating .env file...${NC}"
    cp .env.example .env
    
    echo ""
    echo -e "${GREEN}✅ .env file created${NC}"
    echo -e "${BLUE}⚠️  IMPORTANT: Edit .env file with your settings:${NC}"
    echo "  - SECRET_KEY (generate random 32+ char string)"
    echo "  - S3_BUCKET_NAME (your bucket name)"
    echo "  - GEMINI_API_KEY (your API key)"
    echo "  - ALLOWED_ORIGINS (your frontend URL)"
    echo ""
    read -p "Press Enter to edit .env now..."
    nano .env
fi

# Verify IAM role
echo -e "${BLUE}🔐 Verifying IAM role...${NC}"
ROLE_NAME=$(curl -s http://169.254.169.254/latest/meta-data/iam/security-credentials/)
if [ -z "$ROLE_NAME" ]; then
    echo -e "${GREEN}⚠️  WARNING: No IAM role detected!${NC}"
    echo "Make sure your EC2 instance has the DermaLensAppRole attached"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo -e "${GREEN}✅ IAM role found: $ROLE_NAME${NC}"
fi

# Test DynamoDB access
echo -e "${BLUE}🗄️  Testing DynamoDB access...${NC}"
if aws dynamodb list-tables --region us-east-1 > /dev/null 2>&1; then
    echo -e "${GREEN}✅ DynamoDB access confirmed${NC}"
else
    echo -e "${GREEN}⚠️  Could not access DynamoDB${NC}"
    echo "Make sure IAM role has DynamoDB permissions"
fi

# Create systemd service
echo -e "${BLUE}🔧 Creating systemd service...${NC}"
sudo tee /etc/systemd/system/dermalens.service > /dev/null << EOF
[Unit]
Description=DermaLens API
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/dermalens
Environment="PATH=/home/ubuntu/dermalens/venv/bin"
ExecStart=/home/ubuntu/dermalens/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd
sudo systemctl daemon-reload

# Start service
echo -e "${BLUE}🚀 Starting DermaLens service...${NC}"
sudo systemctl start dermalens
sudo systemctl enable dermalens

# Wait a moment for service to start
sleep 3

# Check status
if sudo systemctl is-active --quiet dermalens; then
    echo -e "${GREEN}✅ Service is running!${NC}"
else
    echo -e "${GREEN}❌ Service failed to start${NC}"
    echo "Check logs: sudo journalctl -u dermalens -n 50"
    exit 1
fi

# Get public IP
PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)

# Test API
echo -e "${BLUE}🧪 Testing API...${NC}"
sleep 2
if curl -s http://localhost:8000/health > /dev/null; then
    echo -e "${GREEN}✅ API is responding!${NC}"
else
    echo -e "${GREEN}⚠️  API not responding yet${NC}"
    echo "Check logs: sudo journalctl -u dermalens -f"
fi

# Final summary
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}🎉 Setup Complete!${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Your API is running at:"
echo -e "  ${BLUE}Health:${NC} http://$PUBLIC_IP:8000/health"
echo -e "  ${BLUE}Docs:${NC}   http://$PUBLIC_IP:8000/api/v1/docs"
echo -e "  ${BLUE}API:${NC}    http://$PUBLIC_IP:8000/api/v1/"
echo ""
echo "Useful commands:"
echo -e "  ${BLUE}View logs:${NC}      sudo journalctl -u dermalens -f"
echo -e "  ${BLUE}Restart:${NC}        sudo systemctl restart dermalens"
echo -e "  ${BLUE}Stop:${NC}           sudo systemctl stop dermalens"
echo -e "  ${BLUE}Service status:${NC} sudo systemctl status dermalens"
echo ""
echo -e "${GREEN}✅ No AWS access keys needed - IAM role is handling authentication!${NC}"
echo ""
