from __future__ import annotations

from pydantic import BaseModel


class HistoryItem(BaseModel):
    id: int
    type: str
    date: str
    grade: str
    score: int
    time: str


class DashboardResponse(BaseModel):
    statistics: dict[str, object]
    recentHistory: list[HistoryItem]
    skillProgress: list[dict[str, object]]
    monthlyActivity: dict[str, object]


class RecentHistoryResponse(BaseModel):
    items: list[HistoryItem]
