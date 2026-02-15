# 🧴 DermaLens

AI-powered skincare analysis that turns a few selfies into personalized routines. Snap three photos, answer a quick skin quiz, and receive metric-level analysis with a morning, evening, and weekly plan — all in under a minute.

## ✨ Features

### Intelligent Skin Analysis
- [x] **Multi-Angle Scanning:** Upload front, left, and right photos for comprehensive coverage
- [x] **AI-Powered Metrics:** Gemini Vision scores acne, redness, oiliness, dryness, and texture (0-100)
- [x] **Overall Health Score:** Single composite score so you know where you stand at a glance
- [x] **Image Quality Validation:** Automatically flags blurry or unusable photos and prompts a retake

### Personalized Skincare Routines
- [x] **Morning, Evening & Weekly Plans:** Three-part routines tailored to your metrics and concerns
- [x] **Evidence-Based Ingredients:** Active ingredient selection backed by dermatological rules (BHA, AHA, niacinamide, ceramides)
- [x] **Safety-First Logic:** Ingredient conflict detection and frequency reduction for sensitive skin
- [x] **Plan Lock Policy:** Encourages sticking with a routine for at least two weeks before changes

### AI Skincare Chat
- [x] **Context-Aware Guidance:** The AI knows your latest scan, routine, and concerns
- [x] **Quick Action Chips:** One-tap prompts for common questions
- [x] **Session History:** Conversations persist and can be resumed
- [x] **Responsible Boundaries:** Recommends a dermatologist for serious concerns — never diagnoses

### Account & Progress Tracking
- [x] **Scan History:** Every analysis saved and accessible from your profile
- [x] **Score Trend Visualization:** Track skin health over time with a bar chart
- [x] **Detail Drill-Down:** Tap any past scan to see full metrics and summary
- [x] **Profile Management:** Edit name, username, and avatar

### Built for Demo
- [x] **Fresh Start on Launch:** App resets to the signup screen every run for live presentations
- [x] **One-Tap Flow Reset:** Restart the analysis workflow without losing scan history

## 🧩 Architecture

DermaLens is a full-stack application with a native iOS client and a stateless Python API. All persistence lives in AWS S3 — no database required.

```
┌─────────────────────────────┐
│         iOS Client          │
│  SwiftUI · Observation · S3 │
└──────────────┬──────────────┘
               │ REST (JSON + Multipart)
┌──────────────▼──────────────┐
│        FastAPI Server       │
│  Stateless · S3-backed      │
├──────┬──────────┬───────────┤
│Gemini│  Routine │    S3     │
│Vision│  Engine  │  Storage  │
└──────┴──────────┴───────────┘
```

### Source Files

**Backend** (`backend/`)
| File | Purpose |
|------|---------|
| `main.py` | FastAPI app entry point, CORS, health check |
| `api/v1/routes/users.py` | Profile auto-creation and updates |
| `api/v1/routes/scans.py` | Photo upload, AI pipeline trigger |
| `api/v1/routes/routines.py` | Routine retrieval by scan or latest |
| `api/v1/routes/chat.py` | AI chat with context injection |
| `services/ai_pipeline.py` | Orchestrates vision, scoring, and routine generation |
| `services/vision/gemini_vision_service.py` | Gemini structured output for skin metrics |
| `services/routine_engine/engine.py` | Rule-based AM/PM routine builder |
| `services/chat_ai/gemini_service.py` | Context-aware Gemini chat |
| `services/storage/s3_service.py` | S3 JSON and image operations |

**iOS** (`frontend/dermalense/dermalense/`)
| File | Purpose |
|------|---------|
| `DermaLensApp.swift` | App entry point, onboarding gate |
| `Models.swift` | All data models and `@Observable` AppState |
| `Theme.swift` | Design tokens (colors, spacing, typography, radii) |
| `Services/APIService.swift` | Singleton networking layer with DTO conversion |
| `Views/Dashboard/DashboardView.swift` | 5-step wizard with progressive disclosure |
| `Views/Dashboard/ConcernsFormView.swift` | Skin type, concerns, and sensitivity form |
| `Views/Dashboard/PhotoUploadView.swift` | 3-photo picker with compression and upload |
| `Views/Dashboard/SkinAnalysisView.swift` | Animated score ring and metric grid |
| `Views/Dashboard/RoutinePlanView.swift` | Timeline-style morning/evening/weekly steps |
| `Views/Dashboard/ChatView.swift` | AI chat with quick actions and typing indicator |
| `Views/Account/AccountView.swift` | Profile, stats, and scan history |

## 💻 Tech Stack

**iOS:** Swift, SwiftUI, Observation, PhotosUI, URLSession

**Backend:** Python, FastAPI, Pydantic, boto3, google-genai, Pillow

**Infrastructure:** AWS S3, AWS EC2 (t3.micro), Gemini 2.5 Flash

## 📦 Installation

### Requirements
- Xcode 26.1 or later
- iOS 26.1+ (simulator or physical device)
- Python 3.11+
- AWS S3 bucket
- Google Gemini API key

### Clone the repository

```bash
git clone https://github.com/compscibro/dermalens.git
cd dermalens
```

### Backend

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your AWS and Gemini credentials

# Start the server
python -m backend.main
```

API available at `http://localhost:8000` | Docs at `http://localhost:8000/api/v1/docs`

### iOS

Open the Xcode project and run:

```
frontend/dermalense/dermalense.xcodeproj
```

Select the **dermalense** scheme, choose a simulator (iPhone 17 Pro recommended), and press `Cmd + R`.

> **Note:** To run on a physical device, update the `baseURL` in `Services/APIService.swift` to your server's IP address and add an ATS exception in `Info.plist`.

## 🔑 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/users/profile?email={email}` | Get or auto-create user profile |
| `PUT` | `/users/profile?email={email}` | Update profile fields |
| `POST` | `/scans/upload?email={email}` | Upload 3 photos + concerns, run AI analysis |
| `GET` | `/scans/{scanId}?email={email}` | Get scan results |
| `GET` | `/scans/history/list?email={email}` | List all scans |
| `GET` | `/routines/{scanId}?email={email}` | Get routine for a scan |
| `GET` | `/routines/latest/plan?email={email}` | Get most recent routine |
| `POST` | `/chat/message?email={email}` | Send message, receive AI response |
| `GET` | `/chat/history?email={email}` | Get chat history |
| `GET` | `/health` | Health check |

All endpoints are prefixed with `/api/v1`.

## 🚦 Roadmap


**Next**
- [ ] HTTPS with a proper domain and SSL certificate
- [ ] User authentication (JWT or OAuth)
- [ ] Haptic feedback and sound effects throughout the app experience

**Coming Soon**
- [ ] **DermaLens Premium:** Unlimited AI chat access via paid subscription (free tier: 3 messages/day)
- [ ] Push notifications for routine reminders and weekly scan prompts
- [ ] Weekly streaks, milestone badges, and achievement sounds to reward consistency
- [ ] Progress photos side-by-side comparison

**Future Vision**
- [ ] **Brand Partnerships:** Curated, science-backed product recommendations with in-app purchase links from partnered brands
- [ ] Multi-user household support
- [ ] Product barcode scanning and ingredient lookup
- [ ] Integration with dermatologist referral services
- [ ] Android client

## 👥 Contributors

- [Mohammed Abdur Rahman](https://github.com/compscibro)
- John Lizama
- [Aahil Shaik](https://github.com/bizaahil)
- Terina Ishaqzai

## 📄 License

DermaLens is open-source and available under the **MIT License**.

See [LICENSE](LICENSE) for full details.
