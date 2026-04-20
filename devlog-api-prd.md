# PRODUCT REQUIREMENTS DOCUMENT
## DevLog API — Developer Activity Logging & Analytics Service

| Field             | Detail                              |
|-------------------|-------------------------------------|
| Versi             | v4.2.0                              |
| Status            | Draft — For Review                  |
| Author            | Ale (Backend Engineer)              |
| Tanggal           | April 2026                          |
| Sprint Duration   | 7 Hari                              |
| Target Concurrency| 200 Concurrent Users                |

---

## 1. Executive Summary

DevLog API adalah layanan RESTful backend yang memungkinkan developer individu untuk mencatat, melacak, dan menganalisis aktivitas pengembangan mereka secara terstruktur. Platform ini menerima log aktivitas coding harian, mengolahnya menjadi statistik yang actionable, dan mendukung integrasi otomatis dengan GitHub Webhooks.

Proyek ini dirancang sebagai solo-sprint 7 hari dengan fokus utama pada penguatan backend engineering patterns: clean architecture, dependency injection, async processing, caching strategy, dan skalabilitas sistem.

---

## 2. Latar Belakang & Problem Statement

### 2.1 Konteks

Developer sering kehilangan visibilitas atas pola kerja mereka sendiri. Pertanyaan seperti "kapan saya paling produktif?" atau "seberapa konsisten commit saya minggu ini?" tidak memiliki jawaban mudah tanpa alat logging yang terdedikasi. Tools yang ada seperti WakaTime bersifat proprietary dan mahal, sementara tidak ada referensi self-hostable yang ringan dan mudah di-extend.

### 2.2 Problem Statement

| Masalah | Dampak |
|---------|--------|
| Tidak ada cara mudah mencatat aktivitas coding secara structured | Data tersebar, tidak bisa dianalisis |
| Tidak ada insight tentang peak productivity hours | Developer tidak tahu waktu terbaik untuk deep work |
| Tracking manual di spreadsheet tidak scalable | Sering ditinggalkan karena terlalu lambat |
| Tidak ada korelasi commit frequency dengan jenis task | Sulit mengukur velocity secara objektif |

---

## 3. Tujuan & Sasaran

### 3.1 Tujuan Produk

- Menyediakan API yang dapat menerima log aktivitas dari developer, baik input manual maupun otomatis via GitHub Webhook
- Mengolah log menjadi statistik yang actionable: daily summary, weekly report, streak tracking
- Menjadi referensi arsitektur backend yang clean, scalable, dan maintainable

### 3.2 Tujuan Learning

| Skill Target | Level |
|---|---|
| Clean Architecture & Layering (Repository Pattern + Service Layer + DI) | Intermediate-Advanced |
| Async Programming (async ORM, async endpoint handlers, background tasks) | Intermediate |
| Database Design (schema relational, indexing strategy, constraints) | Intermediate |
| Supabase Integration (RLS policy, auth, database functions) | Intermediate |
| Caching Strategy (Redis, cache invalidation pattern) | Intermediate |
| Scalability Design (multi-worker, connection pooling, PgBouncer) | Intermediate |
| API Design (versioning, pagination, filtering, HTTP semantics) | Intermediate |
| Observability (structured logging, correlation ID, health check) | Beginner-Intermediate |
| Testing (unit per layer, integration test, coverage) | Intermediate |

---

## 4. Scope Proyek

### 4.1 In Scope

- User authentication via Supabase Auth — DevLog API handles sign up, sign in, sign out via Supabase Admin API
- Use Supabase `auth.users` table for user identity (no separate user_profiles table)
- CRUD untuk Project dan Log Entry dengan RLS policy
- Statistics & Analytics endpoint (daily, weekly, per-project)
- GitHub Webhook receiver untuk auto-log commit activity
- Database function dengan SECURITY DEFINER untuk webhook insert (bypass RLS untuk webhook saja)
- Rate limiting per user berbasis Redis
- API documentation auto-generated (Swagger UI)
- Docker Compose setup untuk local development
- Scalability configuration: multi-worker, Redis caching

### 4.2 Out of Scope

- Frontend / UI (pure API only)
- Team collaboration (multi-user per project)
- Real-time features (WebSocket, SSE)
- Billing atau subscription management
- Deployment ke cloud production
- Horizontal scaling / Kubernetes
- Export data (CSV/JSON)
- Service role key usage

