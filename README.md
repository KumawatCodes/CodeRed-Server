<div align="center">

# ⚡ CodeRed Platform

### A real-time competitive coding platform — built with FastAPI, WebSockets, and AI-powered hints

[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-009688?style=flat&logo=fastapi)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat&logo=python)](https://python.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Neon_Cloud-4169E1?style=flat&logo=postgresql)](https://neon.tech)
[![Redis](https://img.shields.io/badge/Redis-7.x-DC382D?style=flat&logo=redis)](https://redis.io)
[![Azure](https://img.shields.io/badge/Azure_VM-Code_Execution-0078D4?style=flat&logo=microsoftazure)](https://azure.microsoft.com)

**[🌐 Live Demo](#-live-demo) · [📖 API Docs](#-api-documentation) · [🎬 Video Showcase](#-video-showcase) · [🚀 Getting Started](#-getting-started)**

</div>

---

## 📌 Table of Contents

- [Overview](#-overview)
- [Live Demo](#-live-demo)
- [Video Showcase](#-video-showcase)
- [Tech Stack](#-tech-stack)
- [System Architecture](#-system-architecture)
- [Database Schema](#-database-schema)
- [Project Structure](#-project-structure)
- [Core Features](#-core-features)
- [API Documentation](#-api-documentation)
- [Getting Started](#-getting-started)
- [Environment Variables](#-environment-variables)
- [Contributing](#-contributing)

---

## 🧠 Overview

CodeBattle is a full-stack competitive coding platform where users can solve algorithmic problems, compete in real-time 1v1 matches, and get AI-powered hints. Built on **FastAPI** with async PostgreSQL, Socket.IO-based matchmaking, and a sandboxed multi-language code execution engine running on Azure VM.

**Key highlights:**
- Real-time 1v1 matchmaking via WebSockets
- Multi-language code execution (Python, C++, Java, JS, and more) via Piston Engine
- JWT + Google OAuth2 authentication
- AI hint system powered by Gemini, Mistral, and HuggingFace via LangChain
- Image uploads for problems via Cloudinary

---

## 🌐 Live Demo

> 🚀 The platform is deployed and live. Try it out:

| Resource | Link |
|---|---|
| 🌍 Frontend App | `https://codered-client.vercel.app/` ← *paste your URL here* |
| 📡 Backend API Docs| `coming soon` ← *paste your API URL here* |

---

## 🎬 Video Showcase

> A walkthrough of the platform's core features — matchmaking, code submission, and AI hints.

**Google Drive**

```markdown
[![Watch Demo on Google Drive](https://via.placeholder.com/800x450?text=Click+to+Watch+Demo)](https://drive.google.com/file/d/YOUR_1YXx7Ctc8OtAtF_sioXX9FQHlQwPZfrlNFILE_ID/view)
```

This shows a thumbnail image that links to the Drive video when clicked — the best you can do with Drive on GitHub.

---

**👉 Current Demo Link:**

[![Watch Demo](https://img.shields.io/badge/▶_Watch_Demo-Google_Drive-4285F4?style=for-the-badge&logo=googledrive)](https://drive.google.com/file/d/1YXx7Ctc8OtAtF_sioXX9FQHlQwPZfrlN/view?usp=sharing)

> *(Replace the link above with your actual Google Drive share link)*

---

## 🛠 Tech Stack

### Backend Core
| Layer | Technology |
|---|---|
| Framework | FastAPI 0.104.1 |
| Language | Python 3.11 |
| ASGI Server | Uvicorn |
| ORM | SQLAlchemy 2.0 (async) |
| Migrations | Alembic |
| Validation | Pydantic v2 |

### Authentication
| Layer | Technology |
|---|---|
| Token Auth | JWT (python-jose) |
| OAuth2 | Google OAuth (Authlib) |
| Password Hashing | bcrypt + passlib |
| OTP | Email-based via `emails` library |

### Database & Cache
| Layer | Technology |
|---|---|
| Primary DB | PostgreSQL (Neon Cloud) |
| Async Driver | asyncpg |
| Cache / Queue | Redis 7.x |
| Pub/Sub | Redis pub/sub (matchmaking) |

### Real-time
| Layer | Technology |
|---|---|
| WebSockets | Socket.IO (python-socketio) |
| Transport | python-engineio |
| Matchmaking | Redis queue + WebSocket events |

### Code Execution
| Layer | Technology |
|---|---|
| Engine | Piston (self-hosted on Azure VM) |
| Infrastructure | Azure Virtual Machine |
| Background Jobs | Async workers (gevent) |

### AI / LLM
| Layer | Technology |
|---|---|
| Orchestration | LangChain + LangGraph |
| Models | Gemini (Google), Mistral, HuggingFace |
| Tracing | LangSmith |

### Storage
| Layer | Technology |
|---|---|
| Image Storage | Cloudinary |

---

## 🏗 System Architecture

> High-level overview of how the platform components connect.

```
┌─────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                         │
│                  Browser  ·  Mobile App                     │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTP / WebSocket
┌──────────────────────────▼──────────────────────────────────┐
│                    FASTAPI APPLICATION                       │
│   REST API v1 (auth, users, problems, submissions, friends)  │
│   REST API v2 (auths, code_execution, user)                  │
│   WebSocket Server (Socket.IO — matchmaking)                 │
└──────┬──────────┬─────────────────────┬──────────┬──────────┘
       │          │                     │          │
  ┌────▼───┐ ┌───▼──────┐     ┌────────▼──┐ ┌────▼───────┐
  │  Auth  │ │ Business │     │    Code   │ │   AI/LLM   │
  │Service │ │ Services │     │ Execution │ │  LangChain │
  │JWT/OTP │ │ Problems │     │  Service  │ │  Gemini    │
  │Google  │ │ Users    │     │           │ │  Mistral   │
  │OAuth   │ │ Friends  │     │           │ │  HuggingF. │
  └───┬────┘ └───┬──────┘     └─────┬─────┘ └────────────┘
      │          │                  │
  ┌───▼──────────▼──┐          ┌────▼──────────────────────┐
  │   DATA LAYER    │          │  CODE EXECUTION LAYER     │
  │  PostgreSQL     │          │  Azure Virtual Machine    │
  │  (Neon Cloud)   │          │  Piston Engine (sandbox)  │
  │  Redis Cache    │          │  Multi-language support   │
  │  Cloudinary     │          └───────────────────────────┘
  └─────────────────┘
```
![System Design](https://github.com/KumawatCodes/CodeRed-Server/blob/main/documents/System%20Design/system%20design.jpeg)
### Key Flows

**1. User Authentication**
```
Browser → FastAPI → [Email+OTP | Google OAuth] → JWT issued → Authenticated
```

**2. Code Submission & Execution**
```
User submits code → API v2 /code_execution → Package (code + test input)
→ Send to Piston API on Azure VM → Get output → Compare → Return result
```

**3. Real-time Matchmaking**
```
User requests match → WebSocket → Matchmaking Service
→ Redis pub/sub queue → Match found → Notify both users
```

**4. Problem Image Upload**
```
Admin uploads image → Cloudinary (store) → URL returned → Saved to PostgreSQL
```

---

## 🗄 Database Schema
![Database Schema](https://github.com/KumawatCodes/CodeRed-Server/blob/main/documents/migrations/database%20schema.jpeg)
> Core entities and their relationships.

### Users
| Column | Type | Notes |
|---|---|---|
| `id` | UUID | Primary Key |
| `username` | VARCHAR | Unique |
| `email` | VARCHAR | Unique |
| `hashed_password` | VARCHAR | bcrypt |
| `is_verified` | BOOLEAN | OTP verified |
| `auth_provider` | ENUM | `local`, `google` |
| `profile_image_url` | VARCHAR | Cloudinary URL |
| `created_at` | TIMESTAMP | Auto |
| `updated_at` | TIMESTAMP | Auto |

### Problems
| Column | Type | Notes |
|---|---|---|
| `id` | UUID | Primary Key |
| `title` | VARCHAR | |
| `slug` | VARCHAR | Unique URL slug |
| `description` | TEXT | Markdown body |
| `difficulty` | ENUM | `easy`, `medium`, `hard` |
| `image_url` | VARCHAR | Cloudinary URL |
| `created_by` | UUID | FK → Users |
| `created_at` | TIMESTAMP | Auto |

### Test Cases
| Column | Type | Notes |
|---|---|---|
| `id` | UUID | Primary Key |
| `problem_id` | UUID | FK → Problems |
| `input` | TEXT | |
| `expected_output` | TEXT | |
| `is_hidden` | BOOLEAN | Hidden from user |

### Submissions
| Column | Type | Notes |
|---|---|---|
| `id` | UUID | Primary Key |
| `user_id` | UUID | FK → Users |
| `problem_id` | UUID | FK → Problems |
| `language` | VARCHAR | e.g. `python`, `cpp` |
| `code` | TEXT | Submitted code |
| `status` | ENUM | `accepted`, `wrong_answer`, `tle`, `error` |
| `runtime_ms` | INTEGER | Execution time |
| `memory_kb` | INTEGER | Memory usage |
| `submitted_at` | TIMESTAMP | Auto |

### Matches (1v1)
| Column | Type | Notes |
|---|---|---|
| `id` | UUID | Primary Key |
| `player_one_id` | UUID | FK → Users |
| `player_two_id` | UUID | FK → Users |
| `problem_id` | UUID | FK → Problems |
| `winner_id` | UUID | FK → Users, nullable |
| `status` | ENUM | `pending`, `active`, `completed` |
| `started_at` | TIMESTAMP | |
| `ended_at` | TIMESTAMP | |

### Friends
| Column | Type | Notes |
|---|---|---|
| `id` | UUID | Primary Key |
| `requester_id` | UUID | FK → Users |
| `addressee_id` | UUID | FK → Users |
| `status` | ENUM | `pending`, `accepted`, `blocked` |
| `created_at` | TIMESTAMP | Auto |

### Entity Relationships
```
Users ──< Submissions >── Problems
Users ──< Friends >── Users
Users ──< Matches >── Problems
Problems ──< TestCases
```

---

## 📁 Project Structure

```
codebattle-backend/
├── app/
│   ├── api/
│   │   ├── v1/
│   │   │   └── endpoints/
│   │   │       ├── auth/          # Login, register, OTP, Google OAuth
│   │   │       ├── users/         # User profile, settings
│   │   │       ├── friends/       # Friend requests, list
│   │   │       ├── problem/       # Problem CRUD, image upload
│   │   │       └── submission/    # Submit code, history
│   │   └── v2/
│   │       └── endpoints/
│   │           ├── auths/         # v2 auth (refresh, logout)
│   │           ├── code_execution/ # Execute code via Piston
│   │           └── user/          # Extended user operations
│   │
│   ├── core/                      # Config, security, database setup
│   ├── models/                    # SQLAlchemy ORM models
│   ├── schemas/                   # Pydantic request/response schemas
│   ├── repositories/              # DB query layer (repository pattern)
│   ├── services/
│   │   ├── webSocket/
│   │   │   └── matchmaking/       # Socket.IO matchmaking logic
│   │   └── (email, cloudinary, AI services)
│   └── new_services/              # LangChain AI hint services
│
├── workers/                       # Background async workers
├── documents/                     # System design docs, DB diagrams
│   └── migrations/                # Alembic migration history
└── .venv/                         # Python virtual environment
```

---

## ✨ Core Features

### 🔐 Authentication
- Email registration with OTP verification
- Google OAuth2 sign-in (via Authlib)
- JWT access + refresh token flow
- Password hashing with bcrypt

### 📋 Problems
- Create, list, filter problems by difficulty
- Attach images via Cloudinary
- Hidden and visible test cases per problem

### 💻 Code Execution
- Submit code in Python, C++, Java, JavaScript, Go, and more
- Code runs in an isolated Piston sandbox on Azure VM
- Verdict: Accepted / Wrong Answer / TLE / Runtime Error
- Runtime and memory tracking per submission

### ⚔️ Real-time Matchmaking
- WebSocket-based 1v1 competitive matches
- Redis pub/sub queue for player pairing
- Live match state updates via Socket.IO events

### 🤖 AI Hints
- LangChain router selects the best model (Gemini / Mistral / HuggingFace)
- LangGraph workflow for multi-step reasoning
- LangSmith tracing for observability

### 👥 Social
- Friend requests and friend list
- User profiles with stats

---

## 📡 API Documentation

Once the server is running, interactive API docs are available at:

| Docs | URL |
|---|---|
| Swagger UI | `http://localhost:8000/docs` |
| ReDoc | `http://localhost:8000/redoc` |
| OpenAPI JSON | `http://localhost:8000/openapi.json` |

### Endpoint Summary

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/auth/register` | Register with email + OTP |
| `POST` | `/api/v1/auth/login` | Login, get JWT tokens |
| `POST` | `/api/v1/auth/google` | Google OAuth sign-in |
| `GET` | `/api/v1/users/me` | Get current user profile |
| `GET` | `/api/v1/problem/` | List all problems |
| `POST` | `/api/v1/problem/` | Create problem (admin) |
| `POST` | `/api/v1/submission/` | Submit code |
| `GET` | `/api/v1/submission/` | Submission history |
| `POST` | `/api/v1/friends/request` | Send friend request |
| `POST` | `/api/v2/code_execution/run` | Execute code via Piston |
| `WS` | `/ws/matchmaking` | WebSocket matchmaking |

---

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- PostgreSQL (or Neon Cloud account)
- Redis server
- Cloudinary account
- Google OAuth credentials
- Piston API running (self-hosted on Azure VM or via public instance)

### Installation

```bash
# 1. Clone the repo
git clone https://github.com/your-username/codebattle-backend.git
cd codebattle-backend

# 2. Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Linux / Mac

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
# Fill in your values (see Environment Variables section)

# 5. Run database migrations
alembic upgrade head

# 6. Start the development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## 🔑 Environment Variables

Create a `.env` file in the root directory:

```env
# ── Database ──────────────────────────────────────
DATABASE_URL=postgresql+asyncpg://user:password@host/dbname
SYNC_DATABASE_URL=postgresql://user:password@host/dbname

# ── Redis ─────────────────────────────────────────
REDIS_URL=redis://localhost:6379

# ── JWT ───────────────────────────────────────────
SECRET_KEY=your_super_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# ── Google OAuth ──────────────────────────────────
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret

# ── Cloudinary ────────────────────────────────────
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret

# ── Email (OTP) ───────────────────────────────────
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password

# ── Piston (Code Execution) ───────────────────────
PISTON_API_URL=http://your-azure-vm-ip:2000

# ── AI / LLM ──────────────────────────────────────
GOOGLE_API_KEY=your_gemini_api_key
MISTRAL_API_KEY=your_mistral_api_key
HUGGINGFACEHUB_API_TOKEN=your_hf_token
LANGCHAIN_API_KEY=your_langsmith_key
LANGCHAIN_TRACING_V2=true
```

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit changes: `git commit -m "feat: add your feature"`
4. Push to branch: `git push origin feature/your-feature`
5. Open a Pull Request

---

<div align="center">

Built with ⚡ FastAPI · PostgreSQL · Redis · Azure · LangChain

</div>