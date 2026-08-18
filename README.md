# AI Travel Planner 🌍✈️

An intelligent, full-stack **AI Travel Planner** web application designed to craft personalized trip itineraries, recommend destinations, estimate travel budgets, plan routes, and dynamically re-plan trips.

---

## 🚀 Streamlit Community Cloud Deployment Instructions

### 1. Push to GitHub
```bash
git remote add origin https://github.com/<YOUR_GITHUB_USERNAME>/ai-travel-planner.git
git branch -M main
git push -u origin main
```

### 2. Deploy on Streamlit Cloud
1. Sign in to [share.streamlit.io](https://share.streamlit.io) using your GitHub account.
2. Click **New App** and select your repository `ai-travel-planner`.
3. Set **Main file path** to `app.py`.
4. (Optional) Add `GEMINI_API_KEY` under **Advanced Settings -> Secrets**.
5. Click **Deploy!** Your app will be live at:
   `https://<YOUR_GITHUB_USERNAME>-ai-travel-planner.streamlit.app`

---

## 🌟 Key Features & Highlights

- **100% Zero External API Keys Needed**: Built to run locally using custom algorithmic tools, local SQLite data, and local LLM/RAG abstractions.
- **Modern Security Architecture**: Argon2 password hashing (`pwdlib`), JWT token authentication, email verification, and password reset capability.
- **Local Development Email Service**: Captures and logs all verification and password reset emails locally to `data/dev_emails.log` without requiring external SMTP or paid email API services.
- **Pastel UI Aesthetic**: Clean, modern, calm pastel theme (soft cream, blush pink, lavender, peach, and sage accents).
- **Smart Itinerary Generator**: Day-by-day customized travel plans matching your budget, pace, and interests.
- **Dynamic Replanning**: Agentic capabilities to adjust existing itineraries (e.g., "Make it cheaper", "Remove museums").
- **Budget & Distance Calculators**: Accurate local mathematical models for intercity and intracity trip expenses.
- **Local Travel Knowledge Base**: Curated database of destinations, attractions, local cuisines, accommodations, and transit modes.

---

## 🔐 Authentication & Email Verification Architecture (Phase 4)

> [!NOTE]
> **Local Email Mechanism**: Production email delivery APIs (SendGrid/Mailgun/SES) are **not required**. During development, verification links and reset links are formatted and automatically logged to `data/dev_emails.log` and standard output.

### 1. User Registration & Email Verification Flow
1. User registers at `/register` with name, email, and password.
2. Password is hashed using **Argon2** via `pwdlib`.
3. Account is created with `is_verified = False` and a 24-hour verification token.
4. Local dev email logger writes verification link `http://127.0.0.1:8000/auth/verify-email?token=<token>` to `data/dev_emails.log`.
5. User accesses verification link -> Account becomes verified (`is_verified = True`) and token is invalidated.
6. **Login Enforcement**: Unverified users are blocked at login with `HTTP 403 Forbidden` until verified.

### 2. Password Reset Flow
1. User requests password reset at `/forgot-password` or `POST /auth/forgot-password`.
2. System returns a generic success message (preventing email enumeration).
3. If account exists, a 1-hour reset token is generated and logged to `data/dev_emails.log` with link `http://127.0.0.1:8000/reset-password?token=<token>`.
4. User opens reset page, enters new password -> Password is re-hashed via Argon2 and reset token is destroyed.

---

## 🏗️ Technical Stack

- **Backend**: FastAPI (Python 3.10+)
- **Security & Hashing**: `pwdlib[argon2]`, `PyJWT` (HS256 algorithm)
- **Database**: SQLite with SQLAlchemy ORM (`data/travel_planner.db`)
- **Frontend**: HTML5, CSS3 (Soft Pastel Theme), Vanilla JavaScript, Jinja2 Templates
- **AI / Agentic Layer**: Clean Python LLM/RAG abstraction layer for local open-source LLMs & vector search

---

## 📁 Project Architecture

```text
AI_TRAVEL_PLANNER/
│
├── app/
│   ├── main.py              # FastAPI app entry point & routes
│   │
│   ├── core/                # Core settings, security, email & dependencies
│   │   ├── config.py
│   │   ├── security.py      # Argon2 & PyJWT helpers
│   │   ├── email.py         # Local dev email logger (data/dev_emails.log)
│   │   └── dependencies.py  # OAuth2 Bearer token auth dependency
│   │
│   ├── database/            # Database configuration, models & seeds
│   │   ├── database.py      # SQLite connection & safe schema migration
│   │   ├── models.py        # SQLAlchemy User, Destination, Place, Stay, etc.
│   │   └── seed.py
│   │
│   ├── auth/                # Authentication router & service
│   │   ├── router.py        # /register, /login, /verify-email, /forgot-password, etc.
│   │   ├── schemas.py       # Pydantic auth schemas
│   │   └── service.py       # Auth, verification & password reset logic
│   │
│   ├── travel/              # Destination & travel discovery engine
│   │   ├── router.py
│   │   ├── schemas.py
│   │   └── service.py
│   │
│   ├── ai/                  # Local AI, tools, RAG & agent layer
│   │   ├── agent.py
│   │   ├── tools.py
│   │   ├── rag.py
│   │   └── llm.py
│   │
│   └── trips/               # Itineraries, saved trips & replanning
│       ├── router.py
│       ├── schemas.py
│       └── service.py
│
├── templates/               # Pastel HTML Jinja2 UI templates
│   ├── index.html
│   ├── register.html
│   ├── login.html
│   ├── verify_email.html
│   ├── forgot_password.html
│   ├── reset_password.html
│   └── profile.html
│
├── static/                  # Static assets (CSS, JS, media)
│   ├── css/style.css        # Soft pastel theme design system
│   ├── js/auth.js           # Client-side JWT auth & form handlers
│   └── images/
│
├── data/                    # Local storage & dev email logs
│   ├── travel_planner.db    # SQLite database
│   └── dev_emails.log       # Local development email log
│
├── tests/                   # Pytest test suites (22 passed tests)
│   ├── test_main.py
│   ├── test_database.py
│   ├── test_auth.py
│   ├── test_email_verification.py
│   └── test_password_reset.py
│
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10 or higher
- `pip` (Python package manager)

### Installation & Execution

1. **Clone or navigate to the repository**:
   ```bash
   cd AI_TRAVEL_PLANNER
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Setup**:
   Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

4. **Run the FastAPI Development Server**:
   ```bash
   python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
   ```

5. **Access Application**:
   - Web UI: [http://127.0.0.1:8000](http://127.0.0.1:8000)
   - Interactive API Docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
   - Database Status: [http://127.0.0.1:8000/database-status](http://127.0.0.1:8000/database-status)

6. **Run Test Suites**:
   ```bash
   python -m pytest tests/
   ```

---

## 🛠️ Phased Implementation Roadmap

- [x] **Phase 1**: Project Setup + FastAPI Web Foundation
- [x] **Phase 2**: SQLite + SQLAlchemy Database Models & Pastel UI
- [x] **Phase 3**: User Registration, Argon2 Hashing & JWT Authentication
- [x] **Phase 4**: Email Verification & Password Reset (Local Dev Mechanism)
- [ ] **Phase 5**: Main Travel UI Framework
- [ ] **Phase 6**: Travel Database & Seed Exploration
- [ ] **Phase 7**: Local GenAI Integration
- [ ] **Phase 8**: Local RAG Knowledge Engine
- [ ] **Phase 9**: Agentic AI Tools Infrastructure
- [ ] **Phase 10**: Smart Itinerary Generator & Trip Replanner

---

## 📄 License

MIT License. Designed and built with ❤️ as a self-contained AI Travel Companion.