---

## 5. User Personas

| Persona | Deskripsi | Kebutuhan Utama |
|---|---|---|
| Solo Developer (Primary) | Developer freelance yang ingin melacak produktivitas harian | API sederhana, dokumentasi jelas, mudah diintegrasikan |
| Mahasiswa CS (Secondary) | Mahasiswa yang ingin membangun portfolio dan belajar dari pola coding-nya | Lightweight, self-hostable, bisa diextend |
| Backend Engineer Learner | Engineer yang ingin mempelajari arsitektur backend modern sambil membangun sesuatu nyata | Clean architecture, best practices, bisa dijadikan referensi |

---

## 6. Functional Requirements

### 6.1 Authentication (via Supabase Admin API)

DevLog API menangani authentication secara penuh menggunakan Supabase Admin API. User dapat sign up, sign in, dan sign out melalui endpoint API. Tidak ada client-side Supabase Auth SDK yang digunakan.

**Sign Up:**
- User register dengan email + password
- DevLog API call `supabase.auth.admin.create_user()` untuk buat user baru
- User otomatis login dan dapat access token

**Sign In:**
- User login dengan email + password
- DevLog API call `supabase.auth.sign_in_with_password()` untuk verify credentials
- Return access token + refresh token jika sukses

**Sign Out:**
- Invalidate user session
- Return success response

User identity menggunakan tabel `auth.users` yang sudah ada di Supabase. Tidak perlu membuat tabel user tambahan.

### 6.2 Project Module

User dapat membuat, membaca, mengupdate, dan menghapus project miliknya. Project berfungsi sebagai grouping untuk log entries. Penghapusan bersifat soft delete agar data historis tetap terjaga.

RLS policy: user hanya bisa akses project yang dimiliki.

### 6.3 Log Entry Module

User dapat mencatat aktivitas pengembangan dengan detail: tipe aktivitas, durasi, project terkait, tag, dan waktu mulai. Waktu mulai boleh diisi retroactively. Tipe aktivitas yang didukung: coding, review, debugging, documentation, meeting, research, deployment.

Setiap kali log entry dibuat atau diupdate, cache analytics milik user tersebut otomatis diinvalidasi agar statistik selalu fresh.

RLS policy: user hanya bisa akses log entries miliknya.

### 6.4 Analytics Module

- **Daily Summary** — total durasi per tipe aktivitas, total entries, project paling aktif, dan peak hour untuk tanggal tertentu. Dihitung berdasarkan timezone user.
- **Weekly Report** — breakdown per hari, streak counter, dan heatmap data (7 hari x 24 jam) untuk visualisasi pola kerja.
- **Project Statistics** — total waktu, breakdown tipe aktivitas, dan weekly velocity trend untuk rentang tanggal tertentu.

Semua analytics di-cache di Redis dan diinvalidasi saat ada perubahan log.

### 6.5 GitHub Webhook Module

User mengkonfigurasi mapping antara repository GitHub dengan project di DevLog. Saat ada push event, GitHub mengirim payload ke API, sistem memverifikasi keasliannya via HMAC signature, lalu otomatis membuat log entry bertipe coding dengan estimasi durasi berdasarkan jumlah commit.

Insert log dari webhook menggunakan PostgreSQL function dengan SECURITY DEFINER — ini memungkinkan insert tanpa user context (karena webhook tidak punya access token Supabase).

---

## 7. Non-Functional Requirements

| Kategori | Requirement | Target |
|---|---|---|
| Performance | Response time endpoint CRUD | < 200ms p95 pada 200 concurrent users |
| Performance | Response time analytics (cache hit) | < 50ms p95 |
| Performance | Response time analytics (cache miss) | < 500ms p95 |
| Concurrency | Target concurrent users | 200 tanpa error rate > 1% |
| Scalability | Worker configuration | Gunicorn minimal 4 uvicorn workers |
| Scalability | DB connection | Via Supabase client |
| Security | Auth | Sign up/sign in/sign out via Supabase Admin API |
| Security | RLS | Semua query ke tabel wajib melalui RLS policy |
| Security | Webhook | HMAC-SHA256 signature wajib diverifikasi |
| Security | Webhook Insert | SECURITY DEFINER function (bukan service role key) |
| Security | SQL Injection | Parameterized queries via Supabase client |
| Reliability | Rate limiting | 100 req/menit per user, 20 req/menit untuk analytics |
| Maintainability | Test coverage | Minimum 70% unit + integration test |
| Maintainability | Architecture | Strict separation: Router → Service → Repository → DB |
| Observability | Logging | Structured JSON logging dengan correlation ID per request |

