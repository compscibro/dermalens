# 🚀 EC2 Deployment Guide - Step by Step

## Prerequisites

- AWS Account
- AWS CLI installed locally
- SSH key pair created in AWS

---

## 📋 Complete Deployment Steps

### Step 1: Create IAM Role (One-time Setup)

```bash
# 1. Create the IAM role
aws iam create-role \
  --role-name DermaLensAppRole \
  --assume-role-policy-document '{
    "Version": "2012-10-17",
    "Statement": [{
      "Effect": "Allow",
      "Principal": {"Service": "ec2.amazonaws.com"},
      "Action": "sts:AssumeRole"
    }]
  }'

# 2. Create and attach DynamoDB policy
cat > dermalens-dynamodb-policy.json << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:CreateTable",
        "dynamodb:DescribeTable",
        "dynamodb:GetItem",
        "dynamodb:PutItem",
        "dynamodb:UpdateItem",
        "dynamodb:DeleteItem",
        "dynamodb:Query",
        "dynamodb:Scan"
      ],
      "Resource": "arn:aws:dynamodb:*:*:table/dermalens-*"
    }
  ]
}
EOF

aws iam put-role-policy \
  --role-name DermaLensAppRole \
  --policy-name DermaLensDynamoDBPolicy \
  --policy-document file://dermalens-dynamodb-policy.json

# 3. Create and attach S3 policy
cat > dermalens-s3-policy.json << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:DeleteObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::dermalens-images",
        "arn:aws:s3:::dermalens-images/*"
      ]
    }
  ]
}
EOF

aws iam put-role-policy \
  --role-name DermaLensAppRole \
  --policy-name DermaLensS3Policy \
  --policy-document file://dermalens-s3-policy.json

# 4. Create instance profile
aws iam create-instance-profile \
  --instance-profile-name DermaLensAppProfile

# 5. Add role to instance profile
aws iam add-role-to-instance-profile \
  --instance-profile-name DermaLensAppProfile \
  --role-name DermaLensAppRole

echo "✅ IAM Role created successfully!"
```

---

### Step 2: Create S3 Bucket for Images

```bash
# Create S3 bucket (use a unique name)
aws s3 mb s3://dermalens-images-YOUR-UNIQUE-ID --region us-east-1

# Enable CORS for presigned URLs
cat > cors.json << 'EOF'
{
  "CORSRules": [
    {
      "AllowedOrigins": ["*"],
      "AllowedMethods": ["GET", "PUT", "POST", "DELETE"],
      "AllowedHeaders": ["*"],
      "ExposeHeaders": ["ETag"],
      "MaxAgeSeconds": 3000
    }
  ]
}
EOF

aws s3api put-bucket-cors \
  --bucket dermalens-images-YOUR-UNIQUE-ID \
  --cors-configuration file://cors.json

echo "✅ S3 bucket created and configured!"
```

---

### Step 3: Create Security Group

```bash
# Create security group
aws ec2 create-security-group \
  --group-name dermalens-sg \
  --description "Security group for DermaLens API"

# Allow SSH (port 22)
aws ec2 authorize-security-group-ingress \
  --group-name dermalens-sg \
  --protocol tcp \
  --port 22 \
  --cidr 0.0.0.0/0

# Allow HTTP (port 80)
aws ec2 authorize-security-group-ingress \
  --group-name dermalens-sg \
  --protocol tcp \
  --port 80 \
  --cidr 0.0.0.0/0

# Allow API port (port 8000)
aws ec2 authorize-security-group-ingress \
  --group-name dermalens-sg \
  --protocol tcp \
  --port 8000 \
  --cidr 0.0.0.0/0

echo "✅ Security group created!"
```

---

### Step 4: Launch EC2 Instance

```bash
# Find latest Ubuntu AMI ID for your region
# For us-east-1, Ubuntu 22.04:
AMI_ID="ami-0c7217cdde317cfec"

# Launch instance
aws ec2 run-instances \
  --image-id $AMI_ID \
  --instance-type t2.micro \
  --key-name YOUR-KEY-PAIR-NAME \
  --security-groups dermalens-sg \
  --iam-instance-profile Name=DermaLensAppProfile \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=DermaLens-API}]'

# Get instance public IP
aws ec2 describe-instances \
  --filters "Name=tag:Name,Values=DermaLens-API" \
  --query 'Reservations[0].Instances[0].PublicIpAddress' \
  --output text

echo "✅ EC2 instance launched!"
echo "Wait 2-3 minutes for instance to be ready, then continue..."
```

---

### Step 5: Deploy Application on EC2

