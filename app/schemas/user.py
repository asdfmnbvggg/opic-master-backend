from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class UserProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    name: str
    phone: str
    email: str | None
    birth_date: date | None
    created_at: datetime