---

## 8. Tech Stack

| Komponen | Teknologi | Justifikasi |
|---|---|---|
| Runtime | Python 3.12 | Familiar dari Claimly, fokus ke pattern bukan syntax baru |
| Framework | FastAPI | Async-first, Dependency Injection eksplisit, Swagger auto-generated |
| Validation | Pydantic v2 | Validasi runtime + type inference sekaligus, core Rust (cepat) |
| Database | PostgreSQL via Supabase Cloud | Managed, familiar dari Claimly, tidak perlu maintenance server |
| ORM | Supabase Python Client (postgrest) | Async, langsung akses via RLS policy tanpa JWT verification manual |
| Migrations | Supabase Migrations CLI | Standard untuk Supabase project |
| Auth | Supabase Admin API | DevLog API handle sign up/sign in/sign out via Admin API |
| Cache & Rate Limit | Redis 7 + redis-py async | Analytics caching dan rate limiting per user |
| Testing | pytest + httpx + pytest-asyncio | Standar industri Python, httpx untuk async integration test |
| Logging | structlog | Structured JSON logging, production-grade |
| Server | Gunicorn + uvicorn workers | Multi-process untuk handle 200 concurrent users |
| Container | Docker + Docker Compose | Local dev environment (FastAPI + Redis) |

---

## 9. Arsitektur Sistem

### 9.1 High-Level Architecture

```
Client (Postman / CLI / GitHub)
        │
        ▼
Gunicorn (4 uvicorn workers)
        │
        ▼
FastAPI Application
  ├── Auth Middleware (verify Bearer token)
  ├── Rate Limit Middleware (Redis)
  ├── Structured Logging Middleware (correlation ID)
  └── Routers
        │
        ├── Service Layer (business logic + cache)
        │       │
        │       └── Repository Layer (Supabase client queries)
        │               │
        │    ┌──────────┴──────────┐
        │    ▼                     ▼
        │  Supabase PostgreSQL  Redis 7
        │  (auth.users +         (Docker,
        │   custom tables,      cache + rate limit)
        │   RLS enabled)
        │
        └── Webhook Handler
            └── Calls SECURITY DEFINER function for log insert
```

### 9.2 Perbedaan dengan Arsitektur Original

| Komponen | Original (v3.0.0) | Updated (v4.2.0) |
|---|---|---|
| User Identity | Tabel `user_profiles` sendiri | Gunakan `auth.users` Supabase |
| Auth Flow | Client-side Supabase SDK | DevLog API handle sign up/sign in via Admin API |
| Auth Endpoints | None (delegated) | Full auth: sign up, sign in, sign out |
| JWT Verification | Manual via `python-jose` + JWKS endpoint | Via Supabase client token verification |
| Webhook Insert | Service role key untuk bypass RLS | SECURITY DEFINER function |

### 9.3 Clean Architecture: Layering Pattern

Setiap modul mengikuti 4 layer yang strict. Tidak ada layer yang boleh skip atau memanggil layer di bawahnya langsung.

| Layer | Tanggung Jawab | Tidak Boleh |
|---|---|---|
| Router | HTTP in/out, request parsing, response serialization | Akses DB langsung, business logic |
| Service | Orchestration, business rules, cache logic | Akses DB langsung (harus lewat Repository) |
| Repository | Semua interaksi dengan database (Supabase client queries) | Business logic, HTTP concerns |
| Database | Supabase tables dengan RLS + SECURITY DEFINER functions | — |

Dependency injection dilakukan via FastAPI `Depends()` — setiap layer di-inject ke layer di atasnya secara eksplisit, sehingga mudah di-mock saat testing.

### 9.4 Struktur Direktori

