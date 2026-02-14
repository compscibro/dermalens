# 🚀 DermaLens Backend - DynamoDB + IAM Role Version

## 🎯 What's Different

This version uses:
- ✅ **DynamoDB** instead of PostgreSQL (NoSQL, serverless)
- ✅ **IAM Roles** instead of access keys (more secure!)
- ✅ **No RDS** needed (cost savings!)
- ✅ Perfect for single-user-per-account architecture

## 🔑 IAM Role Benefits

**No Access Keys = More Secure!**
- When running on AWS (EC2/ECS/Lambda), IAM role provides credentials automatically
- No need to manage or rotate access keys
- No risk of leaked credentials
- AWS best practice for security

## 📊 Database Structure

### DynamoDB Tables

**1. dermalens-users**
- Partition Key: `user_id` (String)
- GSI: `email-index` on `email`
- Stores: User accounts and profiles

**2. dermalens-scans**
- Partition Key: `user_id` (String)
- Sort Key: `scan_id` (String)
- LSI: `scan-date-index` on `scan_date`
- Stores: All facial scans for each user

**3. dermalens-treatment-plans**
- Partition Key: `user_id` (String)
- Sort Key: `plan_id` (String)
- Stores: Treatment plans per user

**4. dermalens-chat-messages**
- Partition Key: `user_id` (String)
- Sort Key: `message_id` (String)
- LSI: `session-index` on `session_id`
- Stores: Chat history per user

### Why This Design Works

**Single-User Access Pattern:**
- Each user ONLY accesses their own data
- Partition key = `user_id` ensures data isolation
- Perfect for multi-tenant SaaS where users can't see each other's data
- DynamoDB's pricing and performance scale automatically

## ⚡ Quick Start - Local Testing

### Option 1: Use DynamoDB Local (Docker)

```bash
# 1. Install dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Start DynamoDB Local
docker run -d -p 8000:8000 amazon/dynamodb-local

# 3. Configure for local DynamoDB
cp .env.example .env
# Add this line to .env:
AWS_DYNAMODB_ENDPOINT=http://localhost:8000

# 4. Start server
uvicorn app.main:app --reload
```

The server will automatically create all tables on startup!

### Option 2: Use Real AWS DynamoDB (Free Tier)

```bash
# 1. Install dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Configure AWS credentials (temporary for local dev)
aws configure
# Enter your AWS Access Key ID
# Enter your AWS Secret Access Key
# Enter region: us-east-1

# 3. Configure environment
cp .env.example .env
# Edit .env and set your table names

# 4. Start server
uvicorn app.main:app --reload
```

Tables will be created automatically in AWS!

## 🚀 Production Deployment on AWS

### Step 1: Create IAM Role

```bash
# Create IAM role with DynamoDB permissions
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

# Attach DynamoDB full access policy
aws iam attach-role-policy \
  --role-name DermaLensAppRole \
  --policy-arn arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess

# Attach S3 full access policy
aws iam attach-role-policy \
  --role-name DermaLensAppRole \
  --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess

# Create instance profile
aws iam create-instance-profile \
  --instance-profile-name DermaLensAppProfile

# Add role to instance profile
aws iam add-role-to-instance-profile \
  --instance-profile-name DermaLensAppProfile \
  --role-name DermaLensAppRole
```

### Step 2: Launch EC2 with IAM Role

```bash
# Launch EC2 instance with the IAM role
aws ec2 run-instances \
  --image-id ami-0c55b159cbfafe1f0 \  # Ubuntu 20.04
  --instance-type t2.micro \
  --iam-instance-profile Name=DermaLensAppProfile \
  --key-name your-key-pair \
  --security-groups your-security-group
```

### Step 3: Deploy Application on EC2

```bash
# SSH into EC2
ssh -i your-key.pem ubuntu@your-ec2-ip

# Install dependencies
sudo apt update
sudo apt install -y python3-pip python3-venv

# Clone your repo
git clone your-repo-url
cd dermalens_backend_dynamodb

# Setup Python environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
nano .env
# Set your table names and other configs
# NO AWS KEYS NEEDED - IAM role provides them!

# Start with systemd (production)
sudo nano /etc/systemd/system/dermalens.service
```

**dermalens.service:**
```ini
[Unit]
Description=DermaLens API
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/dermalens_backend_dynamodb
Environment="PATH=/home/ubuntu/dermalens_backend_dynamodb/venv/bin"
ExecStart=/home/ubuntu/dermalens_backend_dynamodb/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Start service
sudo systemctl daemon-reload
sudo systemctl start dermalens
sudo systemctl enable dermalens
sudo systemctl status dermalens
```

## 🐳 Docker Deployment (with IAM Role)

### Dockerfile
Already included in the project!

### Deploy to ECS (Fargate)

```bash
# 1. Build and push Docker image
aws ecr create-repository --repository-name dermalens-api
docker build -t dermalens-api .
docker tag dermalens-api:latest YOUR_AWS_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/dermalens-api:latest
docker push YOUR_AWS_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/dermalens-api:latest

# 2. Create ECS task definition with IAM role
# The task role will automatically have DynamoDB and S3 access!
```

