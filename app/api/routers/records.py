from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.db.models.user import User
from app.schemas.record import DashboardResponse, RecentHistoryResponse
from app.services.record_service import RecordService

router = APIRouter(prefix="/api/records", tags=["records"])


@router.get("/dashboard", response_model=DashboardResponse)
def get_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DashboardResponse:
    return RecordService(db).get_dashboard(current_user.id)


@router.get("/history", response_model=RecentHistoryResponse)
def get_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> RecentHistoryResponse:
    return RecordService(db).get_history(current_user.id)


@router.get("/monthly", response_model=DashboardResponse)
def get_monthly_dashboard(
    year: int = Query(..., ge=2024),
    month: int = Query(..., ge=1, le=12),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DashboardResponse:
    return RecordService(db).get_dashboard(current_user.id, year=year, month=month)
