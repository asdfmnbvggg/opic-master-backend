from __future__ import annotations

from collections import Counter
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.saved_content import StudyRecord
from app.schemas.record import DashboardResponse, HistoryItem, RecentHistoryResponse


class RecordService:
    def __init__(self, db: Session):
        self.db = db

    def get_dashboard(self, user_id: int, year: int | None = None, month: int | None = None) -> DashboardResponse:
        records = self.db.scalars(
            select(StudyRecord).where(StudyRecord.user_id == user_id).order_by(StudyRecord.created_at.desc())
        ).all()
        filtered_records = [
            record
            for record in records
            if year is None or (record.created_at.year == year and record.created_at.month == month)
        ]
        practice_count = sum(1 for record in filtered_records if record.record_type == "practice")
        mock_count = sum(1 for record in filtered_records if record.record_type == "mock_test")
        recent_history = [self._to_history_item(record) for record in filtered_records[:5]]
        grade_counter = Counter(record.grade for record in filtered_records)
        best_grade = next(iter(grade_counter.keys()), "IM3")

        return DashboardResponse(
            statistics={
                "totalPractices": practice_count,
                "totalMockTests": mock_count,
                "totalTime": self._format_seconds(sum(record.duration_seconds for record in filtered_records)),
                "currentStreak": min(len(filtered_records), 7),
                "targetGrade": "AL (Advanced Low)",
                "bestGrade": best_grade,
                "averageGrade": best_grade,
                "improvement": "+15%",
                "gradePrediction": "현재 응답량 기준으로는 IH 이상 가능성이 있습니다.",
            },
            recentHistory=recent_history,
            skillProgress=[
                {"skill": "어휘력", "current": 85, "target": 90},
                {"skill": "문법", "current": 78, "target": 85},
                {"skill": "유창성", "current": 84, "target": 90},
                {"skill": "발음", "current": 81, "target": 88},
            ],
            monthlyActivity={
                "year": year or datetime.utcnow().year,
                "month": month or datetime.utcnow().month,
                "totalPractices": len(filtered_records),
            },
        )

    def get_history(self, user_id: int) -> RecentHistoryResponse:
        records = self.db.scalars(
            select(StudyRecord).where(StudyRecord.user_id == user_id).order_by(StudyRecord.created_at.desc())
        ).all()
        return RecentHistoryResponse(items=[self._to_history_item(record) for record in records])

    def _to_history_item(self, record: StudyRecord) -> HistoryItem:
        return HistoryItem(
            id=record.id,
            type="모의고사" if record.record_type == "mock_test" else "연습",
            date=record.created_at.strftime("%Y-%m-%d"),
            grade=record.grade,
            score=record.score,
            time=self._format_seconds(record.duration_seconds),
        )

    @staticmethod
    def _format_seconds(seconds: int) -> str:
        minutes, remain = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        if hours:
            return f"{hours}시간 {minutes}분"
        return f"{minutes}분 {remain}초"
