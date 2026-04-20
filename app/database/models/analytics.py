from datetime import date

from pydantic import BaseModel


class DailySummary(BaseModel):
    date: date
    total_minutes: int
    total_entries: int
    by_activity_type: dict[str, int]
    peak_hour: int
    top_project: str | None


class WeeklyReport(BaseModel):
    week: str
    total_minutes: int
    total_entries: int
    by_day: dict[str, int]
    streak_count: int
    heatmap: list[list[int]]


class ProjectStats(BaseModel):
    project_id: str
    total_minutes: int
    by_activity_type: dict[str, int]
    velocity_trend: list[dict[str, int]]