```bash
# SSH into your EC2 instance
ssh -i YOUR-KEY.pem ubuntu@YOUR-EC2-PUBLIC-IP

# Once connected to EC2, run these commands:

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install -y python3-pip python3-venv git nginx

# Create app directory
mkdir -p ~/dermalens
cd ~/dermalens

# Upload your code (from your local machine)
# Option A: Use git
git clone YOUR-GITHUB-REPO .

# Option B: Use scp from your local machine
# scp -i YOUR-KEY.pem -r dermalens_backend_dynamodb/* ubuntu@YOUR-EC2-IP:~/dermalens/

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cat > .env << 'EOF'
PROJECT_NAME=DermaLens
VERSION=1.0.0
API_V1_PREFIX=/api/v1
DEBUG=False

SECRET_KEY=CHANGE-THIS-TO-A-RANDOM-32-CHAR-STRING
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080

ALLOWED_ORIGINS=["http://YOUR-DOMAIN.com","https://YOUR-DOMAIN.com"]

# NO AWS KEYS NEEDED - IAM ROLE PROVIDES THEM!
AWS_REGION=us-east-1

# DynamoDB Tables
DYNAMODB_USERS_TABLE=dermalens-users
DYNAMODB_SCANS_TABLE=dermalens-scans
DYNAMODB_PLANS_TABLE=dermalens-treatment-plans
DYNAMODB_CHAT_TABLE=dermalens-chat-messages

# S3 Bucket (use the one you created)
S3_BUCKET_NAME=dermalens-images-YOUR-UNIQUE-ID
S3_PRESIGNED_URL_EXPIRATION=3600

# Add your API keys
GEMINI_API_KEY=your-gemini-key-here
NANOBANANA_API_KEY=your-key-or-mock

MIN_TREATMENT_DAYS=14
MAX_TREATMENT_DAYS=28
SCORE_DECLINE_THRESHOLD=10.0
MIN_SCAN_INTERVAL_DAYS=7
MAX_IMAGE_SIZE_MB=10
EOF

# Edit the .env file with your actual values
nano .env

echo "✅ Application deployed!"
```

---

### Step 6: Create Systemd Service

```bash
# Create systemd service file
sudo nano /etc/systemd/system/dermalens.service
```

Paste this content:

```ini
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
```

Save and exit (Ctrl+X, Y, Enter)

```bash
# Reload systemd
sudo systemctl daemon-reload

# Start the service
sudo systemctl start dermalens

# Enable on boot
sudo systemctl enable dermalens

# Check status
sudo systemctl status dermalens

echo "✅ Service started!"
```

---

### Step 7: Configure Nginx (Optional - for production)

```bash
# Create nginx config
sudo nano /etc/nginx/sites-available/dermalens
```

Paste this:

```nginx
server {
    listen 80;
    server_name YOUR-DOMAIN.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/dermalens /etc/nginx/sites-enabled/

# Test nginx config
sudo nginx -t

# Restart nginx
sudo systemctl restart nginx

echo "✅ Nginx configured!"
```

---

### Step 8: Verify Everything Works

```bash
# Check if tables were created
aws dynamodb list-tables --region us-east-1

# Test API health
curl http://YOUR-EC2-PUBLIC-IP:8000/health

# Test registration
curl -X POST http://YOUR-EC2-PUBLIC-IP:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpass123",
    "full_name": "Test User"
  }'

echo "✅ Everything is working!"
```

---

## 🔍 Verify IAM Role is Working

```bash
# SSH into your EC2 instance
ssh -i YOUR-KEY.pem ubuntu@YOUR-EC2-IP

# Check if IAM role credentials are available
curl http://169.254.169.254/latest/meta-data/iam/security-credentials/

# Should show: DermaLensAppRole

# Get the credentials (you'll see temporary access keys)
curl http://169.254.169.254/latest/meta-data/iam/security-credentials/DermaLensAppRole

# Test DynamoDB access
aws dynamodb list-tables --region us-east-1

# Should show your dermalens-* tables
```

---

## 📊 Monitor Your Application

```bash
# View logs in real-time
sudo journalctl -u dermalens -f

# Check service status
sudo systemctl status dermalens

# Restart if needed
sudo systemctl restart dermalens
```

---

## 🐛 Troubleshooting

### Service won't start
```bash
# Check logs
sudo journalctl -u dermalens -n 50

# Check Python errors
cd ~/dermalens
source venv/bin/activate
python -m app.main
```

### DynamoDB permission issues
```bash
# Verify IAM role is attached
aws ec2 describe-instances \
  --instance-ids $(ec2-metadata --instance-id | cut -d " " -f 2) \
  --query 'Reservations[0].Instances[0].IamInstanceProfile'

# Check if tables exist
aws dynamodb list-tables
```

### Tables not auto-creating
```bash
# Manually create tables
cd ~/dermalens
source venv/bin/activate
python3 -c "from app.db.dynamodb import dynamodb_client; dynamodb_client.create_tables_if_not_exist()"
```

---

## 🔒 Security Checklist

- [ ] ✅ IAM role created with minimal permissions
- [ ] ✅ Security group restricts SSH to your IP only
- [ ] ✅ Changed SECRET_KEY in .env to random string
- [ ] ✅ DEBUG=False in production
- [ ] ✅ Using HTTPS (setup SSL with Let's Encrypt)
- [ ] ✅ Regular system updates scheduled

---

## 💰 Cost Estimate

**Monthly Cost (AWS Free Tier):**
- EC2 t2.micro: Free first year, then ~$8/month
- DynamoDB: Free tier (25GB + 200M requests)
- S3: Free tier (5GB)
- Data transfer: ~$1-2/month

**Total: $0/month first year, then ~$10-15/month**

---

## 🎉 You're Live!

Your API is now running at:
- **Health**: http://YOUR-EC2-IP:8000/health
- **Docs**: http://YOUR-EC2-IP:8000/api/v1/docs
- **API**: http://YOUR-EC2-IP:8000/api/v1/

**No access keys in your code!** IAM role handles everything! 🔐
