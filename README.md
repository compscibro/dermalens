# 🚀 DermaLens Backend - DynamoDB Edition

## ✨ Key Features

- ✅ **DynamoDB** instead of PostgreSQL (NoSQL, serverless, pay-per-use)
- ✅ **IAM Roles** instead of access keys (AWS security best practice!)
- ✅ **No RDS** needed (saves ~$15/month minimum)
- ✅ **Auto-scaling** (handles traffic spikes automatically)
- ✅ **Free tier** available (25GB + 200M requests/month)
- ✅ **Perfect for single-user-per-account** architecture

## 🎯 Why This Version?

### You said:
> "I do not want an RDS database, rework the whole backend to be in DynamoDB, since the user is only going to have their own account to access I also plan to use an IAM role on AWS"

### Perfect! This version is designed for:
1. **Each user only accesses their own data** ✅
2. **No cross-user queries needed** ✅  
3. **Running on AWS with IAM roles** ✅
4. **Cost optimization** ✅
5. **Auto-scaling** ✅

## 📊 Architecture

### Database Design

```
DynamoDB Tables:
├── dermalens-users
│   ├── PK: user_id
│   └── GSI: email-index
├── dermalens-scans
│   ├── PK: user_id
│   ├── SK: scan_id
│   └── LSI: scan-date-index
├── dermalens-treatment-plans
│   ├── PK: user_id
│   └── SK: plan_id
└── dermalens-chat-messages
    ├── PK: user_id
    ├── SK: message_id
    └── LSI: session-index
```

### IAM Role Authentication

**No Access Keys Needed!**
```
EC2/ECS/Lambda → IAM Role → DynamoDB/S3
(Credentials provided automatically by AWS)
```

## ⚡ Quick Start

### Local Testing with DynamoDB Local

```bash
# 1. Start DynamoDB Local
docker run -d -p 8000:8000 amazon/dynamodb-local

# 2. Install dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Configure for local
cp .env.example .env
# Add to .env:
AWS_DYNAMODB_ENDPOINT=http://localhost:8000

# 4. Start server
uvicorn app.main:app --reload
```

Visit: **http://localhost:8000/api/v1/docs**

Tables are created automatically on startup!

### Using Real AWS DynamoDB

```bash
# 1. Configure AWS CLI (temporary for local dev)
aws configure
# Enter your AWS credentials and region

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env with your settings

# 4. Start server
uvicorn app.main:app --reload
```

## 🚀 Production Deployment

### Step 1: Create IAM Role

```bash
# Create role for EC2
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

# Attach DynamoDB permissions
aws iam attach-role-policy \
  --role-name DermaLensAppRole \
  --policy-arn arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess

# Attach S3 permissions
aws iam attach-role-policy \
  --role-name DermaLensAppRole \
  --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess
```

### Step 2: Launch EC2 with IAM Role

```bash
# Create instance profile
aws iam create-instance-profile \
  --instance-profile-name DermaLensAppProfile

# Add role to profile
aws iam add-role-to-instance-profile \
  --instance-profile-name DermaLensAppProfile \
  --role-name DermaLensAppRole

# Launch EC2 with IAM role
aws ec2 run-instances \
  --image-id ami-0c55b159cbfafe1f0 \
  --instance-type t2.micro \
  --iam-instance-profile Name=DermaLensAppProfile \
  --key-name your-key \
  --security-groups your-sg
```

### Step 3: Deploy App

