<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0b5d63&height=220&section=header&text=EchoMind&fontSize=70&fontColor=ffffff&animation=fadeIn&fontAlignY=38&desc=Memory-First%20Audience%20Intelligence%20Agent&descFontSize=22&descFontColor=e6f1f1&descAlignY=62" width="100%"/>

[![Typing SVG](https://readme-typing-svg.demolab.com?font=Fira+Code&size=18&pause=1000&color=0B5D63&center=true&vCenter=true&width=600&lines=An+AI+that+remembers+what+your+audience+responds+to;Learn+%E2%86%92+Remember+%E2%86%92+Recall+%E2%86%92+Recommend;Dual-Persistence%3A+SQLite+Audit+%2B+Hindsight+AI;FastAPI+%2B+SQLAlchemy+%2B+Bcrypt+%2B+JWT)](https://git.io/typing-svg)

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/FastAPI-0.141.1-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI" />
  <img src="https://img.shields.io/badge/SQLite3-Relational%20DB-003B57?style=for-the-badge&logo=sqlite&logoColor=white" alt="SQLite" />
  <img src="https://img.shields.io/badge/SQLAlchemy-ORM%20Layer-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white" alt="SQLAlchemy" />
  <img src="https://img.shields.io/badge/Hindsight-AI%20Memory-7928CA?style=for-the-badge&logo=openai&logoColor=white" alt="Hindsight AI" />
  <img src="https://img.shields.io/badge/JWT-Stateless%20Auth-000000?style=for-the-badge&logo=jsonwebtokens&logoColor=white" alt="JWT" />
</p>

---

</div>

## 📌 Executive Overview

**Brands don't have a memory of their audience. EchoMind gives them one.**

**EchoMind** is a memory-first social intelligence platform that learns from historical social media interactions and content performance data, remembers what an audience responds to, and uses that persistent memory to generate actionable, platform-aware recommendations.

Instead of treating every content decision in isolation, EchoMind maintains continuous institutional memory:
- **What worked** (proven formats, high engagement triggers)
- **What flopped** (content styles to actively avoid)
- **What the audience repeatedly asks for** (requested tutorials, questions)

---

## 💡 The Core Memory Loop

A conventional content tool generates advice from generic prompts. EchoMind operates on a closed-loop intelligence architecture:

```text
       Audience Experience
                ↓
         Hindsight Retain
                ↓
         Hindsight Recall
                ↓
        Hindsight Reflect
                ↓
  Audience-Aware Recommendation
                ↓
    Execute New Experience
                ↓
        Learn Again (Memory)
```

---

## 🏛️ System Architecture

EchoMind utilizes a **two-tier data layer**:
1. **SQLite Application Database:** Authoritative, inspectable local relational store for user identities, bcrypt-secured authentication, user profiles, and an activity audit log.
2. **Hindsight AI Memory Layer:** Managed AI semantic vector memory and reasoning engine for long-term recall, retention, and reflection.

```text
                       ┌─────────────────────────┐
                       │   EchoMind Web Client   │
                       │   Vanilla HTML5/CSS/JS  │
                       └────────────┬────────────┘
                                    │ HTTP REST + JWT
                                    ▼
                       ┌─────────────────────────┐
                       │   FastAPI Backend       │
                       │   JWT Middleware & ORM  │
                       └─────┬─────────────┬─────┘
                             │             │
              SQLAlchemy ORM │             │ Native Async SDK
                             ▼             ▼
       ┌────────────────────────┐       ┌────────────────────────┐
       │   SQLite Application   │       │   Hindsight AI Memory  │
       │   Database (Local)     │       │   (Cloud Service)      │
       ├────────────────────────┤       ├────────────────────────┤
       │ • users                │       │ • aretain              │
       │ • memory_logs          │       │ • arecall              │
       │ • user profiles        │       │ • areflect             │
       │ • audit trails         │       │ • persistent banks     │
       └────────────────────────┘       └────────────────────────┘
```

### End-to-End Dual-Persistence Data Flow (`POST /learn`)

When a user teaches an audience experience to EchoMind:

```text
User Submits Experience
          ↓
  Frontend (fetch)
          ↓ [Bearer JWT + JSON]
    POST /learn
          ↓
   FastAPI Server
   ├──→ 1. Hindsight AI Memory Layer
   │        └── aretain(bank_id, content, context) ──→ External Semantic Store
   │
   └──→ 2. SQLite Application Layer
            └── INSERT INTO memory_logs (user_id, content, platform, bank)
          ↓
  JSON Response 200 OK
          ↓
  Frontend Updates UI & Profile Audit Stream
```

---

## ✨ Features

| Feature | Description | Architecture Layer |
|---|---|---|
| 🧠 **Persistent Audience Memory** | Retains social performance experiences across sessions | Hindsight Vector Store |
| 🔍 **Semantic Memory Recall** | Retrieves relevant memories for specific strategic questions | Hindsight Recall |
| 💭 **Evidence-Based Recommendations** | Generates recommendations with explicit evidence citations | Hindsight Reflect |
| 🔒 **JWT Authentication** | Stateless token auth (`HS256`, 24h expiration) | Python-Jose |
| 🛡️ **Bcrypt Security** | Cryptographically salted password hashing | Direct Bcrypt |
| 👤 **User Profiles & Persistence** | Editable user name, bio, and avatar | SQLite `users` Table |
| 📜 **Memory Audit Logs** | Per-user chronological audit trail of all taught experiences | SQLite `memory_logs` Table |
| 🎯 **Multi-Platform Support** | Platform-specific intelligence for LinkedIn, Instagram, YouTube, X | FastAPI + Prompt Engine |
| ⚡ **Live Status Monitoring** | Real-time connectivity checks against the Hindsight memory bank | FastAPI `/api/status` |
| 🛡️ **Security Headers & XSS Guard** | Strict CSP, X-Frame-Options, input length limits, HTML sanitization | FastAPI Middleware |

---

## 🗄️ Database Schema (SQLite)

The database (`echomind.db`) is automatically provisioned via SQLAlchemy ORM on FastAPI startup:

### `users`
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique user identifier |
| `name` | VARCHAR(100) | NOT NULL | User's full name |
| `email` | VARCHAR(255) | UNIQUE, NOT NULL, INDEX | Login email address |
| `password_hash` | VARCHAR(255) | NOT NULL | Bcrypt password hash |
| `bio` | TEXT | DEFAULT "" | User bio/description |
| `profile_image` | VARCHAR(500) | DEFAULT "" | Profile avatar image URL |
| `created_at` | DATETIME | DEFAULT UTC NOW | Registration timestamp |
| `updated_at` | DATETIME | DEFAULT UTC NOW | Last profile update timestamp |

### `memory_logs`
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique log entry ID |
| `user_id` | INTEGER | FOREIGN KEY (`users.id`), NOT NULL | Owning user ID |
| `content` | TEXT | NOT NULL | Experience text content |
| `platform` | VARCHAR(50) | DEFAULT "general" | Social platform |
| `hindsight_bank` | VARCHAR(100) | DEFAULT "social-audience" | Target Hindsight bank |
| `created_at` | DATETIME | DEFAULT UTC NOW | Logged timestamp |

```text
Relationship: users.id  ──(1 : N)──>  memory_logs.user_id
```

---

## 🔌 API Endpoints Reference

### Public & Core EchoMind Routes
- `GET /` — Serves the main Single-Page Application dashboard.
- `GET /signin` — Serves the dedicated Sign In page.
- `GET /signup` — Serves the dedicated Sign Up page.
- `GET /health` — Health check liveness probe (`{"status":"healthy"}`).
- `GET /api/status` — Live connectivity check against the active Hindsight memory bank.
- `GET /memory` (alias `/api/memory`) — Semantically queries and recalls retained audience memories.
- `POST /learn` (alias `/api/learn`) — Dual-persistence endpoint: stores experience in Hindsight AI and writes to SQLite `memory_logs` if authenticated.
- `GET /recommendation` (alias `/api/recommendation`) — Reflected AI reasoning yielding practical next-post recommendations.
- `POST /api/demo/seed` — Seeds 4 curated social experiences for rapid demonstration.

### Authentication Routes
- `POST /auth/signup` — Registers a new user, hashes password, inserts into SQLite, and returns JWT.
- `POST /auth/signin` — Verifies bcrypt credentials, issues JWT access token.
- `POST /auth/logout` — Client-side token revocation confirmation.

### User Profile & Audit Routes (`Authorization: Bearer <JWT>` Required)
- `GET /users/me` — Fetches authenticated user's profile from SQLite.
- `PUT /users/me` — Updates user name, bio, and avatar in SQLite.
- `GET /users/me/memories` — Retrieves chronological SQLite audit logs for the authenticated user.

---

## 🧪 Verified Browser QA & Test Results

The application underwent rigorous end-to-end browser QA using headless Chromium:

| Verification Metric | Result | Detail |
|---|---|---|
| **E2E Journey Steps** | **28 / 28 Passed** | Complete flow: Register → Sign In → Edit Profile → Refresh → Teach → Audit → Recall → Recommend → Logout |
| **Monitored Browser Requests** | **29 Requests** | Inspected via DevTools network interceptor |
| **Authenticated JWT Requests** | **17 Requests** | Correct `Authorization: Bearer <token>` transmission |
| **Console Errors** | **0 Errors** | Zero uncaught JavaScript errors or runtime exceptions |
| **Page Errors** | **0 Errors** | Zero unhandled DOM or template exceptions |
| **CORS Errors** | **0 Errors** | Same-origin architecture with zero cross-origin failures |
| **HTTP 404 / 500 Errors** | **0 Errors** | All valid API calls returned HTTP 200 / 201 |
| **Database Persistence** | **Verified** | Profile edits and memory logs verified in SQLite across reboots |
| **Hindsight AI Integration** | **Verified** | Live `aretain`, `arecall`, and `areflect` calls confirmed |
| **Responsive Viewports** | **Verified** | Tested across Desktop (1280px), Tablet (768px), and Mobile (375px) |

---

## 📁 Repository Structure

```text
EchoMindv2/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application, route controllers & security middleware
│   ├── database.py             # SQLite engine, session factory, get_db dependency
│   ├── models.py               # User and MemoryLog SQLAlchemy ORM models
│   ├── auth.py                 # Bcrypt hashing & python-jose JWT utilities
│   ├── hindsight_service.py    # Native async Hindsight SDK service layer
│   └── routers/
│       ├── __init__.py
│       ├── auth.py             # /auth/signup, /auth/signin, /auth/logout
│       └── users.py            # /users/me, /users/me/memories
├── static/
│   ├── index.html              # Main SPA dashboard & Profile/Audit tab
│   ├── signin.html             # Dedicated Sign In view
│   └── signup.html             # Dedicated Sign Up view
├── docs/
│   └── article.md              # In-depth architectural writeup
├── requirements.txt            # Python dependencies
├── render.yaml                 # Cloud deployment configuration
├── .gitignore                  # Exclusion rules for secrets, DBs, and venvs
├── .env.example                # Template for environment configuration
└── README.md                   # Project documentation
```

---

## ⚙️ Local Setup & Quickstart

### 1. Clone the Repository
```bash
git clone https://github.com/saivarun-04/EchoMindv2.git
cd EchoMindv2
```

### 2. Set Up Virtual Environment
```bash
python -m venv .venv
```
- **Windows:** `.venv\Scripts\activate`
- **macOS / Linux:** `source .venv/bin/activate`

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Fill in your credentials:
```env
HINDSIGHT_API_KEY=your_hindsight_api_key
HINDSIGHT_BASE_URL=https://api.hindsight.vectorize.io
HINDSIGHT_BANK_ID=social-audience
JWT_SECRET_KEY=your_secure_random_secret
```

### 5. Run the Application
```bash
python -m uvicorn app.main:app --reload
```
Navigate to: **`http://127.0.0.1:8000`**

---

## 🎤 Recommended 5–10 Minute Presentation Demo Flow

Follow this structured sequence to demonstrate **Frontend ↔ Backend ↔ SQLite ↔ Hindsight**:

1. **Problem & Positioning (1 min):** Explain why standard AI generators fail without persistent audience memory.
2. **Architecture Map (1 min):** Show the 2-tier data design (SQLite for identities/audit, Hindsight for AI memory).
3. **Registration & JWT (1 min):** Open `/signup`, register a test account, and show the JWT returned in DevTools Network tab.
4. **Profile & SQLite Persistence (2 mins):** 
   - Switch to the "User Profile" tab.
   - Edit the Name and Bio, save changes.
   - Refresh the page (`Ctrl+F5`) to demonstrate real SQLite database persistence.
5. **Dual-Persistence Teach Action (2 mins):**
   - Teach an audience experience: *"Our LinkedIn post comparing pandas vs polars got 4x comments."*
   - Show that it is retained into Hindsight AI memory while simultaneously appearing in the SQLite Memory Audit Log.
6. **Recall & AI Recommendation (2 mins):**
   - Click "Recall memory" to demonstrate Hindsight semantic search.
   - Click "Recommend next post" on LinkedIn to show evidence-backed reasoning.
7. **Sign Out (1 min):** Click "Sign Out" to verify client token cleanup and auth protection.

---

## 👥 Engineering Team

| Name | Role |
|---|---|
| **Sai Varun Gotteparthi** | Team Lead (TL) |
| **Karanam Poorna Chandra Rayudu** | Team Member |
| **Ch Likith Gandhi** | Team Member |
| **K Siddish** | Team Member |
| **Nelluri Karthikeya** | Team Member |
| **Abinay Karthik Varma** | Team Member |

---

<div align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=0b5d63&height=120&section=footer" width="100%"/>
</div>
