from datetime import datetime
from typing import Any

from pydantic import BaseModel


class UserResponse(BaseModel):
    id: str
    email: str
    created_at: datetime

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    metadata: dict[str, Any] | None = None