```bash
# SSH into EC2
ssh -i your-key.pem ubuntu@your-ec2-ip

# Install Python
sudo apt update && sudo apt install -y python3-pip python3-venv

# Clone and setup
git clone your-repo
cd dermalens_backend_dynamodb
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure
cp .env.example .env
nano .env  # Set your configs, NO AWS KEYS NEEDED!

# Run
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## 📁 Project Structure

```
dermalens_backend_dynamodb/
├── app/
│   ├── main.py                       # FastAPI app (DynamoDB version)
│   ├── core/
│   │   ├── config.py                 # Settings (no AWS keys!)
│   │   └── security.py               # JWT auth
│   ├── db/
│   │   └── dynamodb.py               # DynamoDB client + table setup
│   ├── repositories/                 # Data access layer
│   │   ├── user_repository.py        # User CRUD operations
│   │   ├── scan_repository.py        # Scan operations
│   │   └── treatment_plan_repository.py
│   ├── schemas/                      # Pydantic models
│   ├── api/v1/routes/               # API endpoints
│   │   └── auth_dynamodb.py         # Auth endpoints
│   └── services/                     # Business logic
├── DYNAMODB_GUIDE.md                # Comprehensive DynamoDB guide
├── requirements.txt                  # Dependencies
├── .env.example                     # Config template
└── README.md                        # This file
```

## 🔑 Environment Variables

```env
# NO AWS ACCESS KEYS NEEDED!
# IAM role provides them automatically

# AWS Config
AWS_REGION=us-east-1

# DynamoDB Tables
DYNAMODB_USERS_TABLE=dermalens-users
DYNAMODB_SCANS_TABLE=dermalens-scans
DYNAMODB_PLANS_TABLE=dermalens-treatment-plans
DYNAMODB_CHAT_TABLE=dermalens-chat-messages

# S3 (also uses IAM role)
S3_BUCKET_NAME=dermalens-images

# App Config
SECRET_KEY=your-secret-key
GEMINI_API_KEY=your-gemini-key
```

## 🧪 Testing

### Register a User
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpass123",
    "full_name": "Test User"
  }'
```

### Login
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpass123"
  }'
```

### View Tables (Local)
```bash
# List tables
aws dynamodb list-tables --endpoint-url http://localhost:8000

# View users
aws dynamodb scan \
  --table-name dermalens-users \
  --endpoint-url http://localhost:8000
```

## 💰 Cost Comparison

### PostgreSQL RDS (Previous):
- Minimum: ~$15/month (db.t3.micro)
- Always running
- Manual scaling

### DynamoDB (Current):
- Free tier: 25GB + 200M requests/month
- Pay per use: $0-5/month for small apps
- Auto-scaling
- Serverless

## 🔒 Security

### IAM Role Policy (Minimal Permissions)

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
        "dynamodb:Query"
      ],
      "Resource": "arn:aws:dynamodb:*:*:table/dermalens-*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject"
      ],
      "Resource": "arn:aws:s3:::dermalens-images/*"
    }
  ]
}
```

## 📚 Key Differences from PostgreSQL

| Feature | PostgreSQL | DynamoDB |
|---------|-----------|----------|
| Auth | Access Keys | IAM Role ✅ |
| Database | RDS | DynamoDB ✅ |
| Cost | Fixed $15+ | Pay-per-use $0-5 |
| Scaling | Manual | Auto ✅ |
| Setup | Complex | Simple ✅ |
| Migrations | Alembic | Auto-create |

## 🐛 Troubleshooting

### IAM Role Not Working
```bash
# Verify role is attached
aws ec2 describe-instances --instance-ids i-xxxxx

# Check credentials
curl http://169.254.169.254/latest/meta-data/iam/security-credentials/
```

### DynamoDB Local Connection
```bash
# Restart DynamoDB Local
docker restart $(docker ps -q --filter ancestor=amazon/dynamodb-local)

# Verify it's running
curl http://localhost:8000
```

## 📖 Documentation

- **DYNAMODB_GUIDE.md** - Complete DynamoDB setup and deployment guide
- **README.md** - This file (quick start)
- **/api/v1/docs** - Interactive API documentation

## 🎯 Next Steps

1. ✅ Test locally with DynamoDB Local
2. ✅ Create IAM role in AWS
3. ✅ Deploy to EC2 with IAM role attached
4. ✅ Tables auto-create on first run
5. ✅ Test all endpoints
6. ✅ Monitor with CloudWatch

## 🎉 Benefits Summary

- **No access keys** to manage or leak ✅
- **No RDS costs** (~$180/year saved) ✅
- **Auto-scaling** for traffic spikes ✅
- **Free tier** for development ✅
- **Serverless** - no servers to manage ✅
- **Perfect isolation** - users can't see each other's data ✅

---

**Ready to deploy!** No RDS, no access keys, just pure serverless goodness! 🚀