```
devlog-api/
├── app/
│   ├── main.py                  # FastAPI app factory, lifespan
│   ├── config.py                # Environment variables (Pydantic Settings)
│   ├── dependencies.py          # Global DI: supabase client, redis, auth
│   ├── database/
│   │   ├── supabase.py         # Supabase client setup
│   │   └── models/             # Pydantic schemas
│   ├── modules/
│   │   ├── auth/                # sign up, sign in, sign out, /me
│   │   ├── projects/            # router, service, repository, schemas
│   │   ├── logs/                # router, service, repository, schemas
│   │   ├── analytics/           # router, service (aggregation + cache)
│   │   └── webhooks/            # router, HMAC handler, auto-log
│   ├── middlewares/             # logging, rate limiting
│   └── lib/                     # custom errors, cache helpers
├── supabase/
│   └── migrations/              # Supabase migration files (tables + functions)
├── tests/
│   ├── unit/                    # Test per service/repository layer
│   └── integration/             # Test via httpx async client
├── docker-compose.yml
├── Dockerfile
├── gunicorn.conf.py
└── requirements.txt
```

---

## 10. Database Design

### 10.1 Overview

Database menggunakan Supabase PostgreSQL. Authentication menggunakan tabel `auth.users` yang sudah built-in dari Supabase. Custom tables hanya untuk `projects`, `log_entries`, dan `github_mappings`.

Webhook insert menggunakan PostgreSQL function dengan SECURITY DEFINER — ini bypass RLS karena function berjalan dengan privileges dari function creator, bukan caller.

### 10.2 Tabel & Relasi

**auth.users (BUILT-IN - tidak perlu dibuat)**

Tabel default dari Supabase Auth. Menyimpan data user. Kolom utama yang akan digunakan:

| Kolom | Tipe | Keterangan |
|---|---|---|
| id | UUID | Primary key, digunakan sebagai user_id di tabel lain |
| email | VARCHAR | Email user |
| created_at | TIMESTAMPTZ | Waktu registrasi |

**projects**

Grouping untuk log entries. Mendukung soft delete.

| Kolom | Tipe | Keterangan |
|---|---|---|
| id | UUID | Primary key |
| user_id | UUID | Referensi ke auth.users.id |
| name | VARCHAR | Nama project |
| description | TEXT | Opsional |
| color | VARCHAR(7) | Hex color untuk UI |
| tech_stack | TEXT[] | Array teknologi (max 15) |
| is_active | BOOLEAN | Default true |
| created_at | TIMESTAMPTZ | Auto-generated |
| updated_at | TIMESTAMPTZ | Auto-updated |
| deleted_at | TIMESTAMPTZ | Soft delete |

**log_entries**

Tabel utama. Setiap baris merepresentasikan satu sesi aktivitas developer.

| Kolom | Tipe | Keterangan |
|---|---|---|
| id | UUID | Primary key |
| user_id | UUID | Referensi ke auth.users.id |
| project_id | UUID | FK ke projects, nullable |
| activity_type | VARCHAR(50) | Enum: coding, review, debugging, documentation, meeting, research, deployment |
| description | TEXT | Opsional |
| duration_minutes | INTEGER | Wajib > 0 |
| tags | TEXT[] | Untuk filtering |
| started_at | TIMESTAMPTZ | Boleh retroactive |
| created_at | TIMESTAMPTZ | Auto-generated |
| updated_at | TIMESTAMPTZ | Auto-updated |
| deleted_at | TIMESTAMPTZ | Soft delete |

**github_mappings**

Konfigurasi mapping antara GitHub repository dengan project di DevLog.

| Kolom | Tipe | Keterangan |
|---|---|---|
| id | UUID | Primary key |
| user_id | UUID | Referensi ke auth.users.id |
| project_id | UUID | FK ke projects |
| repo_full_name | VARCHAR(256) | Format: username/repo-name |
| webhook_secret | VARCHAR(256) | HMAC secret untuk verifikasi |
| created_at | TIMESTAMPTZ | Auto-generated |

### 10.3 Indexes

**projects**
| Index | Type | Purpose |
|---|---|---|
| `idx_projects_user_id` | B-tree | Find projects by user |
| `idx_projects_user_active` | Partial B-tree | Find active projects by user (WHERE deleted_at IS NULL) |

**log_entries**
| Index | Type | Purpose |
|---|---|---|
| `idx_log_entries_user_started` | Composite B-tree | List logs with pagination/sort by time |
| `idx_log_entries_project` | B-tree | Find logs by project |
| `idx_log_entries_activity` | B-tree | Filter/group by activity type |
| `idx_log_entries_tags` | GIN | Search by tags (array containment) |
| All above | Partial | WHERE deleted_at IS NULL |

