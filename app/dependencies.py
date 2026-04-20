from typing import Annotated

from fastapi import Depends, Header
from supabase import create_client, SupabaseClient

from app.config import settings


def get_supabase_service_client() -> SupabaseClient:
    return create_client(
        supabase_url=settings.SUPABASE_URL,
        supabase_key=settings.SUPABASE_KEY,
    )


async def get_current_user_token(authorization: str = Header(None)) -> str | None:
    if authorization and authorization.startswith("Bearer "):
        return authorization[7:]
    return None


SupabaseServiceClient = Annotated[SupabaseClient, Depends(get_supabase_service_client)]
CurrentUserToken = Annotated[str | None, Depends(get_current_user_token)]