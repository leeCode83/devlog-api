from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class ActivityType(str, Enum):
    CODING = "coding"
    REVIEW = "review"
    DEBUGGING = "debugging"
    DOCUMENTATION = "documentation"
    MEETING = "meeting"
    RESEARCH = "research"
    DEPLOYMENT = "deployment"


class LogEntryCreate(BaseModel):
    project_id: str | None = None
    activity_type: ActivityType
    description: str | None = None
    duration_minutes: int
    tags: list[str] | None = None
    started_at: datetime


class LogEntryUpdate(BaseModel):
    project_id: str | None = None
    activity_type: ActivityType | None = None
    description: str | None = None
    duration_minutes: int | None = None
    tags: list[str] | None = None
    started_at: datetime | None = None


class LogEntryResponse(BaseModel):
    id: str
    user_id: str
    project_id: str | None
    activity_type: ActivityType
    description: str | None
    duration_minutes: int
    tags: list[str] | None
    started_at: datetime
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class LogEntryListResponse(BaseModel):
    data: list[LogEntryResponse]
    meta: dict[str, str | bool | int]


class LogEntryFilter(BaseModel):
    project_id: str | None = None
    activity_type: ActivityType | None = None
    tags: list[str] | None = None
    from_date: datetime | None = None
    to_date: datetime | None = None