**github_mappings**
| Index | Type | Purpose |
|---|---|---|
| `idx_github_mappings_user` | B-tree | Find mappings by user |
| `uq_github_mappings_user_repo` | Unique constraint | Satu repo per user |

### 10.4 Row Level Security (RLS) Policies

#### 10.4.1 RLS Overview

Semua tabel custom menggunakan RLS untuk keamanan. Setiap query dari aplikasi akan selalu menyertakan `user_id` dari token yang sudah diverifikasi Supabase, dan RLS policy akan mem-filter data sesuai dengan user tersebut.

#### 10.4.2 RLS Policies per Table

**projects**

| Operation | Policy Name | Using Clause | Description |
|---|---|---|---|
| SELECT | projects_select_own | `auth.uid() = user_id` | User hanya bisa read project milik sendiri |
| INSERT | projects_insert_own | `auth.uid() = user_id` | User hanya bisa insert project untuk dirinya sendiri |
| UPDATE | projects_update_own | `auth.uid() = user_id` | User hanya bisa update project miliknya |
| DELETE | projects_delete_own | `auth.uid() = user_id` | User hanya bisa delete project miliknya |

**log_entries**

| Operation | Policy Name | Using Clause | Description |
|---|---|---|---|
| SELECT | log_entries_select_own | `auth.uid() = user_id` | User hanya bisa read log miliknya |
| INSERT | log_entries_insert_own | `auth.uid() = user_id` | User hanya bisa insert log untuk dirinya sendiri |
| UPDATE | log_entries_update_own | `auth.uid() = user_id` | User hanya bisa update log miliknya |
| DELETE | log_entries_delete_own | `auth.uid() = user_id` | User hanya bisa delete log miliknya |

**github_mappings**

| Operation | Policy Name | Using Clause | Description |
|---|---|---|---|
| SELECT | github_mappings_select_own | `auth.uid() = user_id` | User hanya bisa read mapping miliknya |
| INSERT | github_mappings_insert_own | `auth.uid() = user_id` | User hanya bisa insert mapping untuk dirinya sendiri |
| UPDATE | github_mappings_update_own | `auth.uid() = user_id` | User hanya bisa update mapping miliknya |
| DELETE | github_mappings_delete_own | `auth.uid() = user_id` | User hanya bisa delete mapping miliknya |

### 10.5 Webhook: SECURITY DEFINER Function

#### 10.5.1 Problem

GitHub webhook tidak memiliki Supabase access token (hanya HMAC signature untuk verify GitHub identity). Karena itu, webhook tidak bisa menggunakan RLS context untuk insert log entries.

#### 10.5.2 Solution: SECURITY DEFINER Function

PostgreSQL function dengan `SECURITY DEFINER` berjalan dengan privileges dari function creator, bukan caller. Ini memungkinkan webhook untuk insert log entries tanpa user context.

#### 10.5.3 Function Design

```sql
CREATE OR REPLACE FUNCTION insert_webhook_log(
    p_repo_full_name VARCHAR,
    p_commit_count INTEGER,
    p_started_at TIMESTAMPTZ
) RETURNS UUID
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
-- Lookup github_mapping untuk verify repo belongs to user
-- Calculate duration: commit_count * 5 minutes, max 60 minutes
-- Insert log entry with user_id from mapping
-- Return log entry id
$$;
```

#### 10.5.4 Security Considerations

1. **SECURITY DEFINER** — Function executes with creator's privileges. Need to ensure creator is a trusted role.

2. **SET search_path = public** — Prevent function from using unexpected schemas.

3. **Input validation** — Function must validate that:
   - `p_repo_full_name` exists in github_mappings
   - `p_commit_count` is reasonable (1-100 range)

4. **No direct table access** — Function must use the same RLS-protected tables, but the definer role bypasses RLS only for this function.

#### 10.5.5 Anonymous Access for Webhook

Supabase anon key can be used to call the function. The function itself handles authorization by validating the mapping exists and belongs to the user.

---

## 11. Scalability Design (200 Concurrent Users)

### 11.1 Analisis Bottleneck

