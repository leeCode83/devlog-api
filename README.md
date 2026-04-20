# DevLog API

Developer Activity Logging & Analytics Service. RESTful API untuk mencatat, melacak, dan menganalisis aktivitas pengembangan sehari-hari.

## Tech Stack

| Komponen | Teknologi |
|---|---|
| Framework | FastAPI (Python 3.12) |
| Database | Supabase PostgreSQL |
| Auth | Supabase Auth |
| Cache | Redis |
| Server | Gunicorn + Uvicorn workers |

## Prerequisites

- Python 3.12+
- Docker & Docker Compose
- Supabase CLI (untuk migrate)
- Akun Supabase Cloud

## Quick Start

### 1. Clone & Install Dependencies

```bash
cd devlog-api
pip install -r requirements.txt
```

### 2. Environment Setup

Copy `env.example` ke `.env` dan isi nilai yang diperlukan:

```bash
cp env.example .env
```

Edit `.env` dengan kredensial Supabase kamu:

```env
APP_NAME=DevLog API
APP_VERSION=1.0.0
DEBUG=false

# ── Redis ─────────────────────────────────────────────────────
REDIS_URL=redis://localhost:6379/0

# ── Supabase ─────────────────────────────────────────────────
# Dari Supabase Dashboard → Settings → API
SUPABASE_URL=https://your-project-ref.supabase.co
SUPABASE_KEY=your-supabase-key

# ── Gunicorn ───────────────────────────────────────────────────
GUNICORN_WORKERS=4

# ── Rate Limiting ─────────────────────────────────────────────
RATE_LIMIT_GENERAL=100
RATE_LIMIT_ANALYTICS=20
RATE_LIMIT_WINDOW=60
```

### 3. Database Migrations

Pastikan tables dan RLS policies sudah ter-create di Supabase Cloud:

```bash
supabase login
supabase link --project-ref <your-project-ref>
supabase db push
```

### 4. Run with Docker Compose

```bash
docker-compose up --build
```

API akan berjalan di `http://localhost:8000`

### 5. Run Locally (Development)

```bash
# Start Redis via Docker
docker run -d -p 6379:6379 redis:7-alpine

# Run FastAPI with hot reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API Documentation

Swagger UI tersedia di: `http://localhost:8000/docs`

## Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `APP_NAME` | No | DevLog API | Nama aplikasi |
| `APP_VERSION` | No | 1.0.0 | Version |
| `DEBUG` | No | false | Debug mode |
| `REDIS_URL` | Yes | redis://localhost:6379/0 | Redis connection URL |
| `SUPABASE_URL` | Yes | - | Supabase project URL |
| `SUPABASE_KEY` | Yes | - | Supabase publishable key |
| `GUNICORN_WORKERS` | No | 4 | Jumlah Gunicorn workers |
| `RATE_LIMIT_GENERAL` | No | 100 | Rate limit general endpoint (req/mnt) |
| `RATE_LIMIT_ANALYTICS` | No | 20 | Rate limit analytics endpoint (req/mnt) |
| `RATE_LIMIT_WINDOW` | No | 60 | Rate limit window (detik) |

## API Endpoints

### Health Check

```bash
GET /api/v1/health
```

### Authentication

Semua endpoint kecuali `/health` memerlukan header:
```
Authorization: Bearer <supabase_access_token>
```

### Projects

```bash
# List projects
GET /api/v1/projects

# Create project
POST /api/v1/projects
Content-Type: application/json

{
  "name": "My Project",
  "description": "Project description",
  "color": "#FF5733",
  "tech_stack": ["python", "fastapi"]
}

# Get project
GET /api/v1/projects/{id}

# Update project
PATCH /api/v1/projects/{id}
Content-Type: application/json

{
  "name": "Updated Name"
}

# Delete project (soft delete)
DELETE /api/v1/projects/{id}
```

### Log Entries

```bash
# List logs (cursor pagination)
GET /api/v1/logs?limit=20&cursor=<cursor>

# Create log
POST /api/v1/logs
Content-Type: application/json

{
  "project_id": "uuid",
  "activity_type": "coding",
  "description": "Working on feature X",
  "duration_minutes": 90,
  "tags": ["backend", "api"],
  "started_at": "2026-04-20T10:00:00Z"
}

# Get log
GET /api/v1/logs/{id}

# Update log
PATCH /api/v1/logs/{id}
Content-Type: application/json

{
  "duration_minutes": 120
}

# Delete log (soft delete)
DELETE /api/v1/logs/{id}
```

### Analytics

```bash
# Daily summary
GET /api/v1/analytics/daily?date=2026-04-20

# Weekly report
GET /api/v1/analytics/weekly?week=2026-W16

# Project stats
GET /api/v1/analytics/projects/{id}/stats?from=2026-04-01&to=2026-04-30
```

### GitHub Mappings

```bash
# List mappings
GET /api/v1/github-mappings

# Create mapping
POST /api/v1/github-mappings
Content-Type: application/json

{
  "project_id": "uuid",
  "repo_full_name": "username/repo-name",
  "webhook_secret": "your-webhook-secret"
}

# Delete mapping
DELETE /api/v1/github-mappings/{id}
```

### Webhook (GitHub)

```bash
# GitHub push event receiver
POST /api/v1/webhooks/github
X-Hub-Signature-256: sha256=<hmac-signature>
Content-Type: application/json

{
  "repository": {
    "full_name": "username/repo-name"
  },
  "commits": [
    {"id": "abc123"},
    {"id": "def456"}
  ]
}
```

## Activity Types

| Value | Description |
|---|---|
| `coding` | Writing code |
| `review` | Code review |
| `debugging` | Debugging issues |
| `documentation` | Writing docs |
| `meeting` | Meetings |
| `research` | Research |
| `deployment` | Deploying code |

## Response Format

### Success

```json
{
  "success": true,
  "data": { ... }
}
```

### Paginated List

```json
{
  "success": true,
  "data": [...],
  "meta": {
    "cursor": "encoded-cursor",
    "has_more": true,
    "count": 100
  }
}
```

### Error

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Input tidak valid",
    "details": { ... }
  }
}
```

## Database Schema

```
auth.users (built-in Supabase)
    │
    ├── projects ──────────────── log_entries
    │       │                         │
    │       └────── github_mappings ──┘
    │
    └── (via user_id foreign key)
```

### Tables

- **projects** — Grouping untuk log entries
- **log_entries** — Aktivitas harian developer
- **github_mappings** — Mapping repo GitHub ke project

## Row Level Security (RLS)

Semua tabel dilindungi dengan RLS. User hanya bisa akses data miliknya sendiri.

- SELECT: User hanya bisa read miliknya
- INSERT: User hanya bisa insert untuk dirinya sendiri
- UPDATE: User hanya bisa update miliknya
- DELETE: User hanya bisa delete miliknya

## Development

### Run Tests

```bash
pytest tests/ -v
```

### Run with Coverage

```bash
pytest tests/ --cov=app --cov-report=html
```

## License

MIT