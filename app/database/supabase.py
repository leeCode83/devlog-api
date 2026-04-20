from supabase import create_client, SupabaseClient

from app.config import settings


def get_supabase_client() -> SupabaseClient:
    return create_client(
        supabase_url=settings.SUPABASE_URL,
        supabase_key=settings.SUPABASE_KEY,
    )


def get_supabase_anon_client() -> SupabaseClient:
    return create_client(
        supabase_url=settings.SUPABASE_URL,
        supabase_key=settings.SUPABASE_ANON_KEY,
    )