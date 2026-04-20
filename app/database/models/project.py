from datetime import datetime

from pydantic import BaseModel


class ProjectCreate(BaseModel):
    name: str
    description: str | None = None
    color: str | None = None
    tech_stack: list[str] | None = None


class ProjectUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    color: str | None = None
    tech_stack: list[str] | None = None
    is_active: bool | None = None


class ProjectResponse(BaseModel):
    id: str
    user_id: str
    name: str
    description: str | None
    color: str | None
    tech_stack: list[str] | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProjectListResponse(BaseModel):
    data: list[ProjectResponse]
    meta: dict[str, str | bool | int]