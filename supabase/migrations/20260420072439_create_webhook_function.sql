-- =====================================================
-- DevLog API: Webhook SECURITY DEFINER Function
-- Version: 20260420
-- Purpose: Insert log entries from GitHub webhook without user token
-- =====================================================

CREATE OR REPLACE FUNCTION insert_webhook_log(
    p_repo_full_name VARCHAR(256),
    p_commit_count INTEGER,
    p_started_at TIMESTAMPTZ
) RETURNS UUID
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
    mapping_record RECORD;
    log_id UUID;
    v_duration_minutes INTEGER;
BEGIN
    -- 1. Validate inputs
    IF p_commit_count < 1 OR p_commit_count > 100 THEN
        RETURN NULL;
    END IF;

    IF p_repo_full_name IS NULL OR p_started_at IS NULL THEN
        RETURN NULL;
    END IF;

    -- 2. Lookup github_mappings to verify repo is mapped
    SELECT id, user_id, project_id
    INTO mapping_record
    FROM github_mappings
    WHERE repo_full_name = insert_webhook_log.p_repo_full_name;

    -- If no mapping found, return NULL (webhook does no-op)
    IF NOT FOUND THEN
        RETURN NULL;
    END IF;

    -- 3. Calculate duration
    -- 5 minutes per commit, max 60 minutes
    v_duration_minutes := LEAST(p_commit_count * 5, 60);

    -- 4. Insert log entry with user_id from mapping
    INSERT INTO log_entries (
        id,
        user_id,
        project_id,
        activity_type,
        description,
        duration_minutes,
        tags,
        started_at,
        created_at,
        updated_at
    ) VALUES (
        gen_random_uuid(),
        mapping_record.user_id,
        mapping_record.project_id,
        'coding',
        'Auto-logged from GitHub webhook push event',
        v_duration_minutes,
        ARRAY['github', 'webhook', 'auto'],
        p_started_at,
        now(),
        now()
    ) RETURNING id INTO log_id;

    -- 5. Return the inserted log entry ID
    RETURN log_id;

END;
$$;