| Komponen | Bottleneck | Solusi |
|---|---|---|
| FastAPI single process | Default single-threaded tidak cukup untuk 200 concurrent | Gunicorn + 4 uvicorn workers |
| Supabase connection limit | Free tier ~60 connections, bisa habis | Gunakan PgBouncer Transaction Mode (port 6543) |
| Analytics query tanpa cache | Aggregasi berat dijalankan tiap request | Redis cache TTL 1 jam + invalidasi otomatis |
| Redis single instance | Untuk 200 user sudah lebih dari cukup | Tidak perlu Redis Cluster di skala ini |

### 11.2 Konfigurasi Scalability

**Gunicorn (Process Manager)**
- Jumlah worker mengikuti formula: (2 x jumlah CPU core) + 1
- Worker class menggunakan uvicorn untuk async support
- Max requests per worker dikonfigurasi untuk mencegah memory leak

**Supabase Connection**
- Koneksi via Supabase client menggunakan connection pool default
- Untuk local development: port 5432 langsung
- Untuk production: port 6543 via PgBouncer Transaction Mode

### 11.3 Redis Caching Strategy

| Cache Key Pattern | TTL | Invalidasi |
|---|---|---|
| analytics:daily:{user_id}:{date} | 1 jam | Saat ada log entry baru/update |
| analytics:weekly:{user_id}:{week} | 1 jam | Saat ada log entry baru/update |
| analytics:project:{project_id}:{from}:{to} | 30 menit | Saat ada log baru untuk project itu |
| ratelimit:{user_id}:{window} | 60 detik sliding | Auto-expire |

---

## 12. API Design

### 12.1 Conventions

- **Base URL:** `http://localhost:8000/api/v1`
- **Auth Header:** `Authorization: Bearer <supabase_access_token>`
- **Content-Type:** `application/json`
- **Versioning:** URL-based (/v1/) untuk major breaking changes
- **Docs:** `http://localhost:8000/docs` (Swagger UI auto-generated)

### 12.2 Standard Response Format

Semua response mengikuti envelope format yang konsisten:
- Success: objek dengan field `success: true` dan `data`
- Paginated list: tambah field `meta` berisi `cursor`, `has_more`, dan `count`
- Error: objek dengan `success: false` dan `error` berisi `code`, `message`, dan `details` opsional

### 12.3 Daftar Endpoint

| Method | Endpoint | Auth | Deskripsi |
|---|---|---|---|
| POST | /api/v1/auth/signup | Public | Register new user |
| POST | /api/v1/auth/signin | Public | Login user |
| POST | /api/v1/auth/signout | Required | Logout user |
| GET | /api/v1/health | Public | Health check: status API |
| GET | /api/v1/me | Required | Get current user info (from auth.users) |
| PATCH | /api/v1/me | Required | Update user metadata (stored in auth.users) |
| GET | /api/v1/projects | Required | List project user |
| POST | /api/v1/projects | Required | Buat project baru |
| GET | /api/v1/projects/{id} | Required | Detail project |
| PATCH | /api/v1/projects/{id} | Required | Update project |
| DELETE | /api/v1/projects/{id} | Required | Soft delete project |
| GET | /api/v1/logs | Required | List log entries (filter + cursor pagination) |
| POST | /api/v1/logs | Required | Buat log entry |
| GET | /api/v1/logs/{id} | Required | Detail log entry |
| PATCH | /api/v1/logs/{id} | Required | Update log entry |
| DELETE | /api/v1/logs/{id} | Required | Soft delete log entry |
| GET | /api/v1/analytics/daily | Required | Daily summary (cached) |
| GET | /api/v1/analytics/weekly | Required | Weekly report + heatmap |
| GET | /api/v1/analytics/projects/{id}/stats | Required | Project statistics |
| GET | /api/v1/github-mappings | Required | List repo mappings |
| POST | /api/v1/github-mappings | Required | Buat repo mapping |
| DELETE | /api/v1/github-mappings/{id} | Required | Hapus repo mapping |
| POST | /api/v1/webhooks/github | HMAC only | GitHub push event receiver |

### 12.4 Naming Conventions

| Aspek | Konvensi | Contoh |
|---|---|---|
| URL Paths | kebab-case, plural | /log-entries, /github-mappings |
| JSON Keys | snake_case | started_at, user_id, activity_type |
| Enum Values | lowercase snake_case | coding, code_review |
| Timestamps | ISO 8601 UTC | 2026-04-19T10:30:00Z |
| IDs | UUID v4 | 550e8400-e29b-41d4-... |
| Duration | Integer dalam menit | duration_minutes: 90 |

