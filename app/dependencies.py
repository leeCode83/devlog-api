from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPBearer
from supabase import Client

from app.database.supabase import get_client

Client = Annotated[Client, Depends(get_client)]

security = HTTPBearer(auto_error=False)


async def get_current_user_token(authorization: str = Depends(security)) -> str | None:
    if authorization:
        return authorization.credentials
    return None


CurrentUserToken = Annotated[str | None, Depends(get_current_user_token)]