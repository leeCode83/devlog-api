-- =====================================================
-- DevLog API: Create All Tables Migration
-- Version: 20260420
-- =====================================================

-- =====================================================
-- 1. PROJECTS TABLE
-- =====================================================
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    color VARCHAR(7),
    tech_stack TEXT[] CHECK (array_length(tech_stack, 1) <= 15),
    is_active BOOLEAN NOT NULL DEFAULT true,
    deleted_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Index: find projects by user
CREATE INDEX idx_projects_user_id ON projects(user_id);

-- Index: find active projects by user (partial)
CREATE INDEX idx_projects_user_active ON projects(user_id) WHERE deleted_at IS NULL;

-- =====================================================
-- 2. LOG_ENTRIES TABLE
-- =====================================================
CREATE TABLE log_entries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    project_id UUID REFERENCES projects(id) ON DELETE SET NULL,
    activity_type VARCHAR(50) NOT NULL CHECK (activity_type IN (
        'coding',
        'review',
        'debugging',
        'documentation',
        'meeting',
        'research',
        'deployment'
    )),
    description TEXT,
    duration_minutes INTEGER NOT NULL CHECK (duration_minutes > 0),
    tags TEXT[],
    started_at TIMESTAMPTZ NOT NULL,
    deleted_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Index: list logs by user with sort by time (for pagination)
CREATE INDEX idx_log_entries_user_started ON log_entries(user_id, started_at DESC);

-- Index: find logs by project
CREATE INDEX idx_log_entries_project ON log_entries(project_id);

-- Index: filter/group by activity type
CREATE INDEX idx_log_entries_activity ON log_entries(activity_type);

-- Index: search by tags (GIN for array containment queries)
CREATE INDEX idx_log_entries_tags ON log_entries USING GIN (tags);

-- Partial indexes for all log queries (exclude soft-deleted)
CREATE INDEX idx_log_entries_user_started_active ON log_entries(user_id, started_at DESC) WHERE deleted_at IS NULL;
CREATE INDEX idx_log_entries_project_active ON log_entries(project_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_log_entries_activity_active ON log_entries(activity_type) WHERE deleted_at IS NULL;
CREATE INDEX idx_log_entries_tags_active ON log_entries USING GIN (tags) WHERE deleted_at IS NULL;

-- =====================================================
-- 3. GITHUB_MAPPINGS TABLE
-- =====================================================
CREATE TABLE github_mappings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    repo_full_name VARCHAR(256) NOT NULL,
    webhook_secret VARCHAR(256) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    -- Constraint: satu repo per user (tidak bisa map repo yang sama ke dua project)
    CONSTRAINT uq_github_mappings_user_repo UNIQUE (user_id, repo_full_name)
);

-- Index: find mappings by user
CREATE INDEX idx_github_mappings_user ON github_mappings(user_id);

-- =====================================================
-- 4. ENABLE ROW LEVEL SECURITY (RLS)
-- =====================================================
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE log_entries ENABLE ROW LEVEL SECURITY;
ALTER TABLE github_mappings ENABLE ROW LEVEL SECURITY;

-- =====================================================
-- 5. RLS POLICIES
-- =====================================================

-- Projects: user hanya bisa akses miliknya
CREATE POLICY "projects_select_own" ON projects
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "projects_insert_own" ON projects
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "projects_update_own" ON projects
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "projects_delete_own" ON projects
    FOR DELETE USING (auth.uid() = user_id);

-- Log Entries: user hanya bisa akses miliknya
CREATE POLICY "log_entries_select_own" ON log_entries
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "log_entries_insert_own" ON log_entries
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "log_entries_update_own" ON log_entries
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "log_entries_delete_own" ON log_entries
    FOR DELETE USING (auth.uid() = user_id);

-- GitHub Mappings: user hanya bisa akses miliknya
CREATE POLICY "github_mappings_select_own" ON github_mappings
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "github_mappings_insert_own" ON github_mappings
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "github_mappings_update_own" ON github_mappings
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "github_mappings_delete_own" ON github_mappings
    FOR DELETE USING (auth.uid() = user_id); 