# DermaLens Developer Guide

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Repository Structure](#repository-structure)
3. [Getting Started](#getting-started)
4. [Backend](#backend)
5. [iOS Frontend](#ios-frontend)
6. [API Reference](#api-reference)
7. [Data Flow](#data-flow)
8. [Deployment](#deployment)
9. [Troubleshooting](#troubleshooting)

---

## Architecture Overview

DermaLens is an AI-powered skincare analysis platform consisting of two components:

| Layer | Technology | Description |
|-------|-----------|-------------|
| **iOS Client** | SwiftUI, iOS 26.1 | Native app with 5-step analysis workflow |
| **API Server** | FastAPI, Python 3.11+ | Stateless REST API, S3-backed persistence |
| **AI Vision** | Gemini 2.5 Flash | Multi-angle facial skin analysis |
| **AI Chat** | Gemini 2.5 Flash | Context-aware skincare guidance |
| **Storage** | AWS S3 | Images and JSON data (no database) |
| **Hosting** | AWS EC2 (t3.micro) | Single-instance deployment |

### Key Design Decisions

- **No database** -- all persistence is S3 JSON files, keeping the stack minimal.
- **No authentication** -- users are identified by email (query parameter). Suitable for MVP/hackathon scope.
- **No JWT/sessions** -- every request is stateless; the email parameter is the only identifier.
- **Rule-based routines** -- skincare routines are generated locally (not by AI) using an ingredient engine with conflict detection.
- **AI for analysis only** -- Gemini Vision scores skin metrics; Gemini Chat provides guidance. Neither prescribes or diagnoses.

---

## Repository Structure

```
dermalens/
├── backend/                          # FastAPI server
│   ├── main.py                       # Application entry point
│   ├── core/
│   │   └── config.py                 # Settings (env vars, model names)
│   ├── api/v1/
│   │   ├── router.py                 # Route aggregator
│   │   └── routes/
│   │       ├── users.py              # Profile CRUD
│   │       ├── scans.py              # Photo upload + AI analysis
│   │       ├── routines.py           # Routine retrieval
│   │       └── chat.py               # AI chat
│   ├── schemas/                      # Pydantic request/response models
│   │   ├── user.py
│   │   ├── scan.py
│   │   ├── routine.py
│   │   └── chat.py
│   └── services/
│       ├── storage/s3_service.py     # S3 read/write operations
│       ├── ai_pipeline.py            # Orchestrates vision + routine
│       ├── vision/
│       │   ├── gemini_vision_service.py  # Gemini structured output
│       │   ├── validators.py         # Retake detection
│       │   └── normalize.py          # Score clamping
│       ├── scoring/
│       │   ├── metrics.py            # SkinMetrics model
│       │   └── trend.py              # Profile builder
│       ├── routine_engine/
│       │   ├── engine.py             # Rule-based routine builder
│       │   ├── routine_generator.py  # Format adapter
│       │   ├── conflicts.py          # Ingredient conflict rules
│       │   ├── lock_policy.py        # Plan lock (2-week minimum)
│       │   └── adjustment_rules.py   # Active back-off logic
│       └── chat_ai/
│           └── gemini_service.py     # Chat with context injection
│
├── frontend/dermalense/              # Xcode project
│   └── dermalense/
│       ├── DermaLensApp.swift        # App entry point
│       ├── MainTabView.swift         # Tab navigation
│       ├── Models.swift              # Data models + AppState
│       ├── Theme.swift               # Design system tokens
│       ├── Info.plist                # ATS exceptions, scene config
│       ├── Services/
│       │   ├── APIService.swift      # Networking layer
│       │   └── APIError.swift        # Error types
│       └── Views/
│           ├── Onboarding/
│           │   └── OnboardingView.swift
│           ├── Dashboard/
│           │   ├── DashboardView.swift
│           │   ├── ConcernsFormView.swift
│           │   ├── PhotoUploadView.swift
│           │   ├── SkinAnalysisView.swift
│           │   ├── RoutinePlanView.swift
│           │   └── ChatView.swift
│           └── Account/
│               ├── AccountView.swift
│               ├── EditProfileView.swift
│               ├── FullHistoryView.swift
│               └── HistoryDetailView.swift
│
├── requirements.txt                  # Python dependencies
├── start.sh                          # Backend startup script
├── .env                              # Environment variables (not committed)
└── .gitignore
```

---

## Getting Started

### Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| Xcode | 26.1+ | iOS build toolchain |
| Python | 3.11+ | Backend runtime |
| AWS CLI | 2.x | S3 bucket setup (optional) |
| Git | 2.x | Version control |

### Backend Setup

```bash
# Clone and enter the repository
git clone git@github.com:compscibro/dermalens.git
cd dermalens

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your credentials (see Environment Variables section)

# Start the development server
python -m backend.main
```

The API will be available at `http://localhost:8000`. Interactive docs at `http://localhost:8000/api/v1/docs`.

### iOS Setup

1. Open `frontend/dermalense/dermalense.xcodeproj` in Xcode 26.1+.
2. The project uses **PBXFileSystemSynchronizedRootGroup** -- new files are auto-discovered. No manual file reference management needed.
3. Select the `dermalense` scheme and a simulator (iPhone 17 Pro recommended).
4. Build and run (`Cmd + R`).

**Build from terminal:**

```bash
xcodebuild -scheme dermalense \
  -destination 'platform=iOS Simulator,name=iPhone 17 Pro' \
  build
```

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `AWS_ACCESS_KEY_ID` | Yes | -- | AWS IAM access key |
| `AWS_SECRET_ACCESS_KEY` | Yes | -- | AWS IAM secret key |
| `AWS_REGION` | No | `us-east-1` | S3 bucket region |
| `S3_BUCKET_NAME` | No | `dermalens-bucket` | S3 bucket name |
| `GEMINI_API_KEY` | Yes | -- | Google Gemini API key |
| `GEMINI_MODEL` | No | `gemini-2.5-flash` | Chat model identifier |
| `GEMINI_VISION_MODEL` | No | `gemini-2.5-flash` | Vision model identifier |

---

## Backend

### Services Architecture

```
Request → Route Handler → AI Pipeline → S3 Storage
                              │
                    ┌─────────┼──────────┐
                    v         v          v
              Gemini Vision  Scoring   Routine Engine
              (analysis)    (profile)  (rule-based)
```

**AI Pipeline** (`services/ai_pipeline.py`) orchestrates the full scan flow:

1. Sends images to **Gemini Vision** for structured skin metric extraction.
2. Validates image quality (rejects low-confidence or flagged images with HTTP 422).
3. Builds a **skin profile** from metrics + user quiz answers.
4. Generates a **routine plan** using the local rule-based engine.
5. Returns analysis, routine, and lock status.

### S3 Data Layout

All user data persists as JSON files and images in a single S3 bucket:

```
users/{email}/
  profile.json
  scans/{scan_id}/
    front.jpg
    left.jpg
    right.jpg
    analysis.json
    routine.json
    concerns.json
    raw_metrics.json
    plan.json
  chat/{session_id}.json
```

### Routine Engine

The routine engine is deterministic (not AI-generated). It selects active ingredients based on the user's priority concern and metric scores:

| Priority | Active Ingredient | Frequency |
|----------|------------------|-----------|
| Acne (score >= 45) | Salicylic acid (BHA) | 2-3x/week |
| Redness | Niacinamide 2-5% | Daily |
| Texture | Lactic acid (AHA) | 1-2x/week |
| Barrier/Dryness | Hyaluronic acid + ceramides | Daily |

Safety rules reduce frequency for high-irritation-risk profiles. Ingredient conflicts (e.g., retinoid + strong acid) are enforced.

---

## iOS Frontend

### State Management

The app uses the **Observation** framework (iOS 17+), not the legacy `ObservableObject` pattern:

```
@Observable class AppState     →  Single source of truth
@State private var ...         →  View-local state
@Environment(AppState.self)    →  Dependency injection
```

> **Important:** `ObservableObject` + `@StateObject` + `@EnvironmentObject` does not compile with the project's strict concurrency settings (`SWIFT_DEFAULT_ACTOR_ISOLATION = MainActor`). Always use `@Observable` + `@State` + `@Environment(Type.self)`.

### Navigation Structure

```
DermaLensApp
├── OnboardingView              (if !isOnboarded)
└── MainTabView                 (if isOnboarded)
    ├── Tab 1: DashboardView    (5-step wizard)
    │   ├── ConcernsFormView    →  Skin type, concerns, sensitivity
    │   ├── PhotoUploadView     →  3-photo capture + API upload
    │   ├── SkinAnalysisView    →  AI metric results
    │   ├── RoutinePlanView     →  AM/PM/weekly routine
    │   └── ChatView            →  AI skincare guidance
    └── Tab 2: AccountView
        ├── EditProfileView     (sheet)
        ├── FullHistoryView     (push)
        └── HistoryDetailView   (push)
```

### Networking Layer

`APIService` is a singleton that handles all backend communication:

- **Timeouts:** 120s request / 180s resource (AI analysis is slow).
- **Image compression:** Max 1024px dimension, 70% JPEG quality.
- **Upload format:** Multipart form data (front, left, right images + concerns JSON).
- **Date decoding:** ISO 8601 with optional fractional seconds.
- **DTO pattern:** API responses are decoded into `*DTO` structs, then converted to domain models via `.toDomain()` extensions.
- **Error handling:** HTTP 422 is treated as a retake-required response with specific reasons.

### Design System

Defined in `Theme.swift`:

| Token | Values |
|-------|--------|
| **DLColor** | `.primaryFallback` (blue), `.secondaryFallback` (teal), `.accentFallback` (amber), `.surfaceFallback` (light gray) |
| **DLFont** | `.largeTitle` (28pt bold rounded) through `.small` (11pt medium) |
| **DLSpacing** | `.xs` (4) `.sm` (8) `.md` (16) `.lg` (24) `.xl` (32) `.xxl` (48) |
| **DLRadius** | `.sm` (8) `.md` (12) `.lg` (16) `.xl` (24) `.full` (999) |

### Dashboard Reset Flow

The reset button (`arrow.counterclockwise`) in the Dashboard toolbar destroys and recreates all child views by changing a `flowId` UUID applied via `.id(flowId)` on the TabView. This forces SwiftUI to reset all `@State` in child views (form fields, selected photos, etc.) while preserving scan history in AppState.

### Demo Mode

The app currently runs in **demo mode**: `DermaLensApp.swift` clears the saved onboarding state on every launch, forcing the signup flow for presentation purposes. Remove the `.task { ... }` block in `DermaLensApp` to disable this.

---

## API Reference

Base URL: `http://<host>:8000/api/v1`

### Users

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/users/profile?email={email}` | Get profile (auto-creates if missing) |
| `PUT` | `/users/profile?email={email}` | Update profile fields |

### Scans

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/scans/upload?email={email}` | Upload 3 photos + concerns, run AI pipeline |
| `GET` | `/scans/{scanId}?email={email}` | Get scan analysis results |
| `GET` | `/scans/history/list?email={email}` | List all scans (summary records) |

### Routines

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/routines/{scanId}?email={email}` | Get routine for a specific scan |
| `GET` | `/routines/latest/plan?email={email}` | Get most recent routine |

### Chat

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/chat/message?email={email}` | Send message, receive AI response |
| `GET` | `/chat/history?email={email}&sessionId={id}` | Get chat history |

### Health Check

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Returns `{"status": "healthy", "version": "2.0.0"}` |

### Error Responses

| Status | Meaning |
|--------|---------|
| 400 | Invalid email, malformed JSON, missing parameters |
| 404 | Scan, routine, or profile not found |
| 422 | Image quality insufficient (retake required) |
| 500 | Server error (check `server.log`) |

---

## Data Flow

### Scan Upload (End-to-End)

```
iOS: ConcernsFormView
  └─ User fills skin type, concerns, sensitivity
  └─ Passes SkinConcernsForm to DashboardView

iOS: PhotoUploadView
  └─ User selects 3 photos (front, left 90deg, right 90deg)
  └─ Photos compressed (1024px max, 70% JPEG)
  └─ POST /scans/upload (multipart: front, left, right, concerns JSON)

Backend: scans.py route handler
  └─ Uploads images to S3
  └─ Calls ai_pipeline.run_ai()
      ├─ Gemini Vision: analyzes images → SkinMetrics
      ├─ Validator: checks confidence >= 45%, retake flag
      │   └─ If retake needed: returns HTTP 422
      ├─ Scoring: builds skin profile from metrics + quiz
      ├─ Engine: generates AM/PM routine based on profile
      └─ Returns: analysis + routine + lock status
  └─ Stores analysis, routine, concerns, metrics to S3
  └─ Returns SkinScanSchema

iOS: SkinAnalysisView
  └─ Displays overall score (animated ring) + metric grid

iOS: RoutinePlanView (fetched via GET /routines/{scanId})
  └─ Displays morning/evening/weekly steps with timeline

iOS: ChatView
  └─ POST /chat/message with session context
  └─ Backend injects latest scan + routine + concerns into Gemini prompt
  └─ Returns AI response
```

### Metric Scoring

Each metric is scored 0-100 (higher = more severe):

| Metric | Icon | Color Ranges |
|--------|------|-------------|
| Acne | `circle.fill` | 0-25 green, 26-50 yellow, 51-75 orange, 76-100 red |
| Redness | `flame.fill` | Same |
| Oiliness | `drop.fill` | Same |
| Dryness | `sun.max.fill` | Same |
| Texture | `square.grid.3x3.fill` | Same |

**Overall Score** = `100 - average(all metrics)` (higher is better).

---

## Deployment

### EC2 Production Setup

The backend runs on an AWS EC2 instance (`t3.micro`, `us-east-1`).

**1. SSH into the instance:**

```bash
ssh -i dermalens-key.pem ec2-user@<public-ip>
```

**2. Export environment variables:**

```bash
export AWS_ACCESS_KEY_ID="..."
export AWS_SECRET_ACCESS_KEY="..."
export AWS_REGION="us-east-1"
export S3_BUCKET_NAME="dermalens-bucket"
export GEMINI_API_KEY="..."
export GEMINI_MODEL="gemini-2.5-flash"
```

**3. Start the server (persistent):**

```bash
cd ~/dermalens
source venv/bin/activate
nohup python -m backend.main > server.log 2>&1 &
```

**4. Verify:**

```bash
curl http://localhost:8000/health
```

### Updating the iOS Base URL

In `Services/APIService.swift`, update `baseURL` to point to the EC2 public IP:

```swift
self.baseURL = "http://<ec2-public-ip>:8000/api/v1"
```

In `Info.plist`, add an ATS exception for the EC2 IP under `NSAppTransportSecurity > NSExceptionDomains`.

### EC2 Security Group

Ensure the security group allows inbound traffic on port 8000:

| Type | Protocol | Port | Source |
|------|----------|------|--------|
| Custom TCP | TCP | 8000 | 0.0.0.0/0 |
| SSH | TCP | 22 | Your IP |

### Restarting After SSH Disconnect

The `nohup` command keeps the server running after SSH disconnect. To restart:

```bash
kill -9 $(lsof -t -i:8000)    # Kill existing process
nohup python -m backend.main > server.log 2>&1 &
```

---

## Troubleshooting

### Backend

| Issue | Solution |
|-------|----------|
| `Address already in use` | Kill existing process: `kill -9 $(lsof -t -i:8000)` |
| `NoSuchBucket` | Verify `S3_BUCKET_NAME` env var is exported before starting server |
| `Connection refused` on EC2 | Check security group allows port 8000; verify server is running with `ps aux \| grep python` |
| 500 on scan upload | Check `server.log` for stack trace; most common cause is missing env vars |
| `GEMINI_API_KEY` errors | Ensure the key is exported in the same shell session as the server |

### iOS

| Issue | Solution |
|-------|----------|
| Network error on physical device | `localhost` resolves to the phone itself. Use EC2 IP or Mac's LAN IP in `APIService.swift` |
| `The request timed out` | EC2 may be unreachable. Verify with `curl http://<ip>:8000/health` from your machine |
| Build error: `.quaternary` not a Color | Use `Color.secondary.opacity(0.4)` instead; `.quaternary` is a `ShapeStyle`, not `Color` |
| Child view state not resetting | Ensure `.id(flowId)` is applied to the TabView in `DashboardView` |
| `@EnvironmentObject` crash | This project uses `@Observable` + `@Environment(Type.self)`, not `ObservableObject` + `@EnvironmentObject` |
| Image overflow in PhotoUploadView | Images use `GeometryReader` with explicit frame + `.clipped()` to prevent overflow |

---

## Dependencies

### Backend (requirements.txt)

| Package | Version | Purpose |
|---------|---------|---------|
| fastapi | 0.109.0 | Web framework |
| uvicorn | 0.27.0 | ASGI server |
| python-multipart | 0.0.6 | File upload handling |
| pydantic | 2.5.3 | Data validation |
| pydantic-settings | 2.1.0 | Environment config |
| boto3 | 1.34.34 | AWS S3 SDK |
| google-genai | >= 1.0.0 | Gemini AI SDK |
| Pillow | >= 11.0.0 | Image processing |
| python-dotenv | 1.0.1 | .env file loading |

### iOS

No third-party dependencies. The app uses only Apple frameworks:

- **SwiftUI** -- UI framework
- **PhotosUI** -- Image picker
- **Observation** -- State management (`@Observable`)
- **Foundation** -- Networking (`URLSession`), JSON (`JSONDecoder`)