### 12.5 Error Code Taxonomy

| Error Code | HTTP Status | Kapan Digunakan |
|---|---|---|
| VALIDATION_ERROR | 400 | Input tidak valid |
| UNAUTHORIZED | 401 | Token tidak ada, invalid, atau expired |
| FORBIDDEN | 403 | User tidak punya akses ke resource ini |
| NOT_FOUND | 404 | Resource tidak ditemukan atau sudah dihapus |
| CONFLICT | 409 | Duplikat data |
| RATE_LIMITED | 429 | Melebihi rate limit |
| INTERNAL_ERROR | 500 | Error tidak terduga |

### 12.6 Cursor-Based Pagination

Semua list endpoint menggunakan cursor-based pagination, bukan offset. Cursor diencode dari kombinasi (started_at, id) sehingga konsisten meskipun ada insert baru. Lebih efisien dari offset karena tidak memerlukan COUNT(*) di setiap request.

---

## 13. Business Process & User Flows

### 13.1 Alur Autentikasi (Backend-Handled)

**Sign Up:**
1. Client kirim POST /api/v1/auth/signup dengan email + password
2. DevLog API call `supabase.auth.admin.create_user()` via Supabase Admin API
3. User created in `auth.users`, session established
4. Return access token + refresh token to client

**Sign In:**
1. Client kirim POST /api/v1/auth/signin dengan email + password
2. DevLog API call `supabase.auth.sign_in_with_password()` via Supabase client
3. Credentials verified, session created
4. Return access token + refresh token to client

**Sign Out:**
1. Client kirim POST /api/v1/auth/signout dengan Bearer token
2. DevLog API call `supabase.auth.sign_out()` via Supabase client
3. Session invalidated
4. Return success to client

**Token Verification:**
1. Client kirim request dengan Bearer token
2. DevLog API call `supabase.auth.get_user()` via Supabase client
3. Token verified, user info returned
4. User ID extracted and used for RLS policies

### 13.2 Alur Mencatat Aktivitas Harian

1. Developer selesai sesi coding
2. Kirim log entry via POST /api/v1/logs
3. Service validasi input, simpan ke database via Supabase client (RLS automatically filters)
4. Cache analytics user diinvalidasi otomatis
5. Developer request GET /analytics/daily — data fresh tersedia

### 13.3 Alur GitHub Webhook (Auto-Logging)

```
GitHub Push Event
        │
        ▼
Verify HMAC-SHA256 Signature (FastAPI)
        │
        ▼ (if valid)
Extract repo_full_name from payload
        │
        ▼
Call Supabase function: insert_webhook_log()
        │
        ├── Function verifies mapping exists (user_id + repo_full_name)
        ├── Calculate duration: commit_count * 5 min, max 60 min
        ├── Insert log_entries with user_id from mapping
        └── Return log entry ID or error
```

**Proses detail:**

1. Developer konfigurasi mapping repo ke project via POST /api/v1/github-mappings
2. Developer set webhook di GitHub Settings (URL + secret yang sama)
3. Setiap push commit, GitHub kirim payload ke POST /api/v1/webhooks/github
4. FastAPI verifikasi HMAC-SHA256 signature — jika invalid, request ditolak (401)
5. FastAPI extract `repo_full_name` dari payload, hitung commit count
6. FastAPI call Supabase RPC function `insert_webhook_log(repo_full_name, commit_count, started_at)`
7. Function内部:
   - Lookup `github_mappings` WHERE `repo_full_name` = payload.repo
   - Jika tidak ada mapping → return 200 OK (no-op, agar GitHub tidak retry)
   - Hitung duration = min(commit_count * 5, 60) minutes
   - Insert log_entries dengan user_id dari mapping (SECURITY DEFINER bypasses RLS)
   - Return log entry ID
8. FastAPI return 200 OK ke GitHub

---

## 14. Sprint Plan (7 Hari)

