from datetime import datetime

from pydantic import BaseModel


class GitHubMappingCreate(BaseModel):
    project_id: str
    repo_full_name: str
    webhook_secret: str


class GitHubMappingResponse(BaseModel):
    id: str
    user_id: str
    project_id: str
    repo_full_name: str
    created_at: datetime

    model_config = {"from_attributes": True}


class GitHubMappingListResponse(BaseModel):
    data: list[GitHubMappingResponse]
    meta: dict[str, str | bool | int]