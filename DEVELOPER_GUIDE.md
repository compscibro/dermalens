# DermaLens Backend - Complete Development Guide

## 📖 Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [Getting Started](#getting-started)
3. [API Flow Diagrams](#api-flow-diagrams)
4. [Database Schema](#database-schema)
5. [Service Integrations](#service-integrations)
6. [Development Workflow](#development-workflow)
7. [Testing Strategy](#testing-strategy)
8. [Deployment Guide](#deployment-guide)

## 🏛️ Architecture Overview

### Tech Stack
- **Framework**: FastAPI (async Python web framework)
- **Database**: PostgreSQL with SQLAlchemy ORM (async)
- **Authentication**: JWT tokens with bcrypt password hashing
- **Storage**: AWS S3 for image storage
- **AI Services**: 
  - NanoBanana for facial analysis
  - Gemini AI for conversational chat
- **Migrations**: Alembic

### Key Design Patterns
- **Repository Pattern**: Database access through models
- **Service Layer**: Business logic separated from API routes
- **Dependency Injection**: FastAPI's built-in DI for database sessions and auth
- **Async/Await**: Full async support for better performance

## 🚀 Getting Started

### Method 1: Docker Compose (Recommended for Development)
```bash
# Clone repository
git clone <your-repo>
cd dermalens_backend

# Copy environment file
cp .env.example .env
# Edit .env with your API keys

# Start everything
docker-compose up -d

# Run migrations
docker-compose exec api alembic upgrade head

# View logs
docker-compose logs -f api
```

Access:
- API: http://localhost:8000
- Docs: http://localhost:8000/api/v1/docs
- pgAdmin: http://localhost:5050 (optional, use `docker-compose --profile tools up`)

### Method 2: Local Development
```bash
# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up database
createdb dermalens

# Copy and configure environment
cp .env.example .env
# Edit .env with your settings

# Run migrations
alembic upgrade head

# Start server
./start.sh
# Or manually:
uvicorn app.main:app --reload
```

## 🔄 API Flow Diagrams

### User Registration & Authentication Flow
```
1. POST /api/v1/auth/register
   → Validate email uniqueness
   → Hash password
   → Create user record
   → Generate JWT token
   → Return token + user data

2. POST /api/v1/auth/login
   → Validate credentials
   → Update last_login
   → Generate JWT token
   → Return token + user data

3. Authenticated Requests
   → Include: Authorization: Bearer <token>
   → Middleware validates JWT
   → Extracts user from token
   → Injects current_user into endpoint
```

### Scan Submission Flow
```
1. Client: POST /api/v1/scans/presign (for each angle: front, left, right)
   → Server generates S3 presigned URL
   → Returns upload URL + image key

2. Client: Uploads image directly to S3 using presigned URL
   → S3 stores image
   → Returns success

3. Client: POST /api/v1/scans/submit
   → With all three image keys
   → Server creates Scan record (status: PENDING)
   → Queues background processing
   → Returns scan with ID

4. Background Task: process_scan()
   → Status → PROCESSING
   → Generate presigned download URLs
   → Call NanoBanana API with image URLs
   → Parse and store analysis results
   → Status → COMPLETED
   → Calculate score deltas (if not baseline)
```

### Treatment Plan Creation Flow
```
1. User completes baseline scan
2. POST /api/v1/routines/
   → Validate no active plan exists
   → Verify baseline scan is complete
   → routine_engine.generate_routine()
      → Analyze scores
      → Select appropriate ingredients
      → Build AM routine (cleanser → serum → moisturizer → SPF)
      → Build PM routine (cleanser → treatment → serum → moisturizer)
   → Create TreatmentPlan record (status: ACTIVE)
   → Set lock period (14-28 days)
   → Return plan with routines
```

### Weekly Scan & Progress Tracking
```
1. User takes weekly scan (minimum 7 days interval)
2. POST /api/v1/scans/submit
3. Background processing:
   → Analyze images
   → calculate_score_deltas()
      → Find previous scan
      → For each metric:
         - Calculate delta
         - Calculate percent change
         - Determine improvement/worsening
         - Flag if significant (>10% change)
      → Store ScoreDelta records
4. GET /api/v1/scans/{scan_id}/deltas
   → Return all score comparisons
   → Frontend displays progress charts
```

### Treatment Plan Adjustment Logic
```
PATCH /api/v1/routines/current

Adjustment Triggers:
1. SEVERE_IRRITATION (>20% score increase)
   → Immediate adjustment allowed
   
2. SCORE_DECLINE (>10% increase in concern metric)
   → Check latest score deltas
   → Allow adjustment if decline confirmed
   
3. USER_REQUEST
   → Only if plan.can_adjust == True
   → Only after minimum lock period

If adjustment allowed:
→ Mark current plan as ADJUSTED
→ Create new plan (version + 1)
→ Generate new routines based on latest scan
→ New lock period starts
```

### Chat with Context Flow
```
POST /api/v1/chat/message

1. Build context:
   → Get user profile
   → Get active treatment plan (if any)
      - Lock status
      - Days remaining
   → Get latest scan results
   → Calculate score trends (improving/stable/worsening)

2. Prepare conversation:
   → Fetch last 20 messages from session
   → Format for Gemini API

3. Generate response:
   → Send to Gemini with context
   → Get AI response
   → Flag if contains medical advice
   → Flag if requires follow-up

4. Store messages:
   → Save user message
   → Save AI response
   → Link to current scan/plan

5. Return AI response to user
```

## 🗄️ Database Schema

### Users Table
```sql
users (
    id SERIAL PRIMARY KEY,
    email VARCHAR UNIQUE NOT NULL,
    hashed_password VARCHAR NOT NULL,
    full_name VARCHAR,
    skin_type VARCHAR,  -- oily, dry, combination, sensitive
    primary_concern VARCHAR,  -- acne, redness, dryness, oiliness
    is_active BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP,
    last_login TIMESTAMP
)
```

### Scans Table
```sql
scans (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    status VARCHAR,  -- pending, processing, completed, failed
    scan_date TIMESTAMP DEFAULT NOW(),
    
    -- S3 image storage
    front_image_key VARCHAR NOT NULL,
    left_image_key VARCHAR NOT NULL,
    right_image_key VARCHAR NOT NULL,
    front_image_url VARCHAR,
    left_image_url VARCHAR,
    right_image_url VARCHAR,
    
    -- AI analysis scores (0-100)
    acne_score FLOAT,
    redness_score FLOAT,
    oiliness_score FLOAT,
    dryness_score FLOAT,
    texture_score FLOAT,
    pore_size_score FLOAT,
    dark_spots_score FLOAT,
    overall_score FLOAT,
    
    -- Metadata
    raw_analysis JSONB,
    analysis_model_version VARCHAR,
    confidence_score FLOAT,
    processing_time_ms INTEGER,
    error_message VARCHAR,
    
    -- Progress tracking
    is_baseline BOOLEAN DEFAULT false,
    week_number INTEGER,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP
)
```

### Score Deltas Table
```sql
score_deltas (
    id SERIAL PRIMARY KEY,
    current_scan_id INTEGER REFERENCES scans(id),
    previous_scan_id INTEGER REFERENCES scans(id),
    
    metric_name VARCHAR NOT NULL,  -- acne, redness, etc.
    previous_score FLOAT,
    current_score FLOAT,
    delta FLOAT,  -- current - previous
    percent_change FLOAT,
    
    improvement BOOLEAN,  -- true if better
    is_significant BOOLEAN,  -- true if >threshold
    
    days_between_scans INTEGER,
    treatment_plan_id INTEGER REFERENCES treatment_plans(id),
    
    created_at TIMESTAMP DEFAULT NOW()
)
```

### Treatment Plans Table
```sql
treatment_plans (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    status VARCHAR,  -- active, completed, adjusted, cancelled
    version INTEGER DEFAULT 1,
    
    primary_concern VARCHAR NOT NULL,
    
    -- Lock period
    start_date DATE NOT NULL,
    planned_end_date DATE NOT NULL,
    actual_end_date DATE,
    lock_duration_days INTEGER,
    
    baseline_scan_id INTEGER REFERENCES scans(id),
    
    -- Routines (JSONB arrays of steps)
    am_routine JSONB NOT NULL,
    pm_routine JSONB NOT NULL,
    recommended_products JSONB,
    
    instructions TEXT,
    warnings TEXT,
    
    -- Adjustment tracking
    can_adjust BOOLEAN DEFAULT false,
    adjustment_reason VARCHAR,
    adjustment_notes TEXT,
    previous_plan_id INTEGER REFERENCES treatment_plans(id),
    
    -- AI metadata
    generation_model VARCHAR,
    generation_prompt TEXT,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP
)
```

### Chat Messages Table
```sql
chat_messages (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    role VARCHAR NOT NULL,  -- 'user' or 'assistant'
    content TEXT NOT NULL,
    
    current_scan_id INTEGER REFERENCES scans(id),
    current_plan_id INTEGER REFERENCES treatment_plans(id),
    
    reported_concerns JSONB,
    
    -- AI metadata
    model_used VARCHAR,
    tokens_used INTEGER,
    response_time_ms INTEGER,
    
    -- Flags
    contains_medical_advice BOOLEAN DEFAULT false,
    requires_follow_up BOOLEAN DEFAULT false,
    
    session_id VARCHAR,
    
    created_at TIMESTAMP DEFAULT NOW()
)
```

## 🔌 Service Integrations

### AWS S3 Service (`app/services/storage/s3_service.py`)

**Purpose**: Handle image storage and retrieval

**Key Methods**:
- `generate_image_key()`: Create unique S3 key for image
- `generate_presigned_upload_url()`: Get URL for client-side upload
- `generate_presigned_download_url()`: Get URL for image viewing
- `check_image_exists()`: Verify image in S3
- `delete_image()`: Remove image from S3

**Configuration**:
```python
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
S3_BUCKET_NAME=dermalens-images
AWS_REGION=us-east-1
```

**S3 Bucket Setup**:
1. Create bucket in AWS Console
2. Enable CORS:
```json
[{
    "AllowedOrigins": ["*"],
    "AllowedMethods": ["GET", "PUT", "POST"],
    "AllowedHeaders": ["*"],
    "ExposeHeaders": ["ETag"]
}]
```
3. Set bucket policy for presigned URLs

### NanoBanana AI Service (`app/services/vision/nanobanana_service.py`)

**Purpose**: Facial skin analysis using AI

**Key Methods**:
- `analyze_images()`: Submit images for analysis
- `validate_image_quality()`: Pre-check image suitability
- `_normalize_scores()`: Convert API response to 0-100 scale
- `_calculate_overall_score()`: Weighted average of metrics

**Expected API Response** (placeholder - adapt to actual API):
```json
{
  "analysis": {
    "acne": {"score": 45.2, "confidence": 0.95},
    "redness": {"score": 32.1, "confidence": 0.93},
    "oiliness": {"score": 67.8, "confidence": 0.91},
    "dryness": {"score": 21.5, "confidence": 0.94}
  },
  "model_version": "1.2.3",
  "confidence": 0.93
}
```

### Gemini AI Service (`app/services/chat_ai/gemini_service.py`)

**Purpose**: Conversational AI for skincare guidance

**System Prompt**:
- Acts as DermaLens AI assistant
- Provides education, not diagnosis
- Cannot modify treatment plans
- Encourages routine adherence
- Flags severe symptoms for medical attention

**Context Building**:
```python
ChatContextInfo(
    user_id=123,
    user_name="Jane",
    primary_concern="acne",
    has_active_plan=True,
    plan_locked=True,
    days_remaining=10,
    has_recent_scan=True,
    latest_scan_date="2024-02-10",
    latest_scores={"acne": 42.5, ...},
    score_trends={"acne": "improving", ...}
)
```

### Routine Engine (`app/services/routine_engine/routine_generator.py`)

**Purpose**: Generate personalized skincare routines

**Ingredient Database**:
- Maps concerns to active ingredients
- Includes concentrations and benefits
- Provides supportive ingredients
- Maintains conflict rules

**Routine Structure**:
```json
{
  "am_routine": [
    {
      "step_number": 1,
      "product_type": "cleanser",
      "instructions": "Use gentle salicylic acid cleanser...",
      "wait_time_minutes": 0
    },
    // ... more steps
  ],
  "pm_routine": [...]
}
```

**Conflict Rules**:
- Retinol + Vitamin C/AHA/BHA = conflict
- Benzoyl Peroxide + Retinol = conflict
- Engine prevents combining conflicting actives

## 🔬 Development Workflow

### Adding a New Feature

1. **Plan the Feature**
   - Define requirements
   - Design database changes
   - Plan API endpoints

2. **Update Models** (if needed)
   ```bash
   # Edit models in app/models/
   # Create migration
   alembic revision --autogenerate -m "add feature X"
   # Review migration
   # Apply migration
   alembic upgrade head
   ```

3. **Create Schemas**
   ```python
   # Add to app/schemas/
   class NewFeatureRequest(BaseModel):
       field1: str
       field2: int
   
   class NewFeatureResponse(BaseModel):
       id: int
       field1: str
       created_at: datetime
   ```

4. **Add Business Logic**
   ```python
   # Add to appropriate service in app/services/
   async def process_feature(data):
       # Business logic here
       pass
   ```

5. **Create API Endpoint**
   ```python
   # Add to appropriate router in app/api/v1/routes/
   @router.post("/feature", response_model=NewFeatureResponse)
   async def create_feature(
       data: NewFeatureRequest,
       current_user: User = Depends(get_current_active_user),
       db: AsyncSession = Depends(get_db)
   ):
       # Endpoint logic
       pass
   ```

6. **Test the Feature**
   - Manual testing via /docs
   - Write unit tests
   - Integration tests

7. **Update Documentation**
   - Update README
   - Add docstrings
   - Update API examples

### Database Migration Best Practices

```bash
# Always review auto-generated migrations
alembic revision --autogenerate -m "description"
# Edit the generated file in alembic/versions/

# Test migration
alembic upgrade head
# Test rollback
alembic downgrade -1
# Re-apply
alembic upgrade head

# In production, use offline mode for safety
alembic upgrade head --sql > migration.sql
# Review SQL, then apply manually
```

## 🧪 Testing Strategy

### Unit Tests
```python
# tests/test_services/test_routine_engine.py
import pytest
from app.services.routine_engine.routine_generator import routine_engine

def test_generate_routine_for_acne():
    scores = {"acne": 75, "redness": 30, "oiliness": 60, "dryness": 20}
    routine = routine_engine.generate_routine("acne", scores)
    
    assert "am_routine" in routine
    assert "pm_routine" in routine
    assert len(routine["am_routine"]) >= 4  # cleanser, serum, moisturizer, SPF
    assert any(step["product_type"] == "sunscreen" for step in routine["am_routine"])
```

### Integration Tests
```python
# tests/test_api/test_scans.py
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_submit_scan_flow(async_client: AsyncClient, auth_token):
    # Test presign
    response = await async_client.post(
        "/api/v1/scans/presign",
        json={"angle": "front", "content_type": "image/jpeg", "file_size": 1000000},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    
    # Test submit
    response = await async_client.post(
        "/api/v1/scans/submit",
        json={
            "front_image_key": "test/front.jpg",
            "left_image_key": "test/left.jpg",
            "right_image_key": "test/right.jpg"
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 201
```

## 🚀 Deployment Guide

### Environment Setup

1. **Production Environment Variables**
```bash
DEBUG=False
DATABASE_URL=postgresql+asyncpg://prod_user:prod_pass@prod-db:5432/dermalens
SECRET_KEY=<generate-strong-secret>
AWS_ACCESS_KEY_ID=<prod-key>
AWS_SECRET_ACCESS_KEY=<prod-secret>
NANOBANANA_API_KEY=<prod-key>
GEMINI_API_KEY=<prod-key>
```

2. **Database Setup**
```bash
# Create production database
createdb dermalens_prod

# Run migrations
DATABASE_URL=<prod-url> alembic upgrade head
```

3. **Docker Deployment**
```bash
# Build production image
docker build -t dermalens-api:latest .

# Run with production settings
docker run -d \
  -p 8000:8000 \
  --env-file .env.production \
  --name dermalens-api \
  dermalens-api:latest
```

4. **Using Gunicorn for Production**
```bash
gunicorn app.main:app \
  -w 4 \
  -k uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --access-logfile - \
  --error-logfile -
```

### Monitoring & Logging

Add structured logging:
```python
# app/core/logging.py
import logging
from pythonjsonlogger import jsonlogger

logger = logging.getLogger()
logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)
logger.setLevel(logging.INFO)
```

### Health Checks

Already implemented in `app/main.py`:
```
GET /health
→ {"status": "healthy", "service": "DermaLens", "version": "1.0.0"}
```

### Performance Optimization

1. **Database Connection Pooling** (already configured)
2. **Async everywhere** (already implemented)
3. **Redis caching** (future enhancement)
4. **CDN for S3 images** (recommended)

## 📞 Support & Troubleshooting

### Common Issues

**Issue: Database connection fails**
```
Solution: 
- Check PostgreSQL is running
- Verify DATABASE_URL format
- Ensure asyncpg installed
- Check firewall/network settings
```

**Issue: S3 upload fails**
```
Solution:
- Verify AWS credentials
- Check bucket CORS settings
- Confirm bucket region matches AWS_REGION
- Check bucket permissions
```

**Issue: Migration conflicts**
```
Solution:
alembic downgrade -1  # Rollback
# Fix migration file
alembic upgrade head
```

### Getting Help

- Check API docs: `/api/v1/docs`
- Review logs: `docker-compose logs -f api`
- Database inspection: `docker-compose exec db psql -U dermalens`

---

## 🎉 You're Ready!

This backend provides a complete foundation for DermaLens. The architecture is:
- ✅ Scalable
- ✅ Well-structured
- ✅ Production-ready
- ✅ Fully documented

Happy coding! 🚀