| Hari | Focus Area | Deliverable & Key Learning |
|---|---|---|
| Hari 1 | Setup & Foundation | Project structure, Docker Compose, Supabase client setup, env config, structured logging, health check endpoint. LEARNING: Supabase client integration. |
| Hari 2 | Auth Module | Sign up, sign in, sign out endpoints via Supabase Admin API. LEARNING: Auth flow handling di backend. |
| Hari 3 | Projects & Logs Module | Full CRUD dengan Repository Pattern dan Service Layer, Pydantic schemas, cursor-based pagination. LEARNING: Clean architecture layering yang strict. |
| Hari 4 | Analytics Module + Caching | Aggregasi query via Supabase, Redis caching layer, cache invalidation, rate limiting middleware. LEARNING: Caching strategy dan async Redis. |
| Hari 5 | GitHub Webhook + SECURITY DEFINER | HMAC verification, SECURITY DEFINER function, auto-log creation, github_mappings CRUD, Gunicorn config. LEARNING: PostgreSQL function + security pattern. |
| Hari 6 | Testing | Unit test per service layer (mock repository), integration test per endpoint via httpx, coverage report. Target >= 70%. LEARNING: Testing strategy untuk layered architecture. |
| Hari 7 | Polish, Docs & Smoke Test | Swagger audit, README (setup + env + contoh curl), error handling audit, smoke test 200 concurrent dengan Locust. |

### Definition of Done

Sprint dianggap selesai jika:

- Semua 22 endpoint berjalan tanpa error (3 auth + 19 CRUD/stats)
- Docker Compose up dengan satu perintah
- Gunicorn berjalan dengan minimal 4 uvicorn workers
- Sign up/sign in/sign out berfungsi dengan Supabase Admin API
- RLS policies aktif dan berfungsi untuk semua tabel
- SECURITY DEFINER function bekerja untuk webhook
- Test coverage >= 70%
- Swagger UI accessible di /docs dengan semua endpoint terdokumentasi
- Redis caching bekerja: analytics < 50ms pada cache hit
- Rate limiting bekerja: return 429 setelah limit terlampaui
- README lengkap: setup guide + env vars + contoh curl

---

## 15. Risks & Mitigasi

| Risiko | Probabilitas | Dampak | Mitigasi |
|---|---|---|---|
| Supabase client async behavior yang berbeda dari ekspektasi | Rendah | Sedang | Baca dokumentasi postgrest-py, gunakan async methods |
| RLS policy mistake menyebabkan data leak | Rendah | Tinggi | Test setiap policy dengan user berbeda |
| SECURITY DEFINER function vulnerability | Sedang | Tinggi | Buat input validation yang ketat, SET search_path, test dengan berbagai edge cases |
| Connection pool Supabase tidak cukup | Rendah | Tinggi | Monitoring via dashboard, upgrade plan jika perlu |
| Auth flow edge cases (email already exists, wrong password) | Sedang | Sedang | Handle error response dengan proper error codes |
| Scope creep | Tinggi | Tinggi | Dokumen ini adalah kontrak. Fitur tambahan masuk backlog. |

---

## 16. Open Questions & Decisions

| Pertanyaan | Status | Keputusan |
|---|---|---|
| User profile extra data (timezone, dll) disimpan dimana? | RESOLVED | Simpan di `auth.users.metadata` JSON field |
| Rate limit: per endpoint atau global per user? | RESOLVED | Global per user: 100 req/mnt. Analytics: 20 req/mnt. |
| Auth: client-side SDK atau backend-handled? | RESOLVED | Backend handle sign up/sign in/sign out via Supabase Admin API |
| Webhook insert: service role vs SECURITY DEFINER? | RESOLVED | SECURITY DEFINER function (lebih aman, tidak perlu service role key) |
| Target concurrent users? | RESOLVED | 200 concurrent via Gunicorn multi-worker + Supabase connection pool |
| Export data (CSV/JSON)? | BACKLOG | Out of scope sprint ini. |
| Load testing tool? | RESOLVED | Locust (Python-native) untuk smoke test di Hari 7. |

---

## 17. Referensi

- FastAPI Documentation — https://fastapi.tiangolo.com
- Supabase Python Client — https://supabase.com/docs/reference/python/introduction
- Supabase Admin API — https://supabase.com/docs/reference/javascript/admin
- Supabase RLS Documentation — https://supabase.com/docs/guides/database/postgres/row-level-security
- PostgreSQL SECURITY DEFINER — https://www.postgresql.org/docs/current/sql-createfunction.html
- structlog Documentation — https://www.structlog.org
- Locust Load Testing — https://locust.io
- Cursor Pagination Pattern — https://use-the-index-luke.com/no-offset

---

*End of Document — DevLog API PRD v4.2.0 — April 2026*