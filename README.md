# DermaLens Backend API

AI-powered skincare analysis platform backend built with FastAPI, PostgreSQL, and integrates with NanoBanana AI and Gemini AI.

## 🏗️ Project Structure

```
dermalens_backend/
├── app/
│   ├── main.py                          # FastAPI application entry point
│   ├── core/
│   │   ├── config.py                    # Configuration settings
│   │   └── security.py                  # JWT auth & security utilities
│   ├── db/
│   │   └── session.py                   # Database session management
│   ├── models/                          # SQLAlchemy ORM models
│   │   ├── __init__.py
│   │   ├── user.py                      # User model
│   │   ├── scan.py                      # Facial scan model
│   │   ├── score_delta.py               # Score tracking model
│   │   ├── treatment_plan.py            # Treatment routine model
│   │   └── chat_message.py              # Chat history model
│   ├── schemas/                         # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── user.py                      # User schemas
│   │   ├── scan.py                      # Scan schemas
│   │   ├── treatment_plan.py            # Treatment plan schemas
│   │   └── chat.py                      # Chat schemas
│   ├── api/
│   │   └── v1/
│   │       ├── router.py                # Main API router
│   │       └── routes/
│   │           ├── auth.py              # Authentication endpoints
│   │           ├── scans.py             # Scan endpoints
│   │           ├── routines.py          # Treatment plan endpoints
│   │           └── chat.py              # Chat endpoints
│   └── services/                        # Business logic services
│       ├── storage/
│       │   └── s3_service.py            # AWS S3 integration
│       ├── vision/
│       │   └── nanobanana_service.py    # NanoBanana AI integration
│       ├── chat_ai/
│       │   └── gemini_service.py        # Gemini AI chat integration
│       └── routine_engine/
│           └── routine_generator.py     # Treatment routine generation
├── alembic/                             # Database migrations
│   ├── env.py
│   └── versions/
├── .env                                 # Environment variables (create from .env.example)
├── .env.example                         # Environment template
├── alembic.ini                          # Alembic configuration
├── requirements.txt                     # Python dependencies
└── README.md                            # This file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 14+
- AWS S3 bucket
- NanoBanana API key
- Gemini API key

### Installation

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd dermalens_backend
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your actual values
```

5. **Set up PostgreSQL database**
```bash
createdb dermalens
```

6. **Run database migrations**
```bash
alembic upgrade head
```

7. **Run the application**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

API Documentation: `http://localhost:8000/api/v1/docs`

## 📋 Environment Variables

Key environment variables (see `.env.example` for complete list):

```env
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/dermalens

# Security
SECRET_KEY=your-secret-key-here

# AWS S3
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret
S3_BUCKET_NAME=dermalens-images

# AI Services
NANOBANANA_API_KEY=your-nanobanana-key
GEMINI_API_KEY=your-gemini-key
```

## 🔑 API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login user
- `GET /api/v1/auth/me` - Get current user profile
- `PATCH /api/v1/auth/me` - Update user profile
- `POST /api/v1/auth/change-password` - Change password

### Scans
- `POST /api/v1/scans/presign` - Get presigned URL for image upload
- `POST /api/v1/scans/submit` - Submit scan for processing
- `GET /api/v1/scans/history` - Get scan history
- `GET /api/v1/scans/{scan_id}` - Get scan details
- `GET /api/v1/scans/{scan_id}/deltas` - Get score changes

### Treatment Plans
- `POST /api/v1/routines/` - Create treatment plan
- `GET /api/v1/routines/current` - Get active treatment plan
- `PATCH /api/v1/routines/current` - Adjust treatment plan
- `GET /api/v1/routines/history` - Get plan history
- `GET /api/v1/routines/recommendations/{concern}` - Get product recommendations

### Chat
- `POST /api/v1/chat/message` - Send chat message
- `GET /api/v1/chat/history` - Get chat history
- `DELETE /api/v1/chat/session/{session_id}` - Delete chat session

## 🗄️ Database Models

### User
- Authentication and profile information
- Skin type and primary concern
- Relationships: scans, treatment_plans, chat_messages

### Scan
- Facial image references (S3 keys)
- AI analysis scores (acne, redness, oiliness, dryness, etc.)
- Processing status and metadata

### ScoreDelta
- Score changes between scans
- Improvement/worsening tracking
- Significance flags

### TreatmentPlan
- Locked routine (AM/PM steps)
- Lock period (14-28 days)
- Product recommendations
- Adjustment tracking

### ChatMessage
- Conversation history
- Context references (current scan/plan)
- AI metadata

## 🔄 Key Features

### 1. Image Upload Flow
```
Client requests presigned URL → Upload to S3 → Submit scan → Background processing → AI analysis
```

### 2. Treatment Lock Logic
- Plans are locked for 14-28 days
- Weekly scans track progress
- Adjustments only allowed if:
  - Score decline > threshold
  - Severe irritation reported
  - Lock period expired

### 3. Score Tracking
- Baseline scan establishes starting point
- Weekly scans compare against baseline
- Delta calculations show improvement/decline
- Trends inform adjustment decisions

### 4. AI Chat Context
- Maintains conversation history
- Aware of current treatment status
- References latest scan results
- Cannot modify locked plans

## 🧪 Testing

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest

# Run with coverage
pytest --cov=app tests/
```

## 🚢 Deployment

### Docker Deployment (Recommended)

```bash
# Build image
docker build -t dermalens-api .

# Run container
docker run -d -p 8000:8000 --env-file .env dermalens-api
```

### Manual Deployment

1. Set up production database
2. Configure environment variables
3. Run migrations: `alembic upgrade head`
4. Use production ASGI server:
```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## 📊 Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# View migration history
alembic history
```

## 🔒 Security Notes

- JWT tokens expire after 7 days (configurable)
- Passwords hashed with bcrypt
- S3 presigned URLs expire after 1 hour
- CORS configured for specific origins
- Rate limiting recommended for production

## 🐛 Troubleshooting

### Database Connection Issues
- Verify PostgreSQL is running
- Check DATABASE_URL format
- Ensure asyncpg is installed

### S3 Upload Failures
- Verify AWS credentials
- Check bucket permissions
- Confirm CORS settings on bucket

### AI Service Errors
- Validate API keys
- Check service quotas
- Review request/response logs

## 📝 Development Guidelines

### Adding New Endpoints
1. Create route in appropriate `routes/` file
2. Define Pydantic schemas in `schemas/`
3. Add business logic to `services/`
4. Update this README

### Database Changes
1. Modify models in `models/`
2. Create migration: `alembic revision --autogenerate`
3. Review generated migration
4. Apply: `alembic upgrade head`

## 📄 License

[Your License Here]

## 👥 Contributors

[Your Team/Contributors]

## 🤝 Support

For issues and questions:
- GitHub Issues: [Your Repo URL]
- Email: [Your Support Email]
