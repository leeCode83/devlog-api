from pydantic import BaseModel


class SuccessResponse(BaseModel):
    success: bool = True
    data: dict | list | None = None


class ErrorDetail(BaseModel):
    code: str
    message: str
    details: dict | list | None = None


class ErrorResponse(BaseModel):
    success: bool = False
    error: ErrorDetail


class PaginatedMeta(BaseModel):
    cursor: str | None
    has_more: bool
    count: int