**Task Definition (JSON):**
```json
{
  "family": "dermalens-task",
  "taskRoleArn": "arn:aws:iam::YOUR_ACCOUNT:role/DermaLensAppRole",
  "containerDefinitions": [{
    "name": "dermalens-api",
    "image": "YOUR_ECR_IMAGE_URL",
    "portMappings": [{"containerPort": 8000}],
    "environment": [
      {"name": "AWS_REGION", "value": "us-east-1"},
      {"name": "DYNAMODB_USERS_TABLE", "value": "dermalens-users"}
    ]
  }]
}
```

## 🧪 Testing the API

### 1. Check Health
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "DermaLens",
  "version": "1.0.0",
  "database": "DynamoDB",
  "auth": "IAM Role"
}
```

### 2. Test User Registration
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpass123",
    "full_name": "Test User"
  }'
```

### 3. View DynamoDB Tables (Local)

```bash
# List tables
aws dynamodb list-tables --endpoint-url http://localhost:8000

# Scan users table
aws dynamodb scan \
  --table-name dermalens-users \
  --endpoint-url http://localhost:8000
```

## 📋 Environment Variables

```env
# NO AWS ACCESS KEYS NEEDED!
# IAM role provides credentials automatically

AWS_REGION=us-east-1

# Table names
DYNAMODB_USERS_TABLE=dermalens-users
DYNAMODB_SCANS_TABLE=dermalens-scans
DYNAMODB_PLANS_TABLE=dermalens-treatment-plans
DYNAMODB_CHAT_TABLE=dermalens-chat-messages

# S3 bucket (also uses IAM role)
S3_BUCKET_NAME=dermalens-images

# Other configs
SECRET_KEY=your-secret-key
GEMINI_API_KEY=your-gemini-key
```

## 💰 Cost Comparison

### PostgreSQL RDS (Previous):
- **Minimum**: ~$15/month (db.t3.micro)
- **Always running** even with no traffic
- Manual scaling needed

### DynamoDB (Current):
- **Free tier**: 25 GB storage, 200M requests/month
- **Pay per use**: Only pay for what you use
- **Auto-scaling**: Handles traffic spikes automatically
- **Typical cost**: $0-5/month for small apps

## 🔒 Security Best Practices

### IAM Role Permissions

Create a minimal IAM policy:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:GetItem",
        "dynamodb:PutItem",
        "dynamodb:UpdateItem",
        "dynamodb:Query",
        "dynamodb:Scan",
        "dynamodb:DeleteItem"
      ],
      "Resource": [
        "arn:aws:dynamodb:us-east-1:*:table/dermalens-*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:DeleteObject"
      ],
      "Resource": [
        "arn:aws:s3:::dermalens-images/*"
      ]
    }
  ]
}
```

## 🐛 Troubleshooting

### Local DynamoDB Connection Issues
```bash
# Check if DynamoDB Local is running
docker ps | grep dynamodb

# Restart DynamoDB Local
docker restart dynamodb-local

# Verify endpoint in .env
AWS_DYNAMODB_ENDPOINT=http://localhost:8000
```

### IAM Role Issues on EC2
```bash
# Verify IAM role is attached
aws ec2 describe-instances --instance-ids i-xxxxx

# Check if credentials are available
curl http://169.254.169.254/latest/meta-data/iam/security-credentials/

# Test boto3 credentials
python3 -c "import boto3; print(boto3.Session().get_credentials())"
```

### Table Creation Errors
```bash
# Manually create tables if auto-creation fails
python3 -c "
from app.db.dynamodb import dynamodb_client
dynamodb_client.create_tables_if_not_exist()
"
```

## 📚 Key Differences from PostgreSQL Version

| Feature | PostgreSQL | DynamoDB |
|---------|-----------|----------|
| **Authentication** | Access Keys | IAM Role |
| **Database** | RDS (managed) | DynamoDB (serverless) |
| **Migrations** | Alembic | Auto-create tables |
| **Queries** | SQL | NoSQL (Key-Value) |
| **Scaling** | Manual | Automatic |
| **Cost** | Fixed monthly | Pay per use |
| **Relations** | Foreign keys | Denormalized |
| **Local Testing** | PostgreSQL Docker | DynamoDB Local |

## 🎯 When to Use This Version

**Use DynamoDB version if:**
- ✅ Each user only accesses their own data
- ✅ You want automatic scaling
- ✅ You want to minimize costs
- ✅ You're deploying on AWS
- ✅ You want simpler infrastructure

**Use PostgreSQL version if:**
- ❌ Need complex joins across users
- ❌ Need transactions across tables
- ❌ Prefer SQL
- ❌ Want easier local development
- ❌ Not on AWS

## 🚀 Next Steps

1. ✅ Test locally with DynamoDB Local
2. ✅ Create IAM role in AWS
3. ✅ Deploy to EC2/ECS with IAM role
4. ✅ Configure S3 bucket
5. ✅ Set up API keys (Gemini, etc.)
6. ✅ Test all endpoints
7. ✅ Monitor with CloudWatch

---

**No access keys, no RDS, no worries!** 🎉

The backend automatically uses IAM roles for secure, keyless authentication!
